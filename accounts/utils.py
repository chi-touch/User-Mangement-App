from rest_framework.views import exception_handler
from rest_framework.exceptions import AuthenticationFailed
from rest_framework import status


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if isinstance(exc, AuthenticationFailed):
        response.status_code = status.HTTP_401_UNAUTHORIZED

    return response
