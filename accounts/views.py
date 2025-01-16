from sqlite3 import DatabaseError

from django.contrib.auth import authenticate, get_user_model

from django.shortcuts import render
from rest_framework.status import HTTP_200_OK
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings
import logging

from .serializer import RegisterSerializer, LoginSerializer, ProfileUpdateSerializer, ChangePasswordSerializer
from .utils import generate_email_verification_token, send_verification_email, verify_email_verification_token


class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user.is_active = False
            user.save()

            token = generate_email_verification_token(user.email)
            send_verification_email(user, token)

            return Response({"message": "User registered successfully. Please verify your email."},
                            status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(username=username, password=password)
        if not user:
            raise AuthenticationFailed('Invalid credentials')

        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=HTTP_200_OK)


class ProfileUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        serializer = ProfileUpdateSerializer(instance=request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

logger = logging.getLogger(__name__)
class VerifyEmailView(APIView):
    def get(self, request, token):
        logger.info(f"Received token: {token}")
        email = verify_email_verification_token(token)

        if email:
            try:
                user = get_user_model().objects.get(email=email)
                user.is_verified = True
                user.is_active = True
                user.save()
                logger.info(f"Email verified and user activated: {email}")
                return Response({"message": "Email verified successfully."}, status=status.HTTP_200_OK)
            except get_user_model().DoesNotExist:
                logger.warning(f"User does not exist for email: {email}")
                return Response({"error": "Invalid token or user does not exist."}, status=status.HTTP_400_BAD_REQUEST)
            except DatabaseError as e:
                logger.error(f"Database error during email verification: {str(e)}")
                return Response({"error": "Internal server error."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


        logger.warning("Invalid or expired token.")
        return Response({"error": "Invalid or expired token."}, status=status.HTTP_400_BAD_REQUEST)

