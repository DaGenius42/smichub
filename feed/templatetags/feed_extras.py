from datetime import timedelta

from django import template
from django.utils import timezone

register = template.Library()


def _format_time(value):
    """Format a time as H:MM with no leading zero on the hour (e.g. 8:20, 19:20)."""
    hour = value.strftime("%H").lstrip("0") or "0"
    return f"{hour}:{value.strftime('%M')}"


@register.filter
def smart_date(value):
    """Show a friendly timestamp for a post or news item.

    - Today     -> "Today, 8:20"
    - Yesterday -> "Yesterday, 19:20"
    - Older     -> "Aug 4" (no time / year)
    """
    if not value:
        return ""
    local = timezone.localtime(value)
    today = timezone.localdate()
    value_date = local.date()

    if value_date == today:
        return f"Today, {_format_time(local)}"
    if value_date == today - timedelta(days=1):
        return f"Yesterday, {_format_time(local)}"
    return f"{local:%b} {local.day}"
