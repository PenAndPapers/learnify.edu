import logging
from email.message import EmailMessage
from pathlib import Path

import aiosmtplib
from jinja2 import Environment, FileSystemLoader

from app.core.config import get_smtp_config

# Resolve path to app/templates directory
TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "email/templates"

logger = logging.getLogger(__name__)

smtp = get_smtp_config()

# Initialize Jinja2 Environment
env = Environment(loader=FileSystemLoader(TEMPLATES_DIR), autoescape=True)


def render_email_template(template_name: str, context: dict) -> str:
  """Load and render an HTML template with the given context variables."""
  template = env.get_template(template_name)
  return template.render(context)


async def send_email(to: str, subject: str, content: str) -> None:
  message = EmailMessage()
  message["From"] = f"{smtp.from_name} <{smtp.from_email}>"
  message["To"] = to
  message["Subject"] = subject
  message.add_alternative(content, subtype="html")

  try:
    await aiosmtplib.send(
      message,
      hostname=smtp.host,
      port=smtp.port,
      username=smtp.user if smtp.user else None,
      password=smtp.password if smtp.password else None,
      use_tls=smtp.use_tls,
    )
    logger.info(f"Successfully dispatched local email to {to}")
  except Exception as e:
    logger.error(f"Failed to transmit email to Mailpit layout: {e}")
    raise e


async def send_test_email():
  """Pre-baked template wrapper for onboarding registrations."""
  html_template = render_email_template("test_email.html", {})

  await send_email(to="test@example.com", subject="Test Email", content=html_template)
