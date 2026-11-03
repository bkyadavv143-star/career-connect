from notifications.models import Notification

def platform_context(request):
    unread_notifications_count = 0
    recent_notifications = []
    if request.user.is_authenticated:
        unread_notifications_count = Notification.objects.filter(recipient=request.user, is_read=False).count()
        recent_notifications = Notification.objects.filter(recipient=request.user).order_by('-created_at')[:5]

    return {
        'unread_notifications_count': unread_notifications_count,
        'recent_notifications': recent_notifications,
        'SITE_NAME': 'CareerConnect',
        'SITE_TAGLINE': 'Connecting Top Talent with Great Companies',
    }

