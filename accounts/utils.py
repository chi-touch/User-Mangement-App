from rest_framework.views import exception_handler
from rest_framework.exceptions import AuthenticationFailed
from rest_framework import status
from itsdangerous import URLSafeTimedSerializer
from django.conf import settings
from django.core.mail import send_mail
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from django.conf import settings


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if isinstance(exc, AuthenticationFailed):
        response.status_code = status.HTTP_401_UNAUTHORIZED

    return response


def generate_email_verification_token(email):
    serializer = URLSafeTimedSerializer(settings.SECRET_KEY)
    return serializer.dumps(email, salt="email-verification")


def send_verification_email(user, token):
    subject = "Verify Your Email"
    verification_url = f"http://localhost:8000/api/verify-email/{token}/"
    message = f"Hi {user.username},\n\nClick the link below to verify your email:\n\n{verification_url}"
    send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email])


def verify_email_verification_token(token):
    serializer = URLSafeTimedSerializer(settings.SECRET_KEY)
    try:
        email = serializer.loads(token, salt="email-verification", max_age=3600)
        return email
    except SignatureExpired:
        return {"error": "Token expired."}
    except BadSignature:
        return {"error": "Invalid token."}
