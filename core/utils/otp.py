import random

from django.utils import timezone


def generate_otp(length=6):
    return "".join(str(random.randint(0, 9)) for _ in range(length))


def set_user_otp(user, purpose, length=6):
    user.otp_code = generate_otp(length=length)
    user.otp_purpose = purpose
    user.otp_created_at = timezone.now()
    user.save(update_fields=["otp_code", "otp_purpose", "otp_created_at"])
    return user.otp_code
