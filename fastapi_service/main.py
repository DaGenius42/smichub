from fastapi import FastAPI, BackgroundTasks
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from pydantic_settings import BaseSettings, SettingsConfigDict

# Read env
class Settings(BaseSettings):
    mail_username: str
    mail_password: str
    mail_from: str
    mail_port: int
    mail_server: str
    mail_starttls: bool
    mail_ssl_tls: bool

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()

conf = ConnectionConfig(
    MAIL_USERNAME = settings.mail_username,
    MAIL_PASSWORD = settings.mail_password,
    MAIL_FROM = settings.mail_from,
    MAIL_PORT = settings.mail_port,
    MAIL_SERVER = settings.mail_server,
    MAIL_STARTTLS = settings.mail_starttls,
    MAIL_SSL_TLS = settings.mail_ssl_tls,
    USE_CREDENTIALS=True
)

app = FastAPI(title="Griffin Hub Notification Service")

# 异步发送邮件函数（放到后台任务，不阻塞http请求）
async def send_email_background(recipient_email: str, subject: str, body_html: str):
    message = MessageSchema(
        subject=subject,
        recipients=[recipient_email],
        body=body_html,
        subtype="html"
    )
    fm = FastMail(conf)
    await fm.send_message(message)


# 测试接口：调用这个API就会发邮件
@app.post("/send-notification")
async def send_notification(
    background_tasks: BackgroundTasks,
    to_email: str,
    subject: str,
    post_url: str
):
    # 邮件HTML模板，可以自定义，里面带上跳转回Griffin Hub帖子链接
    html_body = f"""
    <h3>Griffin Hub Notification</h3>
    <p>Someone interacted with your post!</p>
    <a href="{post_url}">Click here view the post</a>
    """
    # 添加后台任务，不会等待邮件发送完成就返回response
    background_tasks.add_task(
        send_email_background,
        recipient_email=to_email,
        subject=subject,
        body_html=html_body
    )
    return {"status":"ok", "msg":"Email task added to background"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)

@app.get("/check-config")
def check_config():
    return {
        "mail_username": settings.mail_username,
        "mail_server": settings.mail_server,
        "mail_port": settings.mail_port
    }
