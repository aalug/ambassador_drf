"""
Tests for the JWT authentication.
"""
import datetime

from unittest.mock import patch

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
            last_name='User'
        )

    def test_authenticate_with_valid_token(self):
        token = jwt.encode({'user_id': self.user.id}, settings.SECRET_KEY, algorithm='HS256')
        request = self.factory.get('/', HTTP_COOKIE=f'jwt={token}')
        user, _ = self.authentication.authenticate(request)

        self.assertEqual(user, self.user)

    def test_authenticate_with_invalid_token(self):
        token = jwt.encode({'user_id': self.user.id}, 'wrong_secret_key', algorithm='HS256')
        request = self.factory.get('/', HTTP_COOKIE=f'jwt={token}')

        self.assertRaises(jwt.exceptions.InvalidSignatureError, self.authentication.authenticate, request)

    def test_authenticate_with_nonexistent_user(self):
        payload = {'user_id': 999}
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
        request = self.factory.get('/', HTTP_COOKIE=f'jwt={token}')
        self.assertRaises((AuthenticationFailed, get_user_model().DoesNotExist),
                          self.authentication.authenticate,
                          request)

    def test_authenticate_with_no_token(self):
        request = self.factory.get('/')
        self.assertIsNone(self.authentication.authenticate(request))
