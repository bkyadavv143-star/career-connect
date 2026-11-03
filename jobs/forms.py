from django import forms
from .models import Job, Application


class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = [
            'title', 'description', 'required_skills', 'location',
            'is_remote', 'employment_type', 'experience_level',
            'min_salary', 'max_salary', 'salary_negotiable',
            'vacancies', 'deadline', 'status', 'is_featured'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Senior Full-Stack Python Engineer'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 6, 'placeholder': 'Detailed job description, responsibilities, requirements, and perks...'}),
            'required_skills': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Python, Django, React, PostgreSQL, Docker'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Bengaluru, Karnataka (or Remote)'}),
            'is_remote': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'employment_type': forms.Select(attrs={'class': 'form-select'}),
            'experience_level': forms.Select(attrs={'class': 'form-select'}),
            'min_salary': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '600000'}),
            'max_salary': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '1400000'}),
            'salary_negotiable': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'vacancies': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'deadline': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class JobApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['resume', 'cover_letter']
        widgets = {
            'cover_letter': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Explain why you are a great fit for this role, your relevant achievements, and when you can join...'
            }),
            'resume': forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf'}),
        }

    def clean_resume(self):
        resume = self.cleaned_data.get('resume')
        if resume and hasattr(resume, 'size'):
            if not resume.name.lower().endswith('.pdf'):
                raise forms.ValidationError("Only PDF files are supported.")
            if resume.size > 5 * 1024 * 1024:
                raise forms.ValidationError("Resume size must not exceed 5MB.")
        return resume

