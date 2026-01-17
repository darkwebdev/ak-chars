import os
import smtplib
import logging
from email.message import EmailMessage

logger = logging.getLogger('ak-chars.emailer')

SMTP_HOST = os.getenv('SMTP_HOST')
SMTP_PORT = int(os.getenv('SMTP_PORT') or 0)
SMTP_USER = os.getenv('SMTP_USER')
SMTP_PASS = os.getenv('SMTP_PASS')


def send_email(to_email: str, subject: str, body: str) -> bool:
    """Send email if SMTP is configured, otherwise print to stdout (dev).

    Returns True if SMTP was used, False if fallback (printed).
    """
    if SMTP_HOST and SMTP_PORT and SMTP_USER and SMTP_PASS:
        logger.info('Sending email to %s via SMTP %s:%s', to_email, SMTP_HOST, SMTP_PORT)
        msg = EmailMessage()
        msg['From'] = SMTP_USER
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.set_content(body)
        try:
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as s:
                s.starttls()
                s.login(SMTP_USER, SMTP_PASS)
                s.send_message(msg)
            logger.info('Email sent to %s', to_email)
            return True
        except Exception as e:
            logger.exception('Failed to send email to %s via SMTP: %s', to_email, e)
            # fall back to printing the code
    # dev fallback - print the code
    logger.info('SMTP not configured or failed; printing email to stdout for %s', to_email)
    print(f"Send email to {to_email}: {subject}\n{body}")
    return False
