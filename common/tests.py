"""
Tests for the common app.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

REGISTER_URL = reverse('common:register')
LOGIN_URL = reverse('common:login')


def create_user(**params):
    """Create and return a new user."""
    return get_user_model().objects.create_user(**params)


def create_payload(**params):
    """Create and return a new payload."""
    password = 'password123'
    payload = {
        'email': 'test11@example.com',
        'password': password,
        'confirm_password': password,
        'first_name': 'Test',
        'last_name': 'User'
    }
    payload.update(params)
    return payload


class PublicUserApiTests(TestCase):
    """Test the public (that do not require authentication)
       features of the user API."""

    def setUp(self):
        self.client = APIClient()

    def test_create_user_success(self):
        """Test creating a user is successful."""
        payload = create_payload(email='dycjh@example.com',)
        res = self.client.post(REGISTER_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(email=payload['email'])
        self.assertTrue(user.check_password(payload['password']))

        # Check that the API is secure and does not send password in plain text in response
        self.assertNotIn('password', res.data)

    def test_user_with_email_exists_error(self):
        """Test error returned if user with email exists."""
        payload = create_payload(email='test1@example.com')
        del payload['confirm_password']
        create_user(**payload)
        payload['confirm_password'] = 'password123'

        res = self.client.post(REGISTER_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short_error(self):
        """Test an error is returned if password less than 5 chars."""
        payload = create_payload(password='12345', confirm_password='12345')
        res = self.client.post(REGISTER_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)

    def test_passwords_do_not_match_error(self):
        """Test an error is returned if passwords do not match."""
        payload = create_payload(password='password', confirm_password='wrongPass')

        res = self.client.post(REGISTER_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)

    def test_admin_is_not_ambassador(self):
        """Test that new admin user is not an ambassador."""
        payload = create_payload()
        res = self.client.post(REGISTER_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(email=payload['email'])
        self.assertFalse(user.is_ambassador)

    def test_login(self):
        """Test that login is successful."""
        payload = create_payload()
        # Delete confirm_password, it is not needed in creating a user this way
        del payload['confirm_password']
        create_user(**payload)
        credentials = {
            'email': payload['email'],
            'password': payload['password']
        }
        res = self.client.post(LOGIN_URL, credentials, format='json')

        user = get_user_model().objects.get(email=payload['email'])
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_login_wrong_password_error(self):
        """Test login with wrong password raises error.."""
        payload = create_payload()
        # Delete confirm_password, it is not needed in creating a user this way
        del payload['confirm_password']
        create_user(**payload)
        credentials = {
            'email': payload['email'],
            'password': 'wrongPassword'
        }
        res = self.client.post(LOGIN_URL, credentials, format='json')

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_login_wrong_email_error(self):
        """Test login with wrong email raises error."""
        payload = create_payload()
        del payload['confirm_password']
        create_user(**payload)
        credentials = {
            'email': 'wrongEmail',
            'password': payload['password']
        }
        res = self.client.post(LOGIN_URL, credentials, format='json')

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_password_or_email_not_provided_error(self):
        """Test an error is returned if password or email is not provided."""
        data = create_payload()
        del data['confirm_password']
        create_user(**data)

        payload_1 = {'email': data['email'], 'password': ''}
        payload_2 = {'email': '', 'password': data['password']}

        res_1 = self.client.post(LOGIN_URL, payload_1, format='json')
        res_2 = self.client.post(LOGIN_URL, payload_2, format='json')

        self.assertEqual(res_1.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(res_2.status_code, status.HTTP_403_FORBIDDEN)
