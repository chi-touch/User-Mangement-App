# accounts/tokens.py
from django.conf import settings
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from itsdangerous import URLSafeTimedSerializer


# from django.utils import six
# from django.contrib.auth import get_user_model
# from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
# from django.template.loader import render_to_string
# from django.utils.encoding import force_bytes, force_text


class EmailVerificationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return str(user.pk) + user.email + str(timestamp)


email_verification_token_generator = EmailVerificationTokenGenerator()

def generate_email_verification_token(user):
    serializer = URLSafeTimedSerializer(settings.SECRET_KEY)
    return serializer.dumps(user.email, salt="email-verification")

# def generate_email_verification_token(user):
#     return email_verification_token_generator.make_token(user)
