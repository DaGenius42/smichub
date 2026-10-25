# utils.py
import requests
import logging

FASTAPI_NOTIFY_URL = "http://127.0.0.1:8001/send-notification"

logger = logging.getLogger(__name__)

def trigger_email_notify(to_email: str, subject: str, post_absolute_url: str):
    """调用FastAPI服务发送邮件通知，失败不崩溃Django，只打日志"""
    params = {
        "to_email": to_email,
        "subject": subject,
        "post_url": post_absolute_url
    }
    try:
        resp = requests.post(FASTAPI_NOTIFY_URL, params=params, timeout=4)
        resp.raise_for_status()
    except Exception as e:
        logger.warning(f"邮件通知调用失败: {str(e)}")
