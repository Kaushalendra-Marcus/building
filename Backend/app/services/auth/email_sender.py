import aiosmtplib
from email.message import EmailMessage
from app.config import get_settings

settings = get_settings()

async def send_verification_email(to_email: str, token: str):
    link = link = f"{settings.FRONTEND_URL}/verify?token={token}"

    msg = EmailMessage()
    msg["Subject"] = "Verify your email"
    msg["From"] = settings.EMAIL_FROM
    msg["To"] = to_email
    msg.set_content(f"Click to verify your email:\n{link}")

    await aiosmtplib.send(
        msg,
        hostname=settings.SMTP_HOST,
        port=settings.SMTP_PORT,
        username=settings.SMTP_USER,
        password=settings.SMTP_PASS,
        start_tls=True,
    )