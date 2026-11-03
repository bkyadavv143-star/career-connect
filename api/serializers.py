from rest_framework import serializers
from accounts.models import User, Company, CandidateProfile, EmployerProfile
from jobs.models import Job, Application
from notifications.models import Notification


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'phone', 'role', 'bio']
        read_only_fields = ['id']


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['id', 'name', 'slug', 'website', 'logo_url', 'industry', 'company_size', 'headquarters', 'description', 'is_verified', 'created_at']
        read_only_fields = ['id', 'slug', 'created_at']


class CandidateProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = CandidateProfile
        fields = [
            'id', 'user', 'headline', 'resume', 'education_degree',
            'education_institution', 'graduation_year', 'cgpa_or_percentage',
            'skills', 'experience_years', 'current_location',
            'github_url', 'linkedin_url', 'portfolio_url', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class EmployerProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    company = CompanySerializer(read_only=True)

    class Meta:
        model = EmployerProfile
        fields = ['id', 'user', 'company', 'designation', 'is_approved', 'created_at']
        read_only_fields = ['id', 'created_at']


class JobSerializer(serializers.ModelSerializer):
    company_details = CompanySerializer(source='company', read_only=True)
    employer_name = serializers.CharField(source='employer.get_full_name', read_only=True)
    applications_count = serializers.IntegerField(read_only=True)
    formatted_salary = serializers.CharField(read_only=True)

    class Meta:
        model = Job
        fields = [
            'id', 'title', 'slug', 'employer', 'employer_name', 'company',
            'company_details', 'description', 'required_skills', 'location',
            'is_remote', 'employment_type', 'experience_level', 'min_salary',
            'max_salary', 'salary_negotiable', 'formatted_salary', 'vacancies',
            'deadline', 'status', 'is_featured', 'is_approved', 'views_count',
            'applications_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'slug', 'employer', 'created_at', 'updated_at', 'views_count']


class ApplicationSerializer(serializers.ModelSerializer):
    job_details = JobSerializer(source='job', read_only=True)
    candidate_details = UserSerializer(source='candidate', read_only=True)
    candidate_profile = CandidateProfileSerializer(source='candidate.candidate_profile', read_only=True)

    class Meta:
        model = Application
        fields = [
            'id', 'job', 'job_details', 'candidate', 'candidate_details',
            'candidate_profile', 'resume', 'cover_letter', 'status',
            'employer_notes', 'applied_at', 'updated_at'
        ]
        read_only_fields = ['id', 'candidate', 'applied_at', 'updated_at']

    def validate(self, attrs):
        request = self.context.get('request')
        job = attrs.get('job')
        if request and request.method == 'POST':
            if Application.objects.filter(job=job, candidate=request.user).exists():
                raise serializers.ValidationError({"non_field_errors": ["You have already applied for this job."]})
        return attrs


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'recipient', 'sender', 'title', 'message', 'notification_type', 'target_url', 'is_read', 'created_at']
        read_only_fields = ['id', 'recipient', 'sender', 'created_at']

