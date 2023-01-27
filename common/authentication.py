import datetime
import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed


class JWTAuthentication(BaseAuthentication):
    """Class for handling JWT Authentication."""

    def authenticate(self, request):
        """Authenticates a user."""
        token = request.COOKIES.get('jwt')
        if not token:
            return None

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Signature expired.')

        user = get_user_model().objects.get(id=payload['user_id'])
        if user is None:
            raise AuthenticationFailed('User does not exist.')
        return user, None

    @staticmethod
    def generate_jwt(user_id):
        """Generates a JWT token for a given user."""
        payload = {
            'user_id': user_id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1),
            'iat': datetime.datetime.utcnow()
        }
        return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

