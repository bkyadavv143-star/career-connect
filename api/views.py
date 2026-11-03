from rest_framework import viewsets, permissions, status, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Q, Count
from django.shortcuts import get_object_or_404

from accounts.models import User, Company, CandidateProfile, EmployerProfile
from jobs.models import Job, Application
from notifications.models import Notification
from .serializers import (
    UserSerializer, CompanySerializer, CandidateProfileSerializer,
    EmployerProfileSerializer, JobSerializer, ApplicationSerializer,
    NotificationSerializer
)


class IsEmployerOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and (request.user.is_employer or request.user.is_platform_admin)

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_platform_admin or (hasattr(obj, 'employer') and obj.employer == request.user)


class JobViewSet(viewsets.ModelViewSet):
    serializer_class = JobSerializer
    permission_classes = [IsEmployerOrReadOnly]

    def get_queryset(self):
        queryset = Job.objects.select_related('company', 'employer').all()

        # Public users only see ACTIVE and approved jobs
        if not (self.request.user.is_authenticated and self.request.user.is_platform_admin):
            if self.action in ['list', 'retrieve']:
                queryset = queryset.filter(status='ACTIVE', is_approved=True)

        # Filters
        q = self.request.query_params.get('q')
        if q:
            queryset = queryset.filter(
                Q(title__icontains=q) |
                Q(description__icontains=q) |
                Q(company__name__icontains=q) |
                Q(required_skills__icontains=q)
            )

        location = self.request.query_params.get('location')
        if location:
            queryset = queryset.filter(location__icontains=location)

        skills = self.request.query_params.get('skills')
        if skills:
            queryset = queryset.filter(required_skills__icontains=skills)

        employment_type = self.request.query_params.get('type')
        if employment_type:
            queryset = queryset.filter(employment_type=employment_type)

        experience = self.request.query_params.get('exp')
        if experience:
            queryset = queryset.filter(experience_level=experience)

        min_salary = self.request.query_params.get('min_salary')
        if min_salary:
            try:
                queryset = queryset.filter(max_salary__gte=int(min_salary))
            except ValueError:
                pass

        employer_id = self.request.query_params.get('employer')
        if employer_id:
            queryset = queryset.filter(employer_id=employer_id)

        return queryset.order_by('-created_at')

    def perform_create(self, serializer):
        emp_profile = getattr(self.request.user, 'employer_profile', None)
        company = emp_profile.company if emp_profile else None
        serializer.save(employer=self.request.user, company=company)


class ApplicationViewSet(viewsets.ModelViewSet):
    serializer_class = ApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_platform_admin:
            return Application.objects.select_related('job', 'candidate', 'candidate__candidate_profile', 'job__company').all()
        elif user.is_employer:
            return Application.objects.filter(job__employer=user).select_related('job', 'candidate', 'candidate__candidate_profile', 'job__company')
        else:
            return Application.objects.filter(candidate=user).select_related('job', 'job__company')

    def perform_create(self, serializer):
        job = serializer.validated_data['job']
        app = serializer.save(candidate=self.request.user)

        # Send notification to employer
        Notification.objects.create(
            recipient=job.employer,
            sender=self.request.user,
            title=f"New Candidate Applied: {job.title}",
            message=f"{self.request.user.get_full_name() or self.request.user.username} applied for {job.title}.",
            notification_type='NEW_APPLICATION',
            target_url=f"/dashboard/employer/applicants/?job={job.id}"
        )

        # Send confirmation to candidate
        Notification.objects.create(
            recipient=self.request.user,
            title="Application Sent",
            message=f"You successfully applied for {job.title} at {job.company.name}.",
            notification_type='STATUS_CHANGE',
            target_url="/dashboard/candidate/"
        )

    def perform_update(self, serializer):
        instance = serializer.save()
        # Notify candidate on status update
        Notification.objects.create(
            recipient=instance.candidate,
            sender=self.request.user,
            title=f"Application Update: {instance.job.title}",
            message=f"Your application status has been changed to: {instance.get_status_display()}.",
            notification_type='STATUS_CHANGE',
            target_url="/dashboard/candidate/"
        )


class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all().order_by('name')
    serializer_class = CompanySerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]


class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user).order_by('-created_at')

    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        notif = self.get_object()
        notif.is_read = True
        notif.save()
        return Response({'status': 'marked as read'})

    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
        return Response({'status': 'all marked as read'})


class DashboardStatsAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        data = {}

        if user.is_platform_admin:
            data = {
                'role': 'ADMIN',
                'total_candidates': User.objects.filter(role='CANDIDATE').count(),
                'total_employers': User.objects.filter(role='EMPLOYER').count(),
                'total_jobs': Job.objects.count(),
                'active_jobs': Job.objects.filter(status='ACTIVE').count(),
                'total_applications': Application.objects.count(),
                'total_companies': Company.objects.count(),
                'applications_by_status': {
                    'Pending': Application.objects.filter(status='PENDING').count(),
                    'Shortlisted': Application.objects.filter(status='SHORTLISTED').count(),
                    'Selected': Application.objects.filter(status='SELECTED').count(),
                    'Rejected': Application.objects.filter(status='REJECTED').count(),
                },
                'jobs_by_type': {
                    'Full-time': Job.objects.filter(employment_type='FULL_TIME').count(),
                    'Part-time': Job.objects.filter(employment_type='PART_TIME').count(),
                    'Internship': Job.objects.filter(employment_type='INTERNSHIP').count(),
                    'Contract': Job.objects.filter(employment_type='CONTRACT').count(),
                }
            }
        elif user.is_employer:
            user_jobs = Job.objects.filter(employer=user)
            user_apps = Application.objects.filter(job__employer=user)
            data = {
                'role': 'EMPLOYER',
                'total_posted_jobs': user_jobs.count(),
                'active_jobs': user_jobs.filter(status='ACTIVE').count(),
                'total_applications_received': user_apps.count(),
                'shortlisted_count': user_apps.filter(status='SHORTLISTED').count(),
                'selected_count': user_apps.filter(status='SELECTED').count(),
                'rejected_count': user_apps.filter(status='REJECTED').count(),
            }
        else:
            cand_apps = Application.objects.filter(candidate=user)
            data = {
                'role': 'CANDIDATE',
                'total_applied': cand_apps.count(),
                'pending': cand_apps.filter(status='PENDING').count(),
                'shortlisted': cand_apps.filter(status='SHORTLISTED').count(),
                'selected': cand_apps.filter(status='SELECTED').count(),
                'rejected': cand_apps.filter(status='REJECTED').count(),
            }

        return Response(data)
