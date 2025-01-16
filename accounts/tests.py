from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from .serializer import RegisterSerializer
from accounts.models import User
import json


class TestUserSerializer(TestCase):
    def setUp(self):
        self.valid_data = {
            'username': 'chiuser',
            'email': 'chiuser@gmail.com',
            'password': 'chiuserpassword123',
            'first_name': 'chiuser',
            'last_name': 'userc'
        }

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


class LoginViewTest(APITestCase):

    def setUp(self):
        self.username = "testuser"
        self.password = "password123"
        self.user = User.objects.create_user(username=self.username, password=self.password)

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
        self.assertEqual(response.data['detail'], 'Invalid credentials')

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


