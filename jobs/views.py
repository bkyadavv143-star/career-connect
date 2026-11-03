from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.utils import timezone
import json

from .models import Job, Application
from .forms import JobForm, JobApplicationForm
from accounts.models import User, Company, CandidateProfile, EmployerProfile
from notifications.models import Notification


def home_view(request):
    featured_jobs = Job.objects.filter(status='ACTIVE', is_approved=True, is_featured=True)[:6]
    recent_jobs = Job.objects.filter(status='ACTIVE', is_approved=True)[:8]
    total_jobs = Job.objects.filter(status='ACTIVE').count()
    total_companies = Company.objects.count()
    total_candidates = User.objects.filter(role='CANDIDATE').count()
    total_applications = Application.objects.count()

    categories = [
        {'name': 'Software Development', 'count': Job.objects.filter(title__icontains='Developer').count() or 12, 'icon': 'bi-code-slash'},
        {'name': 'Data Science & AI', 'count': Job.objects.filter(title__icontains='Data').count() or 8, 'icon': 'bi-cpu'},
        {'name': 'Cloud & DevOps', 'count': Job.objects.filter(title__icontains='DevOps').count() or 6, 'icon': 'bi-clouds'},
        {'name': 'UI/UX & Product Design', 'count': Job.objects.filter(title__icontains='Design').count() or 5, 'icon': 'bi-palette'},
        {'name': 'Cybersecurity', 'count': Job.objects.filter(title__icontains='Security').count() or 4, 'icon': 'bi-shield-check'},
        {'name': 'Product & Project Mgmt', 'count': Job.objects.filter(title__icontains='Product').count() or 7, 'icon': 'bi-briefcase'},
    ]

    context = {
        'featured_jobs': featured_jobs,
        'recent_jobs': recent_jobs,
        'total_jobs': total_jobs,
        'total_companies': total_companies,
        'total_candidates': total_candidates,
        'total_applications': total_applications,
        'categories': categories,
    }
    return render(request, 'jobs/home.html', context)


