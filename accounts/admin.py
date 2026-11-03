from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Company, CandidateProfile, EmployerProfile


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'phone', 'is_active', 'is_staff')
    list_filter = ('role', 'is_active', 'is_staff')
    fieldsets = UserAdmin.fieldsets + (
        ('Platform Details', {'fields': ('role', 'phone', 'profile_picture', 'bio')}),
    )


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'industry', 'company_size', 'headquarters', 'is_verified', 'created_at')
    list_filter = ('industry', 'company_size', 'is_verified')
    search_fields = ('name', 'headquarters', 'industry')


@admin.register(CandidateProfile)
class CandidateProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'headline', 'experience_years', 'current_location', 'education_degree')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'headline', 'skills')


@admin.register(EmployerProfile)
class EmployerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'company', 'designation', 'is_approved')
    list_filter = ('is_approved',)
    search_fields = ('user__username', 'company__name', 'designation')
