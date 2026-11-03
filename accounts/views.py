from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction

from .models import User, Company, CandidateProfile, EmployerProfile
from .forms import (
    LoginForm, CandidateRegistrationForm, EmployerRegistrationForm,
    CandidateProfileUpdateForm, CompanyUpdateForm
)
from notifications.models import Notification


def login_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:dashboard_redirect')

    form = LoginForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']

        # Allow login by email or username
        user = authenticate(request, username=username, password=password)
        if not user:
            # Try to lookup username by email
            try:
                user_obj = User.objects.get(email=username)
                user = authenticate(request, username=user_obj.username, password=password)
            except User.DoesNotExist:
                user = None

        if user:
            login(request, user)
            messages.success(request, f"Welcome back, {user.first_name or user.username}!")
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('accounts:dashboard_redirect')
        else:
            messages.error(request, "Invalid username/email or password.")

    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out successfully.")
    return redirect('jobs:job_list')


def register_candidate_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:dashboard_redirect')

    form = CandidateRegistrationForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        with transaction.atomic():
            user = form.save(commit=False)
            user.role = 'CANDIDATE'
            user.set_password(form.cleaned_data['password'])
            user.save()

            profile = CandidateProfile.objects.create(
                user=user,
                headline=form.cleaned_data.get('headline'),
                skills=form.cleaned_data.get('skills'),
                education_degree=form.cleaned_data.get('education_degree'),
                education_institution=form.cleaned_data.get('education_institution'),
                resume=form.cleaned_data.get('resume'),
            )

            # Send welcome notification
            Notification.objects.create(
                recipient=user,
                title="Welcome to CareerConnect!",
                message="Your candidate profile has been created. Start browsing exciting career opportunities!",
                notification_type='SYSTEM',
                target_url='/jobs/'
            )

            login(request, user)
            messages.success(request, f"Account created! Welcome to CareerConnect, {user.first_name}!")
            return redirect('accounts:candidate_dashboard')

    return render(request, 'accounts/register_candidate.html', {'form': form})


def register_employer_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:dashboard_redirect')

    form = EmployerRegistrationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        with transaction.atomic():
            user = form.save(commit=False)
            user.role = 'EMPLOYER'
            user.set_password(form.cleaned_data['password'])
            user.save()

            company_name = form.cleaned_data['company_name']
            company, _ = Company.objects.get_or_create(
                name=company_name,
                defaults={
                    'website': form.cleaned_data.get('company_website') or '',
                    'industry': form.cleaned_data.get('company_industry') or 'Technology & Software',
                    'company_size': form.cleaned_data.get('company_size') or '51-200',
                    'headquarters': form.cleaned_data.get('company_headquarters') or 'Bengaluru, India',
                    'description': f"Official profile for {company_name}",
                }
            )

            EmployerProfile.objects.create(
                user=user,
                company=company,
                designation=form.cleaned_data.get('designation') or 'Hiring Manager'
            )

            # Send welcome notification
            Notification.objects.create(
                recipient=user,
                title="Welcome Employer!",
                message="Your employer account is set up. Post your first job vacancy to start receiving top candidates.",
                notification_type='SYSTEM',
                target_url='/jobs/post/'
            )

            login(request, user)
            messages.success(request, f"Welcome {user.first_name}! Your employer account for {company.name} is ready.")
            return redirect('accounts:employer_dashboard')

    return render(request, 'accounts/register_employer.html', {'form': form})


@login_required
def dashboard_redirect(request):
    if request.user.is_platform_admin:
        return redirect('accounts:admin_dashboard')
    elif request.user.is_employer:
        return redirect('accounts:employer_dashboard')
    else:
        return redirect('accounts:candidate_dashboard')


@login_required
def candidate_profile_view(request):
    if not request.user.is_candidate:
        messages.error(request, "Access restricted to candidates.")
        return redirect('accounts:dashboard_redirect')

    profile, _ = CandidateProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = CandidateProfileUpdateForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            user = request.user
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.email = form.cleaned_data['email']
            user.phone = form.cleaned_data['phone']
            user.bio = form.cleaned_data['bio']
            user.save()

            form.save()
            messages.success(request, "Your candidate profile and resume have been updated successfully!")
            return redirect('accounts:candidate_profile')
    else:
        initial = {
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'email': request.user.email,
            'phone': request.user.phone,
            'bio': request.user.bio,
        }
        form = CandidateProfileUpdateForm(instance=profile, initial=initial)

    return render(request, 'accounts/profile_candidate.html', {'form': form, 'profile': profile})


@login_required
def employer_profile_view(request):
    if not request.user.is_employer and not request.user.is_platform_admin:
        messages.error(request, "Access restricted to employers.")
        return redirect('accounts:dashboard_redirect')

    emp_profile, _ = EmployerProfile.objects.get_or_create(user=request.user)
    company = emp_profile.company

    if request.method == 'POST':
        comp_form = CompanyUpdateForm(request.POST, instance=company) if company else None
        designation = request.POST.get('designation', emp_profile.designation)
        first_name = request.POST.get('first_name', request.user.first_name)
        last_name = request.POST.get('last_name', request.user.last_name)
        phone = request.POST.get('phone', request.user.phone)

        if comp_form and comp_form.is_valid():
            comp_form.save()

        emp_profile.designation = designation
        emp_profile.save()

        request.user.first_name = first_name
        request.user.last_name = last_name
        request.user.phone = phone
        request.user.save()

        messages.success(request, "Company details and recruiter profile updated!")
        return redirect('accounts:employer_profile')
    else:
        comp_form = CompanyUpdateForm(instance=company) if company else None

    return render(request, 'accounts/profile_employer.html', {
        'comp_form': comp_form,
        'emp_profile': emp_profile,
        'company': company
    })


def quick_demo_login(request, role):
    """
    Convenient 1-click login for examiners and viva demonstrations.
    Roles: 'admin', 'employer', 'candidate'
    """
    role_map = {
        'admin': 'admin',
        'employer': 'techlead_google',
        'candidate': 'rahul_sharma'
    }

    username = role_map.get(role.lower())
    if not username:
        messages.error(request, f"Unknown demo role: {role}")
        return redirect('accounts:login')

    try:
        user = User.objects.get(username=username)
        login(request, user)
        messages.success(request, f"Demo Logged in as {user.get_role_display()} ({user.username})")
        return redirect('accounts:dashboard_redirect')
    except User.DoesNotExist:
        messages.warning(request, f"Demo user '{username}' not found. Please run the seed command.")
        return redirect('accounts:login')
