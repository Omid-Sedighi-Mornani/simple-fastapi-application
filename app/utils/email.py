import aiosmtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from jinja2 import Environment, FileSystemLoader, select_autoescape
import os

jinja_env = Environment(
    loader=FileSystemLoader("templates"), autoescape=select_autoescape(["html", "xml"])
)


async def render_email_template(template_name: str, context: dict):
    template = jinja_env.get_template(template_name)
    return template.render(context)


async def send_email(
    recipient: str, subject: str, html_content: str, fallback: str = None
):
    message = MIMEMultipart("alternative")
    message["From"] = os.getenv("MAIL_USERNAME")
    message["To"] = recipient
    message["Subject"] = subject

    main_part = MIMEText(html_content, "html")
    message.attach(main_part)

    if fallback:
        fallback_part = MIMEText(fallback, "plain")
        message.attach(fallback_part)

    await aiosmtplib.send(
        message,
        hostname=os.getenv("MAIL_SERVER"),
        port=os.getenv("MAIL_PORT"),
        start_tls=True,
        username=os.getenv("MAIL_USERNAME"),
        password=os.getenv("MAIL_PASSWORD"),
    )
