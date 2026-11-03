from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta

from accounts.models import User, Company, CandidateProfile, EmployerProfile
from jobs.models import Job, Application
from notifications.models import Notification


class CareerConnectPlatformTests(TestCase):
    def setUp(self):
        self.client = Client()

        # Admin user
        self.admin = User.objects.create_superuser(
            username='test_admin',
            email='admin@test.com',
            password='password123',
            role='ADMIN'
        )

        # Company
        self.company = Company.objects.create(
            name='Test Tech Labs',
            website='https://testtech.com',
            industry='Software',
            company_size='51-200',
            headquarters='Bengaluru'
        )

        # Employer user
        self.employer = User.objects.create_user(
            username='test_employer',
            email='employer@test.com',
            password='password123',
            role='EMPLOYER'
        )
        self.emp_profile = EmployerProfile.objects.create(
            user=self.employer,
            company=self.company,
            designation='Lead Recruiter'
        )

        # Candidate user
        self.candidate = User.objects.create_user(
            username='test_candidate',
            email='candidate@test.com',
            password='password123',
            role='CANDIDATE'
        )
        self.cand_profile = CandidateProfile.objects.create(
            user=self.candidate,
            headline='Junior Python Developer',
            skills='Python, Django, SQLite, REST',
            education_degree='B.Tech CSE',
            experience_years=1.0
        )

        # Job
        self.job = Job.objects.create(
            employer=self.employer,
            company=self.company,
            title='Backend Python Developer',
            description='We need a passionate Python developer.',
            required_skills='Python, Django, SQL',
            location='Bengaluru',
            is_remote=True,
            employment_type='FULL_TIME',
            experience_level='ENTRY',
            min_salary=600000,
            max_salary=1000000,
            vacancies=2,
            deadline=timezone.now().date() + timedelta(days=30),
            status='ACTIVE',
            is_approved=True
        )

    def test_homepage_and_job_list(self):
        """Test home page and job catalog render properly with HTTP 200."""
        response = self.client.get(reverse('jobs:home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'CareerConnect')

        response = self.client.get(reverse('jobs:job_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Backend Python Developer')

    def test_job_search_filters(self):
        """Test search filtering by keyword and skill."""
        response = self.client.get(reverse('jobs:job_list'), {'q': 'Backend'})
        self.assertEqual(len(response.context['jobs']), 1)

        response = self.client.get(reverse('jobs:job_list'), {'q': 'NonExistentTitle'})
        self.assertEqual(len(response.context['jobs']), 0)

        response = self.client.get(reverse('jobs:job_list'), {'skill': 'Python'})
        self.assertEqual(len(response.context['jobs']), 1)

    def test_candidate_apply_and_duplicate_prevention(self):
        """Test candidate can apply for a job and duplicate applications are prevented."""
        self.client.login(username='test_candidate', password='password123')

        # First application
        response = self.client.post(reverse('jobs:apply_job', kwargs={'pk': self.job.pk}), {
            'cover_letter': 'I am highly interested in this Django position.'
        }, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Application.objects.filter(job=self.job, candidate=self.candidate).count(), 1)

        # Check notification sent to employer
        employer_notif = Notification.objects.filter(recipient=self.employer, notification_type='NEW_APPLICATION').first()
        self.assertIsNotNone(employer_notif)

        # Attempt duplicate application
        dup_response = self.client.post(reverse('jobs:apply_job', kwargs={'pk': self.job.pk}), {
            'cover_letter': 'Trying again...'
        }, follow=True)

        # Still only 1 application should exist
        self.assertEqual(Application.objects.filter(job=self.job, candidate=self.candidate).count(), 1)
        self.assertContains(dup_response, "already applied")

    def test_employer_update_application_status(self):
        """Test employer can update applicant status and triggers notification."""
        app = Application.objects.create(
            job=self.job,
            candidate=self.candidate,
            status='PENDING'
        )

        self.client.login(username='test_employer', password='password123')
        response = self.client.post(reverse('jobs:update_application_status', kwargs={'pk': app.pk}), {
            'status': 'SHORTLISTED',
            'notes': 'Scheduled interview for Monday.'
        }, follow=True)

        self.assertEqual(response.status_code, 200)
        app.refresh_from_db()
        self.assertEqual(app.status, 'SHORTLISTED')
        self.assertEqual(app.employer_notes, 'Scheduled interview for Monday.')

        # Verify candidate received notification
        cand_notif = Notification.objects.filter(recipient=self.candidate, notification_type='STATUS_CHANGE').first()
        self.assertIsNotNone(cand_notif)
        self.assertIn('Shortlisted', cand_notif.message)

    def test_candidate_withdraw_application(self):
        """Test candidate can withdraw their application."""
        app = Application.objects.create(
            job=self.job,
            candidate=self.candidate,
            status='PENDING'
        )

        self.client.login(username='test_candidate', password='password123')
        response = self.client.get(reverse('jobs:withdraw_application', kwargs={'pk': app.pk}), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Application.objects.filter(pk=app.pk).exists())

    def test_rest_api_endpoints(self):
        """Test Django REST Framework endpoints."""
        # 1. Jobs API
        response = self.client.get('/api/v1/jobs/')
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(response.data['count'], 1)

        # 2. Stats API (authenticated)
        self.client.login(username='test_admin', password='password123')
        stats_response = self.client.get('/api/v1/stats/')
        self.assertEqual(stats_response.status_code, 200)
        self.assertEqual(stats_response.data['role'], 'ADMIN')
        self.assertIn('total_jobs', stats_response.data)
