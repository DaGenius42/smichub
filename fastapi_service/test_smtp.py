# test_smtp.py
import os
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()

MAIL_USERNAME = os.getenv("MAIL_USERNAME")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
MAIL_SERVER = os.getenv("MAIL_SERVER")
MAIL_PORT = int(os.getenv("MAIL_PORT"))

msg = MIMEText("This is a raw SMTP test.")
msg["Subject"] = "Raw SMTP Test"
msg["From"] = MAIL_USERNAME
msg["To"] = MAIL_USERNAME

try:
    with smtplib.SMTP_SSL(MAIL_SERVER, MAIL_PORT) as server:
        server.login(MAIL_USERNAME, MAIL_PASSWORD)
        server.send_message(msg)
    print("✅ Success! Email sent.")
except Exception as e:
    print(f"❌ Error: {e}")
