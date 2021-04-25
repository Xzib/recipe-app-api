from django.test import TestCase
from django.contrib.auth import get_user_model


class ModelTests(TestCase):
    def test_create_user_with_email_successfull(self):
        email = "test@abc.com"
        password = 'Testpass123'
        user =get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        email = 'test@ABC.COM'
        user = get_user_model().objects.create_user(email, 'Testpass123')

        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        """Test creating user with no email raise error"""
        with self.assertRaises(ValueError):
            user = get_user_model().objects.create_user(None,"Testpass123")

    def test_create_new_superuser(self):
        """Test for creating a new superuser"""
        user = get_user_model().objects.create_superuser(
            'supertest@abc.com',
            'test@123'
        )
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)