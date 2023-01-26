"""
Test fpr models.
"""
from django.contrib.auth import get_user_model
from django.test import TestCase


class ModelTest(TestCase):
    """Test models."""

    def test_create_user_with_email_successful(self):
        """Test creating a user with an email is successful."""
        email = 'user@example.com'
        password = 'password123'
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test email is normalized for new users."""
        sample_emails = [
            ['test1@EXAMPLE.com', 'test1@example.com'],
            ['Test2@Example.com', 'Test2@example.com'],
            ['TEST3@EXAMPLE.COM', 'TEST3@example.com'],
            ['test4@example.COM', 'test4@example.com']
        ]
        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(email, 'password123')
            self.assertEqual(user.email, expected)

    def test_new_user_without_email_raise_error(self):
        """Test that creating a user without an email raises a ValueError."""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('', 'password123')

    def test_new_user_with_too_short_password_raise_error(self):
        """Test that creating a user without a password raises a ValueError."""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('user@example.com', 'test1')

    def test_new_user_with_6_chars_password_success(self):
        """Test that creating a user with a password 6 characters
           does not raise a ValueError."""
        get_user_model().objects.create_user(
            'user@example.com',
            'test12'
        )
        self.assertEqual(get_user_model().objects.count(), 1)

    def test_create_superuser(self):
        """Test creating a superuser."""
        user = get_user_model().objects.create_superuser(
            email='superuser@example.com',
            password='admin123'
        )
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_user_xtra_fields(self):
        """Test creating user with extra fields."""
        user_details = {
            'email': 'user@example.com',
            'password': 'password123',
            'first_name': 'First',
            'last_name': 'Last'
        }

        user = get_user_model().objects.create_user(**user_details)

        self.assertEqual(user.first_name, user_details['first_name'])
        self.assertEqual(user.last_name, user_details['last_name'])