def job_list_view(request):
    jobs = Job.objects.filter(status='ACTIVE', is_approved=True).select_related('company', 'employer')

    # Search query
    q = request.GET.get('q', '').strip()
    loc = request.GET.get('loc', '').strip()
    skill = request.GET.get('skill', '').strip()
    emp_type = request.GET.get('type', '').strip()
    exp_level = request.GET.get('exp', '').strip()
    min_sal = request.GET.get('min_sal', '').strip()
    remote_only = request.GET.get('remote', '').strip()

    if q:
        jobs = jobs.filter(
            Q(title__icontains=q) |
            Q(description__icontains=q) |
            Q(company__name__icontains=q) |
            Q(required_skills__icontains=q)
        )

    if loc:
        jobs = jobs.filter(location__icontains=loc)

    if skill:
        jobs = jobs.filter(required_skills__icontains=skill)

    if emp_type:
        jobs = jobs.filter(employment_type=emp_type)

    if exp_level:
        jobs = jobs.filter(experience_level=exp_level)

    if min_sal:
        try:
            jobs = jobs.filter(max_salary__gte=int(min_sal))
        except ValueError:
            pass

    if remote_only == '1':
        jobs = jobs.filter(is_remote=True)

    paginator = Paginator(jobs, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Context counters for filter badges
    context = {
        'jobs': page_obj,
        'page_obj': page_obj,
        'total_count': jobs.count(),
        'q': q,
        'loc': loc,
        'skill': skill,
        'emp_type': emp_type,
        'exp_level': exp_level,
        'min_sal': min_sal,
        'remote_only': remote_only,
        'employment_types': Job.EMPLOYMENT_TYPES,
        'experience_levels': Job.EXPERIENCE_LEVELS,
    }
    return render(request, 'jobs/job_list.html', context)


def job_detail_view(request, pk):
    job = get_object_or_404(Job.objects.select_related('company', 'employer'), pk=pk)

    # Increment view count
    Job.objects.filter(pk=pk).update(views_count=job.views_count + 1)

    existing_application = None
    if request.user.is_authenticated and request.user.is_candidate:
        existing_application = Application.objects.filter(job=job, candidate=request.user).first()

    similar_jobs = Job.objects.filter(
        status='ACTIVE',
        is_approved=True
    ).exclude(id=job.id).filter(
        Q(employment_type=job.employment_type) | Q(location__icontains=job.location.split(',')[0])
    )[:3]

    apply_form = JobApplicationForm()

    context = {
        'job': job,
        'existing_application': existing_application,
        'similar_jobs': similar_jobs,
        'apply_form': apply_form,
    }
    return render(request, 'jobs/job_detail.html', context)


@login_required
def apply_job_view(request, pk):
    if not request.user.is_candidate:
        messages.error(request, "Only registered candidates can apply for jobs.")
        return redirect('jobs:job_detail', pk=pk)

    job = get_object_or_404(Job, pk=pk)

    if job.status != 'ACTIVE':
        messages.error(request, "This job posting is no longer active.")
        return redirect('jobs:job_detail', pk=pk)

    # Check for duplicate application
    if Application.objects.filter(job=job, candidate=request.user).exists():
        messages.warning(request, "You have already applied for this job.")
        return redirect('jobs:job_detail', pk=pk)

    if request.method == 'POST':
        form = JobApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.job = job
            application.candidate = request.user

            # If user didn't upload a new resume in form, check their candidate profile
            if not application.resume:
                candidate_profile = getattr(request.user, 'candidate_profile', None)
                if candidate_profile and candidate_profile.resume:
                    application.resume = candidate_profile.resume

            application.save()

            # Create notification for Employer
            Notification.objects.create(
                recipient=job.employer,
                sender=request.user,
                title=f"New Applicant for {job.title}",
                message=f"{request.user.get_full_name() or request.user.username} has applied for '{job.title}'.",
                notification_type='NEW_APPLICATION',
                target_url=f"/dashboard/employer/applicants/?job={job.id}"
            )

            # Create notification for Candidate
            Notification.objects.create(
                recipient=request.user,
                title="Application Submitted Successfully",
                message=f"You successfully applied for '{job.title}' at {job.company.name}.",
                notification_type='STATUS_CHANGE',
                target_url="/dashboard/candidate/"
            )

            messages.success(request, f"Your application for {job.title} was submitted successfully!")
            return redirect('accounts:candidate_dashboard')
        else:
            messages.error(request, "There was an error in your submission. Please check your inputs.")
            return redirect('jobs:job_detail', pk=pk)

    return redirect('jobs:job_detail', pk=pk)


@login_required
def withdraw_application_view(request, pk):
    if not request.user.is_candidate:
        messages.error(request, "Access denied.")
        return redirect('accounts:dashboard_redirect')

    application = get_object_or_404(Application, pk=pk, candidate=request.user)
    job_title = application.job.title
    application.delete()

    messages.info(request, f"Your application for '{job_title}' has been withdrawn.")
    return redirect('accounts:candidate_dashboard')


@login_required
def post_job_view(request):
    if not request.user.is_employer and not request.user.is_platform_admin:
        messages.error(request, "Only employers can post jobs.")
        return redirect('accounts:dashboard_redirect')

    emp_profile = getattr(request.user, 'employer_profile', None)
    if not emp_profile or not emp_profile.company:
        messages.warning(request, "Please set up your company profile before posting a job vacancy.")
        return redirect('accounts:employer_profile')

    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.employer = request.user
            job.company = emp_profile.company
            job.save()

            messages.success(request, f"Job vacancy '{job.title}' has been posted successfully!")
            return redirect('accounts:employer_dashboard')
    else:
        form = JobForm()

    return render(request, 'jobs/post_job.html', {'form': form, 'title': 'Post New Job Vacancy'})


@login_required
def edit_job_view(request, pk):
    if not request.user.is_employer and not request.user.is_platform_admin:
        messages.error(request, "Access denied.")
        return redirect('accounts:dashboard_redirect')

    if request.user.is_platform_admin:
        job = get_object_or_404(Job, pk=pk)
    else:
        job = get_object_or_404(Job, pk=pk, employer=request.user)

    if request.method == 'POST':
        form = JobForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            messages.success(request, f"Job '{job.title}' updated successfully.")
            return redirect('accounts:employer_dashboard')
    else:
        form = JobForm(instance=job)

    return render(request, 'jobs/post_job.html', {'form': form, 'job': job, 'title': f'Edit Job: {job.title}'})


@login_required
def delete_job_view(request, pk):
    if not request.user.is_employer and not request.user.is_platform_admin:
        messages.error(request, "Access denied.")
        return redirect('accounts:dashboard_redirect')

    if request.user.is_platform_admin:
        job = get_object_or_404(Job, pk=pk)
    else:
        job = get_object_or_404(Job, pk=pk, employer=request.user)

    title = job.title
    job.delete()
    messages.success(request, f"Job listing '{title}' has been deleted.")
    if request.user.is_platform_admin:
        return redirect('accounts:admin_dashboard')
    return redirect('accounts:employer_dashboard')


@login_required
def toggle_job_status_view(request, pk):
    if not request.user.is_employer and not request.user.is_platform_admin:
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    if request.user.is_platform_admin:
        job = get_object_or_404(Job, pk=pk)
    else:
        job = get_object_or_404(Job, pk=pk, employer=request.user)

    job.status = 'CLOSED' if job.status == 'ACTIVE' else 'ACTIVE'
    job.save()

    messages.info(request, f"Job '{job.title}' status changed to {job.status}.")
    return redirect(request.META.get('HTTP_REFERER', 'accounts:employer_dashboard'))


# --- DASHBOARDS ---

@login_required
def candidate_dashboard_view(request):
    if not request.user.is_candidate:
        messages.error(request, "Access restricted to candidates.")
        return redirect('accounts:dashboard_redirect')

    applications = Application.objects.filter(candidate=request.user).select_related('job', 'job__company')
    profile, _ = CandidateProfile.objects.get_or_create(user=request.user)

    # Status breakdown
    pending_count = applications.filter(status='PENDING').count()
    shortlisted_count = applications.filter(status='SHORTLISTED').count()
    selected_count = applications.filter(status='SELECTED').count()
    rejected_count = applications.filter(status='REJECTED').count()

    # Recommended jobs matching skills
    skills_list = profile.get_skills_list()
    recommended_jobs = Job.objects.filter(status='ACTIVE', is_approved=True)
    if skills_list:
        skill_q = Q()
        for s in skills_list[:3]:
            skill_q |= Q(required_skills__icontains=s)
        recommended_jobs = recommended_jobs.filter(skill_q).exclude(applications__candidate=request.user).distinct()[:4]
    else:
        recommended_jobs = recommended_jobs.exclude(applications__candidate=request.user)[:4]

    context = {
        'applications': applications,
        'profile': profile,
        'total_applied': applications.count(),
        'pending_count': pending_count,
        'shortlisted_count': shortlisted_count,
        'selected_count': selected_count,
        'rejected_count': rejected_count,
        'recommended_jobs': recommended_jobs,
    }
    return render(request, 'dashboard/candidate_dashboard.html', context)


@login_required
def employer_dashboard_view(request):
    if not request.user.is_employer and not request.user.is_platform_admin:
        messages.error(request, "Access restricted to employers.")
        return redirect('accounts:dashboard_redirect')

    emp_profile = getattr(request.user, 'employer_profile', None)
    posted_jobs = Job.objects.filter(employer=request.user).annotate(app_count=Count('applications'))

    total_posted = posted_jobs.count()
    active_jobs = posted_jobs.filter(status='ACTIVE').count()
    total_applications = Application.objects.filter(job__employer=request.user).count()
    shortlisted_candidates = Application.objects.filter(job__employer=request.user, status='SHORTLISTED').count()
    hired_candidates = Application.objects.filter(job__employer=request.user, status='SELECTED').count()

    recent_applications = Application.objects.filter(
        job__employer=request.user
    ).select_related('candidate', 'job', 'candidate__candidate_profile').order_by('-applied_at')[:8]

    context = {
        'posted_jobs': posted_jobs,
        'emp_profile': emp_profile,
        'total_posted': total_posted,
        'active_jobs': active_jobs,
        'total_applications': total_applications,
        'shortlisted_candidates': shortlisted_candidates,
        'hired_candidates': hired_candidates,
        'recent_applications': recent_applications,
    }
    return render(request, 'dashboard/employer_dashboard.html', context)


@login_required
def employer_applicants_view(request):
    if not request.user.is_employer and not request.user.is_platform_admin:
        messages.error(request, "Access restricted to employers.")
        return redirect('accounts:dashboard_redirect')

    jobs = Job.objects.filter(employer=request.user)
    applications = Application.objects.filter(job__employer=request.user).select_related(
        'job', 'candidate', 'candidate__candidate_profile'
    )

    # Filtering
    job_id = request.GET.get('job')
    status_filter = request.GET.get('status')

    if job_id:
        applications = applications.filter(job_id=job_id)
    if status_filter:
        applications = applications.filter(status=status_filter)

    context = {
        'applications': applications,
        'jobs': jobs,
        'selected_job_id': job_id,
        'selected_status': status_filter,
        'status_choices': Application.STATUS_CHOICES,
    }
    return render(request, 'dashboard/employer_applicants.html', context)


@login_required
def update_application_status_view(request, pk):
    if not request.user.is_employer and not request.user.is_platform_admin:
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    if request.user.is_platform_admin:
        application = get_object_or_404(Application, pk=pk)
    else:
        application = get_object_or_404(Application, pk=pk, job__employer=request.user)

    if request.method == 'POST':
        new_status = request.POST.get('status')
        notes = request.POST.get('notes', '')

        if new_status in dict(Application.STATUS_CHOICES):
            application.status = new_status
            if notes:
                application.employer_notes = notes
            application.save()

            # Notify candidate about status change
            status_labels = {
                'PENDING': 'Pending Review',
                'SHORTLISTED': 'Shortlisted for Interview 🎉',
                'SELECTED': 'Selected / Offer Extended 🏆',
                'REJECTED': 'Application Not Selected'
            }
            Notification.objects.create(
                recipient=application.candidate,
                sender=request.user,
                title=f"Application Update: {application.job.title}",
                message=f"Your application status for '{application.job.title}' at {application.job.company.name} has been updated to: {status_labels.get(new_status, new_status)}." + (f" Note: {notes}" if notes else ""),
                notification_type='STATUS_CHANGE',
                target_url="/dashboard/candidate/"
            )

            messages.success(request, f"Candidate status updated to '{status_labels.get(new_status, new_status)}'.")

    return redirect(request.META.get('HTTP_REFERER', 'accounts:employer_applicants'))


@login_required
def admin_dashboard_view(request):
    if not request.user.is_platform_admin:
        messages.error(request, "Access restricted to Platform Administrators.")
        return redirect('accounts:dashboard_redirect')

    total_candidates = User.objects.filter(role='CANDIDATE').count()
    total_employers = User.objects.filter(role='EMPLOYER').count()
    total_jobs = Job.objects.count()
    active_jobs = Job.objects.filter(status='ACTIVE').count()
    total_applications = Application.objects.count()
    total_companies = Company.objects.count()

    # Chart data
    # 1. Applications by status
    status_counts = {
        'Pending': Application.objects.filter(status='PENDING').count(),
        'Shortlisted': Application.objects.filter(status='SHORTLISTED').count(),
        'Selected': Application.objects.filter(status='SELECTED').count(),
        'Rejected': Application.objects.filter(status='REJECTED').count(),
    }

    # 2. Jobs by employment type
    job_types = {
        'Full-time': Job.objects.filter(employment_type='FULL_TIME').count(),
        'Part-time': Job.objects.filter(employment_type='PART_TIME').count(),
        'Internship': Job.objects.filter(employment_type='INTERNSHIP').count(),
        'Contract': Job.objects.filter(employment_type='CONTRACT').count(),
    }

    # Recent items
    recent_users = User.objects.order_by('-date_joined')[:6]
    recent_jobs = Job.objects.select_related('company', 'employer').order_by('-created_at')[:8]
    companies = Company.objects.annotate(jobs_count=Count('jobs')).order_by('-created_at')[:6]

    context = {
        'total_candidates': total_candidates,
        'total_employers': total_employers,
        'total_jobs': total_jobs,
        'active_jobs': active_jobs,
        'total_applications': total_applications,
        'total_companies': total_companies,
        'status_counts_json': json.dumps(status_counts),
        'job_types_json': json.dumps(job_types),
        'recent_users': recent_users,
        'recent_jobs': recent_jobs,
        'companies': companies,
    }
    return render(request, 'dashboard/admin_dashboard.html', context)


@login_required
def admin_toggle_job_approval_view(request, pk):
    if not request.user.is_platform_admin:
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    job = get_object_or_404(Job, pk=pk)
    job.is_approved = not job.is_approved
    job.save()

    status_str = "Approved" if job.is_approved else "Unapproved"
    messages.info(request, f"Job '{job.title}' is now {status_str}.")
    return redirect(request.META.get('HTTP_REFERER', 'accounts:admin_dashboard'))


@login_required
def admin_toggle_user_status_view(request, pk):
    if not request.user.is_platform_admin:
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    user_obj = get_object_or_404(User, pk=pk)
    if user_obj.is_superuser:
        messages.warning(request, "Cannot deactivate superuser.")
        return redirect('accounts:admin_dashboard')

    user_obj.is_active = not user_obj.is_active
    user_obj.save()

    status_str = "Active" if user_obj.is_active else "Suspended"
    messages.info(request, f"User '{user_obj.username}' status set to {status_str}.")
    return redirect('accounts:admin_dashboard')


@login_required
def admin_toggle_company_verification_view(request, pk):
    if not request.user.is_platform_admin:
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    comp = get_object_or_404(Company, pk=pk)
    comp.is_verified = not comp.is_verified
    comp.save()

    status_str = "Verified" if comp.is_verified else "Unverified"
    messages.info(request, f"Company '{comp.name}' is now {status_str}.")
    return redirect('accounts:admin_dashboard')
