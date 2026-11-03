from django.urls import path
from . import views
from jobs import views as job_views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/candidate/', views.register_candidate_view, name='register_candidate'),
    path('register/employer/', views.register_employer_view, name='register_employer'),
    path('dashboard/', views.dashboard_redirect, name='dashboard_redirect'),
    path('dashboard/candidate/', job_views.candidate_dashboard_view, name='candidate_dashboard'),
    path('dashboard/employer/', job_views.employer_dashboard_view, name='employer_dashboard'),
    path('dashboard/employer/applicants/', job_views.employer_applicants_view, name='employer_applicants'),
    path('dashboard/admin/', job_views.admin_dashboard_view, name='admin_dashboard'),
    path('profile/candidate/', views.candidate_profile_view, name='candidate_profile'),
    path('profile/employer/', views.employer_profile_view, name='employer_profile'),
    path('demo-login/<str:role>/', views.quick_demo_login, name='demo_login'),
]

