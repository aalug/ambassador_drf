"""
Tests for the JWT authentication.
"""
import jwt

from django.conf import settings
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIRequestFactory
from rest_framework.exceptions import AuthenticationFailed

from common.authentication import JWTAuthentication

LOGIN_URL = reverse('common:login')


class JWTAuthenticationTests(TestCase):
    """Tests for the JWTAuthentication class."""

    def setUp(self):
        self.factory = APIRequestFactory()
        self.authentication = JWTAuthentication()
        self.user = get_user_model().objects.create_user(
            email='user@example.com',
            password='password123',
            first_name='Test',
            last_name='User',
            is_ambassador=False
        )
        self.ambassador = get_user_model().objects.create_user(
            email='ambassador@example.com',
            password='password123',
            first_name='Ambassador',
            last_name='User',
            is_ambassador=True
        )

    def test_authenticate_with_valid_token(self):
        """Test authentication with valid token (admin scope)."""
        token = jwt.encode({'user_id': self.user.id, 'scope': 'admin'}, settings.SECRET_KEY, algorithm='HS256')
        request = self.factory.get('/', HTTP_COOKIE=f'jwt={token}')
        user, _ = self.authentication.authenticate(request)

        self.assertEqual(user, self.user)

    def test_authenticate_with_invalid_token_error(self):
        """Test authentication with invalid token raises error (admin scope)."""
        token = jwt.encode({'user_id': self.user.id, 'scope': 'admin'}, 'wrong_secret_key', algorithm='HS256')
        request = self.factory.get('/', HTTP_COOKIE=f'jwt={token}')

        self.assertRaises(jwt.exceptions.InvalidSignatureError, self.authentication.authenticate, request)

    def test_auth_with_nonexistent_user_error(self):
        """Test authentication with nonexistent user raises error (admin scope)."""
        payload = {'user_id': 999, 'scope': 'admin'}
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
        request = self.factory.get('/', HTTP_COOKIE=f'jwt={token}')
        self.assertRaises((AuthenticationFailed, get_user_model().DoesNotExist),
                          self.authentication.authenticate,
                          request)

    def test_authenticate_with_invalid_token_error_ambassador(self):
        """Test authentication with invalid token raises error (ambassador scope)."""
        self.user.is_ambassador = True
        token = jwt.encode({'user_id': self.ambassador.id, 'scope': 'ambassador'}, 'wrong_secret_key', algorithm='HS256')
        request = self.factory.get('/', HTTP_COOKIE=f'jwt={token}')

        self.assertRaises(jwt.exceptions.InvalidSignatureError, self.authentication.authenticate, request)

    def test_auth_with_nonexistent_user_error_ambassador(self):
        """Test authentication with nonexistent user raises error (ambassador scope)."""
        self.user.is_ambassador = True
        payload = {'user_id': 999, 'scope': 'ambassador'}
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
        request = self.factory.get('/', HTTP_COOKIE=f'jwt={token}')
        self.assertRaises((AuthenticationFailed, get_user_model().DoesNotExist),
                          self.authentication.authenticate,
                          request)

    def test_authentication_with_invalid_scope(self):
        """Test authentication with invalid scope."""
        token = jwt.encode({'user_id': self.user.id, 'scope': 'invalid'}, settings.SECRET_KEY, algorithm='HS256')
        request = self.factory.get('/', HTTP_COOKIE=f'jwt={token}')

        self.assertRaises(AuthenticationFailed, self.authentication.authenticate, request)
