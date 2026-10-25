# feed/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Comments
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
