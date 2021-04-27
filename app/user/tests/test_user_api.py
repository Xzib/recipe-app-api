from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):
    """Tests the user API (public)"""

    def set_up(self):
        self.client = APIClient()

    def test_create_valid_user_success(self):
        """Test that create a valid user successfully"""
        payload = {
            'email': 'zohaib@123.com',
            'password': 'zohaib1234',
            'name': 'zohaib',
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**res.data)
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_user_exists(self):
        """Test for user that already exists"""
        payload = {
            'email': 'zohaib@123.com',
            'password': 'zohaib123',
            'name': 'zohaib',
        }
        create_user(**payload)

        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """Test that password must be greater than 5 chars"""
        payload = {
            'email': 'zohaib@123.com',
            'password': 'pw',
            'name': 'zohaib',
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        """Test that a token is created for the user"""
        payload = {
            'email': 'zohaib@123.com',
            'password': 'pass213',
            'name': 'zohaib'
        }
        create_user(**payload)
        res = self.client.post(TOKEN_URL, payload)

        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_invalid_creadentials(self):
        """Test that token is not created if invalid creadentials are passed"""
        create_user(email='zohaib@123.com', password='testpass')
        payload = {
            'email': 'zohaib@123.com',
            'password': 'wrong',
        }

        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('Token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_no_user(self):
        """Test that token is not created if user doesn't exist"""
        payload = {
            'email': 'zohaib@123.com',
            'password': 'pass1234',
        }

        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('Token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_missing_fiels(self):
        """Test that email and password are required"""
        res = self.client.post(TOKEN_URL, {'email': 'one', 'password': ''})

        self.assertNotIn('Token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
