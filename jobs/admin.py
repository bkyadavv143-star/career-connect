from django.contrib import admin
from .models import Job, Application


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'location', 'employment_type', 'experience_level', 'status', 'is_featured', 'is_approved', 'created_at')
    list_filter = ('status', 'employment_type', 'experience_level', 'is_featured', 'is_approved')
    search_fields = ('title', 'company__name', 'required_skills', 'location')
    list_editable = ('status', 'is_featured', 'is_approved')


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('candidate', 'job', 'status', 'applied_at')
    list_filter = ('status', 'applied_at')
    search_fields = ('candidate__username', 'job__title', 'job__company__name')
    list_editable = ('status',)
