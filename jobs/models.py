from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from accounts.models import User, Company


class Job(models.Model):
    EMPLOYMENT_TYPES = (
        ('FULL_TIME', 'Full-time'),
        ('PART_TIME', 'Part-time'),
        ('INTERNSHIP', 'Internship'),
        ('CONTRACT', 'Contract'),
    )

    EXPERIENCE_LEVELS = (
        ('ENTRY', 'Entry Level (0-1 yrs)'),
        ('MID', 'Mid Level (2-5 yrs)'),
        ('SENIOR', 'Senior Level (5+ yrs)'),
        ('LEAD', 'Lead / Principal (8+ yrs)'),
    )

    STATUS_CHOICES = (
        ('ACTIVE', 'Active'),
        ('CLOSED', 'Closed'),
        ('EXPIRED', 'Expired'),
    )

    employer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posted_jobs')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='jobs')
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=250, blank=True)
    description = models.TextField()
    required_skills = models.CharField(max_length=300, help_text="Comma-separated skills (e.g. Python, Django, PostgreSQL, Docker)")
    location = models.CharField(max_length=150, default='Remote / Hybrid')
    is_remote = models.BooleanField(default=False)
    employment_type = models.CharField(max_length=20, choices=EMPLOYMENT_TYPES, default='FULL_TIME')
    experience_level = models.CharField(max_length=20, choices=EXPERIENCE_LEVELS, default='ENTRY')
    min_salary = models.PositiveIntegerField(help_text="Annual salary or monthly stipend (in INR)", default=500000)
    max_salary = models.PositiveIntegerField(help_text="Max annual salary or stipend (in INR)", default=1200000)
    salary_negotiable = models.BooleanField(default=True)
    vacancies = models.PositiveIntegerField(default=1)
    deadline = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE')
    is_featured = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=True)
    views_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            self.slug = f"{base_slug}-{int(timezone.now().timestamp())}"
        super().save(*args, **kwargs)

    @property
    def is_expired(self):
        if self.deadline and timezone.now().date() > self.deadline:
            return True
        return self.status == 'EXPIRED'

    @property
    def applications_count(self):
        return self.applications.count()

    def get_skills_list(self):
        if not self.required_skills:
            return []
        return [s.strip() for s in self.required_skills.split(',') if s.strip()]

    def formatted_salary(self):
        min_lakh = self.min_salary / 100000
        max_lakh = self.max_salary / 100000
        if min_lakh >= 1 or max_lakh >= 1:
            return f"₹{min_lakh:.1f}L - ₹{max_lakh:.1f}L / yr"
        return f"₹{self.min_salary:,} - ₹{self.max_salary:,}"

    def __str__(self):
        return f"{self.title} at {self.company.name}"


class Application(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending Review'),
        ('SHORTLISTED', 'Shortlisted'),
        ('REJECTED', 'Rejected'),
        ('SELECTED', 'Selected'),
    )

    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    candidate = models.ForeignKey(User, on_delete=models.CASCADE, related_name='job_applications')
    resume = models.FileField(upload_to='application_resumes/', blank=True, null=True)
    cover_letter = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    employer_notes = models.TextField(blank=True, null=True, help_text="Internal notes or interview feedback")
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-applied_at']
        unique_together = ('job', 'candidate')  # Prevents duplicate applications

    def __str__(self):
        return f"{self.candidate.username} applied for {self.job.title}"
