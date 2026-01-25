import random
import hashlib
from concurrent.futures.thread import ThreadPoolExecutor
from datetime import timedelta
import sib_api_v3_sdk
from django.utils import timezone
from sib_api_v3_sdk.rest import ApiException
from campusanon import settings
from .models import EmailOTP
import string
import logging

logger = logging.getLogger(__name__)
email_executor = ThreadPoolExecutor(max_workers=3)


def generate_internal_username():
    return "user_" + "".join(
        random.choices(string.ascii_lowercase + string.digits, k=8)
    )

def generate_otp():
    return str(random.randint(100000, 999999))


def hash_email(email: str) -> str:
    return hashlib.sha256(email.encode()).hexdigest()


def _send_email_sync(email, otp):
    try:
        api_key = getattr(settings, "BREVO_API_KEY", None)
        if not api_key:
            logger.error("BREVO_API_KEY is not configured. Unable to send emails.")
            raise RuntimeError("BREVO_API_KEY is not configured. Set it in your environment or settings.")

        configuration = sib_api_v3_sdk.Configuration()
        configuration.api_key['api-key'] = api_key

        api_instance = sib_api_v3_sdk.TransactionalEmailsApi(
            sib_api_v3_sdk.ApiClient(configuration)
        )

        send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
            to=[{"email": email}],
            sender={"email": settings.DEFAULT_FROM_EMAIL, "name": "CampusAnon"},
            subject="Your Verification Code",
            html_content=f"<p>Your OTP is: <strong>{otp}</strong></p><p>It expires in 5 minutes.</p>"
        )

        api_instance.send_transac_email(send_smtp_email)
        logger.info(f"OTP sent successfully to {email}")
    except ApiException as e:
        logger.error(f"Failed to send OTP to {email}: {e}")

def send_email_otp(email):
    otp = generate_otp()

    EmailOTP.objects.update_or_create(
        email=email,
        defaults={
            "otp": otp,
            "expires_at": timezone.now() + timedelta(minutes=5),
            "attempts": 0,
        }
    )

    email_executor.submit(_send_email_sync, email, otp)