from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.text import slugify


class User(AbstractUser):
    ROLE_CHOICES = (
        ('ADMIN', 'Admin'),
        ('EMPLOYER', 'Employer'),
        ('CANDIDATE', 'Candidate / Job Seeker'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='CANDIDATE')
    phone = models.CharField(max_length=20, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def is_candidate(self):
        return self.role == 'CANDIDATE'

    @property
    def is_employer(self):
        return self.role == 'EMPLOYER'

    @property
    def is_platform_admin(self):
        return self.role == 'ADMIN' or self.is_superuser or self.is_staff

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"


class Company(models.Model):
    COMPANY_SIZE_CHOICES = (
        ('1-10', '1-10 employees'),
        ('11-50', '11-50 employees'),
        ('51-200', '51-200 employees'),
        ('201-500', '201-500 employees'),
        ('500+', '500+ employees'),
    )

    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    website = models.URLField(blank=True, null=True)
    logo = models.ImageField(upload_to='company_logos/', blank=True, null=True)
    logo_url = models.CharField(max_length=500, blank=True, null=True, help_text="Direct URL fallback for logo")
    industry = models.CharField(max_length=120, default='Technology & Software')
    company_size = models.CharField(max_length=20, choices=COMPANY_SIZE_CHOICES, default='51-200')
    headquarters = models.CharField(max_length=200, default='Bengaluru, India')
    description = models.TextField(blank=True, null=True)
    is_verified = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Companies"
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class EmployerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employer_profile')
    company = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True, blank=True, related_name='employers')
    designation = models.CharField(max_length=120, default='HR Manager')
    is_approved = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        comp = self.company.name if self.company else "No Company"
        return f"{self.user.get_full_name() or self.user.username} @ {comp}"


class CandidateProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='candidate_profile')
    headline = models.CharField(max_length=255, blank=True, null=True, help_text="e.g. Full-Stack Developer | Python & React")
    resume = models.FileField(upload_to='resumes/', blank=True, null=True)
    education_institution = models.CharField(max_length=255, blank=True, null=True)
    education_degree = models.CharField(max_length=150, blank=True, null=True)
    graduation_year = models.PositiveIntegerField(blank=True, null=True)
    cgpa_or_percentage = models.CharField(max_length=50, blank=True, null=True)
    skills = models.TextField(blank=True, null=True, help_text="Comma-separated skills (e.g. Python, Django, React, SQL)")
    experience_years = models.DecimalField(max_digits=4, decimal_places=1, default=0.0)
    current_location = models.CharField(max_length=150, blank=True, null=True)
    github_url = models.URLField(blank=True, null=True)
    linkedin_url = models.URLField(blank=True, null=True)
    portfolio_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_skills_list(self):
        if not self.skills:
            return []
        return [s.strip() for s in self.skills.split(',') if s.strip()]

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username}'s Profile"
