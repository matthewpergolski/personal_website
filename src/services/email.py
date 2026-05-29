import os
import asyncio
import smtplib
import ssl
from email.message import EmailMessage
from typing import Tuple, Optional


async def send_email(subject: str, body: str, *, sender: Optional[str] = None, to: Optional[str] = None, reply_to: Optional[str] = None) -> Tuple[bool, str]:
    """Send an email via SMTP using env configuration.

    Returns (ok, info). If SMTP is not configured, returns (False, reason).
    Env vars:
      SMTP_HOST, SMTP_PORT (default 587), SMTP_USER, SMTP_PASSWORD/SMTP_PASS,
      SMTP_FROM (fallback CONTACT_EMAIL), SMTP_TO (fallback CONTACT_EMAIL),
      SMTP_TLS (default true)
    """
    host = os.getenv("SMTP_HOST")
    port = int(os.getenv("SMTP_PORT") or 587)
    user = os.getenv("SMTP_USER")
    password = os.getenv("SMTP_PASSWORD") or os.getenv("SMTP_PASS")
    sender = sender or os.getenv("SMTP_FROM") or os.getenv("CONTACT_EMAIL")
    to = to or os.getenv("SMTP_TO") or os.getenv("CONTACT_EMAIL")
    use_tls = (os.getenv("SMTP_TLS", "true").lower() in ("1", "true", "yes"))

    if not host or not port or not sender or not to:
        return False, "SMTP not configured (missing host/port/from/to)"

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = to
    msg.set_content(body)
    if reply_to and "@" in reply_to:
        msg["Reply-To"] = reply_to

    def _send():
        if str(port) == "465":
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(host, port, context=context, timeout=15) as smtp:
                if user and password:
                    smtp.login(user, password)
                smtp.send_message(msg)
                return
        with smtplib.SMTP(host, port, timeout=15) as smtp:
            smtp.ehlo()
            if use_tls:
                context = ssl.create_default_context()
                smtp.starttls(context=context)
                smtp.ehlo()
            if user and password:
                smtp.login(user, password)
            smtp.send_message(msg)

    try:
        await asyncio.to_thread(_send)
        return True, "sent"
    except Exception as e:
        return False, str(e)
