# feed/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Comments, CustomUser, News, Notification, UserNotificationSetting
from .utils import trigger_email_notify

@receiver(post_save, sender=Comments)
def on_new_comment(sender, instance, created, **kwargs):
    # only run when brand‑new comment is created, skip update/edit
    if created:
        comment = instance
        post = comment.post

        # Don’t send email if user comments on their own post
        if comment.author != post.author:

            # Check user notification setting (UserNotificationSetting)
            if hasattr(post.author, "notify_setting") and post.author.notify_setting.notify_comment:
                trigger_email_notify(
                    to_email=post.author.email,
                    subject="Griffin Hub: Someone commented your post",
                    post_absolute_url=f"http://127.0.0.1:8000/feed/post/{post.id}/"
                )

@receiver(post_save, sender=News)
def on_new_stuco_news(sender, instance, created, **kwargs):
    """Tell every other user about a newly published StuCo news item."""
    if not created:
        return

    # Set by NewsAdmin when an admin publishes the item, so the author shows up.
    actor = getattr(instance, "_created_by", None)

    opted_out = UserNotificationSetting.objects.filter(
        notify_stuco_news=False
    ).values("user_id")
    recipients = CustomUser.objects.exclude(pk__in=opted_out)
    if actor is not None:
        recipients = recipients.exclude(pk=actor.pk)

    Notification.objects.bulk_create([
        Notification(
            recipient=user,
            actor=actor,
            notification_type="stuco_news",
            news=instance,
            message=f"New StuCo news: {instance.title}",
        )
        for user in recipients
    ])
