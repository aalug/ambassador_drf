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
LOGOUT_URL = reverse('common:logout')
USER_URL = reverse('common:user')
PROFILE_URL = reverse('common:profile')
PASSWORD_URL = reverse('common:password')


def create_user(**params):
    """Create and return a new user."""
    return get_user_model().objects.create_user(**params)


def create_payload(create_confirm_pass, **params):
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
    if not create_confirm_pass:
        # Delete confirm_password, it is not needed in this case.
        del payload['confirm_password']

    return payload


class RegisterUserApiTests(TestCase):
    """Test registering a user through the API."""

    def setUp(self):
        self.client = APIClient()

    def test_create_user_success(self):
        """Test creating a user is successful."""
        payload = create_payload(create_confirm_pass=True)
        res = self.client.post(REGISTER_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(email=payload['email'])
        self.assertTrue(user.check_password(payload['password']))

        # Check that the API is secure and does not send password in plain text in response
        self.assertNotIn('password', res.data)

    def test_user_with_email_exists_error(self):
        """Test error returned if user with email exists."""
        payload = create_payload(create_confirm_pass=False)
        create_user(**payload)
        payload['confirm_password'] = payload['password']

        res = self.client.post(REGISTER_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short_error(self):
        """Test an error is returned if password less than 6 chars."""
        payload = create_payload(create_confirm_pass=True,
                                 password='12345',
                                 confirm_password='12345')
        res = self.client.post(REGISTER_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)

    def test_passwords_do_not_match_error(self):
        """Test an error is returned if passwords do not match."""
        payload = create_payload(create_confirm_pass=True,
                                 confirm_password='wrongPass')

        res = self.client.post(REGISTER_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)

    def test_admin_is_not_ambassador(self):
        """Test that new admin user is not an ambassador."""
        payload = create_payload(create_confirm_pass=True)
        res = self.client.post(REGISTER_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(email=payload['email'])
        self.assertFalse(user.is_ambassador)

    def test_register_only_post_allowed(self):
        """Test that only POST is allowed in register API."""
        r1 = self.client.get(REGISTER_URL)
        r2 = self.client.patch(REGISTER_URL, {}, format='json')
        r3 = self.client.put(REGISTER_URL, {}, format='json')
        r4 = self.client.delete(REGISTER_URL)

        self.assertEqual(r1.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(r2.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(r3.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(r4.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class LoginUserApiTests(TestCase):
    """Tests for login a user through the API."""

    def setUp(self):
        self.client = APIClient()
        payload = create_payload(create_confirm_pass=False)
        create_user(**payload)
        self.credentials = {
            'email': payload['email'],
            'password': payload['password']
        }

    def test_login_success(self):
        """Test that login is successful."""
        res = self.client.post(LOGIN_URL, self.credentials, format='json')

        user = get_user_model().objects.get(email=self.credentials['email'])
        self.assertTrue(user.check_password(self.credentials['password']))
        self.assertNotIn('password', res.data)

    def test_login_wrong_password_error(self):
        """Test login with wrong password raises error.."""
        self.credentials['password'] = 'wrongPassword'
        res = self.client.post(LOGIN_URL, self.credentials, format='json')

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_wrong_email_error(self):
        """Test login with wrong email raises error."""
        self.credentials['email'] = 'wrongEmail'
        res = self.client.post(LOGIN_URL, self.credentials, format='json')

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_password_or_email_not_provided_error(self):
        """Test an error is returned if password or email are not provided."""

        payload_1 = {'email': self.credentials['email'], 'password': ''}
        payload_2 = {'email': '', 'password': self.credentials['password']}

        res_1 = self.client.post(LOGIN_URL, payload_1, format='json')
        res_2 = self.client.post(LOGIN_URL, payload_2, format='json')

        self.assertEqual(res_1.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(res_2.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_only_post_allowed(self):
        """Test that only POST is allowed in login API."""
        r1 = self.client.get(LOGIN_URL)
        r2 = self.client.patch(LOGIN_URL, {}, format='json')
        r3 = self.client.put(LOGIN_URL, {}, format='json')
        r4 = self.client.delete(LOGIN_URL)

        self.assertEqual(r1.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(r2.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(r3.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(r4.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_jwt_auth(self):
        """Test JWT authentication."""
        res = self.client.post(LOGIN_URL, self.credentials, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('jwt', res.cookies)

    def test_jwt_auth_wrong_password_error(self):
        """Test JWT authentication with wrong password raises error."""
        self.credentials['password'] = 'wrongPassword'
        res = self.client.post(LOGIN_URL, self.credentials, format='json')

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotIn('jwt', res.cookies)

    def test_jwt_auth_wrong_email_error(self):
        """Test JWT authentication with wrong email raises error."""
        self.credentials['email'] = 'wrongEmail'
        res = self.client.post(LOGIN_URL, self.credentials, format='json')

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotIn('jwt', res.cookies)

    def test_jwt_auth_success(self):
        """Test JWT authentication with correct credentials is successful."""
        res = self.client.post(LOGIN_URL, self.credentials, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('jwt', res.cookies)


class PrivateUserApiTests(TestCase):
    """Test API requests that require authentication."""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(**create_payload(create_confirm_pass=False))
        self.client.force_authenticate(user=self.user)

    def test_get_user(self):
        """Test get user authenticated."""
        res = self.client.get(USER_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'id': self.user.id,
            'email': self.user.email,
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
            'is_ambassador': self.user.is_ambassador
        })

    def test_post_user_not_allowed(self):
        """Test POST is not allowed for the "user" endpoint."""
        res = self.client.post(USER_URL, {})

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_logout_user_success(self):
        """Test logout API."""
        res = self.client.post(LOGOUT_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        if 'jwt' in res.cookies:
            self.assertEqual(res.cookies.get('jwt').value, '')
        else:
            self.assertNotIn('jwt', res.cookies)

    def test_logout_only_post_allowed(self):
        """Test that only POST is allowed in logout API."""
        r1 = self.client.get(LOGOUT_URL)
        r2 = self.client.patch(LOGOUT_URL, {}, format='json')
        r3 = self.client.put(LOGOUT_URL, {}, format='json')
        r4 = self.client.delete(LOGOUT_URL)

        self.assertEqual(r1.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(r2.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(r3.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(r4.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_profile(self):
        """Test update profile API."""
        payload = {
            'first_name': 'New first name',
            'last_name': 'New last name'
        }
        res = self.client.put(PROFILE_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(self.user.first_name, payload['first_name'])
        self.assertEqual(self.user.last_name, payload['last_name'])

    def test_cant_update_password_via_update_profile(self):
        """Test that password cannot be updated vie the update profile API."""
        payload = {
            'password': 'New_password',
            'confirm_password': 'New_password'
        }
        res = self.client.put(PROFILE_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cant_update_profile_without_auth(self):
        """Test update profile API without authentication raises error."""
        self.client.logout()
        payload = {
            'first_name': 'New first name',
            'last_name': 'New last name'
        }
        res = self.client.put(PROFILE_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_profile_only_put_allowed(self):
        """Test that only PUT is allowed in update profile API."""
        r1 = self.client.get(PROFILE_URL)
        r2 = self.client.post(PROFILE_URL, {}, format='json')
        r3 = self.client.patch(PROFILE_URL, {}, format='json')
        r4 = self.client.delete(PROFILE_URL)

        self.assertEqual(r1.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(r2.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(r3.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(r4.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_password_success(self):
        """Test update password API."""
        payload = {
            'password': 'New_password',
            'confirm_password': 'New_password'
        }
        res = self.client.put(PASSWORD_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(self.user.check_password(payload['password']))

    def test_update_passwords_do_not_match_error(self):
        """Test update password, if password and confirm_password
           do not match raises error."""
        payload = {
            'password': 'New_password',
            'confirm_password': 'Wrong_password'
        }
        res = self.client.put(PASSWORD_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(self.user.check_password(payload['password']))
        self.assertFalse(self.user.check_password(payload['confirm_password']))

    def test_update_password_only_put_allowed(self):
        """Test that only PUT is allowed in update password API."""
        r1 = self.client.get(PASSWORD_URL)
        r2 = self.client.post(PASSWORD_URL, {}, format='json')
        r3 = self.client.patch(PASSWORD_URL, {}, format='json')
        r4 = self.client.delete(PASSWORD_URL)

        self.assertEqual(r1.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(r2.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(r3.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(r4.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)