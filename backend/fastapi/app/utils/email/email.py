import logging
from email.message import EmailMessage

import aiosmtplib

from app.core.config import get_smtp_config

logger = logging.getLogger(__name__)

smtp = get_smtp_config()


def send_email(to: str, subject: str, content: str) -> None:
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


def send_welcome_email(to: str, subject: str):
  """
  Pre-baked template wrapper for onboarding registrations.
  """
  subject = "Welcome to Learnify.edu! 🎉"
  html_template = """
    <html>
        <body style="font-family: sans-serif; color: #333; padding: 20px;">
            <h2 style="color: #4F46E5;">Hello!</h2>
            <p>Thank you for creating an account on <strong>Learnify.edu</strong>.</p>
            <p>Your local full-stack workspace sandbox is officially tracking communications!</p>
            <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;" />
            <small style="color: #666;">This is a system generated notification from your Docker stack.</small>
        </body>
    </html>
    """
  await send_email(to=to, subject=subject, content=html_template)
