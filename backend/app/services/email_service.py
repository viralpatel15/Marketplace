import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings


async def send_email(to_email: str, subject: str, html_body: str):
    print(f"[DEV] Email to {to_email}: {subject}")


async def send_welcome_email(user_email: str, name: str):
    await send_email(user_email, "Welcome to YourMarket!", f"<p>Hi {name}, welcome!</p>")


async def send_inquiry_confirmation_email(buyer_email: str, product_name: str, company_name: str):
    await send_email(
        buyer_email,
        f"Inquiry sent for {product_name}",
        f"<p>Your inquiry for <b>{product_name}</b> has been sent to <b>{company_name}</b>.</p>",
    )
