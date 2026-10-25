from .models import Notification


def notifications(request):
    """Expose the number of unread notifications to every template."""
    if not request.user.is_authenticated:
        return {"unread_notifications_count": 0}

    count = Notification.objects.filter(
        recipient=request.user, is_read=False
    ).count()
    return {"unread_notifications_count": count}
