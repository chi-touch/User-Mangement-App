from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from .serializer import RegisterSerializer
from accounts.models import User
import json
from django.core import mail
from django.contrib.auth import get_user_model
from accounts.utils import send_verification_email
from accounts.tokens import generate_email_verification_token
from django.urls import reverse


class TestUserSerializer(TestCase):
    def setUp(self):
        self.valid_data = {
            'username': 'chiuser',
            'email': 'chiuser@gmail.com',
            'password': 'chiuserpassword123',
            'first_name': 'chiuser',
            'last_name': 'userc'
        }
        self.client = APIClient()

        self.invalid_data = {
            'username': 'invalid username!',
            'email': 'user@example.com',
            'password': 'validPassword123',
            'first_name': 'ValidFirstName',
            'last_name': 'ValidLastName',
        }

    def test_valid_data_creates_user(self):
        serializer = RegisterSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid())
        user = serializer.save()
        self.assertIsInstance(user, User)
        self.assertEqual(user.username, self.valid_data['username'])
        self.assertEqual(user.first_name, self.valid_data['first_name'])
        self.assertEqual(user.last_name, self.valid_data['last_name'])
        self.assertEqual(user.email, self.valid_data['email'])
        self.assertTrue(user.check_password(self.valid_data['password']))

    def test_invalid_data_raises_errors(self):
        invalid_data_with_invalid_email_and_password = {
            'username': 'invalid username!',
            'email': 'invalidemail',
            'password': 'short',
            'first_name': 'ValidFirstName1',
            'last_name': 'InvalidLastName1',
        }

        serializer = RegisterSerializer(data=invalid_data_with_invalid_email_and_password)
        self.assertFalse(serializer.is_valid())
        self.assertIn('username', serializer.errors)
        self.assertIn('email', serializer.errors)
        self.assertIn('password', serializer.errors)
        self.assertIn('first_name', serializer.errors)
        self.assertIn('last_name', serializer.errors)

    def test_invalid_data_raises_error(self):
        serializer = RegisterSerializer(data=self.invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('username', serializer.errors)

    def test_profile_update(self):
        # Create a user
        user = User.objects.create_user(username='testuser', password='TestPass123!')

        # Authenticate the client with the created user
        self.client.force_authenticate(user=user)

        response = self.client.patch('/accounts/api/profile/', {
            'first_name': 'Test',
            'last_name': 'User'
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], 'Test')
        self.assertEqual(response.data['last_name'], 'User')
        print(response.data)


class LoginViewTest(APITestCase):

    def setUp(self):
        self.username = "testuser"
        self.password = "password123"
        self.email = "testuser@example.com"

        self.user = User.objects.create_user(
            username=self.username,
            email=self.email,
            password=self.password
        )

    def test_login_valid_credentials(self):
        response = self.client.post(
            '/accounts/api/login/',
            data=json.dumps({
                'username': self.username,
                'password': self.password
            }),
            content_type='application/json'
        )

        print(response.data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('refresh', response.data)
        self.assertIn('access', response.data)

    def test_login_invalid_username(self):
        response = self.client.post(
            '/accounts/api/login/',
            data=json.dumps({
                'username': 'wronguser',
                'password': self.password
            }),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_invalid_password(self):
        response = self.client.post(
            '/accounts/api/login/',
            data=json.dumps({
                'username': self.username,
                'password': 'wrongpassword'
            }),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], 'Invalid credentials')


class EmailVerificationTest(TestCase):
    def setUp(self):
        self.User = get_user_model()
        self.user = self.User.objects.create_user(username='testuser', email='testuser@example.com',
                                                  password='password123')
        self.token = generate_email_verification_token(self.user)

    def test_send_verification_email(self):
        send_verification_email(self.user, self.token)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "Verify Your Email")
        self.assertEqual(mail.outbox[0].to, [self.user.email])
        verification_url = f"http://localhost:8000/api/verify-email/{self.token}/"
        self.assertIn(verification_url, mail.outbox[0].body)

    def test_email_verification_link_valid(self):
        url = reverse('verify-email', args=[self.token])
        print(f"Verification URL: {url}")
        response = self.client.get(url)
        print(f"Response status: {response.status_code}")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Email verified successfully")

    def test_invalid_token_is_expired(self):
        invalid_token = "invalid-token"
        url = reverse('verify-email', args=[invalid_token])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 400)
        self.assertContains(response, "Invalid token or expired")

    def test_invalid_token(self):
        invalid_token = "invalid-token"
        url = reverse('verify-email', args=[invalid_token])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid token or user does not exist", response.json().get("error", ""))
