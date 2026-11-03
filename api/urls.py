from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    JobViewSet, ApplicationViewSet, CompanyViewSet,
    NotificationViewSet, DashboardStatsAPIView
)

router = DefaultRouter()
router.register(r'jobs', JobViewSet, basename='api-job')
router.register(r'applications', ApplicationViewSet, basename='api-application')
router.register(r'companies', CompanyViewSet, basename='api-company')
router.register(r'notifications', NotificationViewSet, basename='api-notification')

urlpatterns = [
    path('stats/', DashboardStatsAPIView.as_view(), name='api-stats'),
    path('', include(router.urls)),
]

