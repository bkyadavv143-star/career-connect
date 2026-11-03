from django.urls import path
from . import views

app_name = 'jobs'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('jobs/', views.job_list_view, name='job_list'),
    path('jobs/post/', views.post_job_view, name='post_job'),
    path('jobs/<int:pk>/', views.job_detail_view, name='job_detail'),
    path('jobs/<int:pk>/edit/', views.edit_job_view, name='edit_job'),
    path('jobs/<int:pk>/delete/', views.delete_job_view, name='delete_job'),
    path('jobs/<int:pk>/toggle-status/', views.toggle_job_status_view, name='toggle_status'),
    path('jobs/<int:pk>/apply/', views.apply_job_view, name='apply_job'),
    path('applications/<int:pk>/withdraw/', views.withdraw_application_view, name='withdraw_application'),
    path('applications/<int:pk>/update-status/', views.update_application_status_view, name='update_application_status'),

    # Admin moderation actions
    path('admin/jobs/<int:pk>/toggle-approval/', views.admin_toggle_job_approval_view, name='admin_toggle_approval'),
    path('admin/jobs/<int:pk>/delete/', views.delete_job_view, name='admin_delete_job'),
    path('admin/users/<int:pk>/toggle-status/', views.admin_toggle_user_status_view, name='admin_toggle_user'),
    path('admin/companies/<int:pk>/toggle-verify/', views.admin_toggle_company_verification_view, name='admin_toggle_company'),
]

