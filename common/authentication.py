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
        is_ambassador = 'api/ambassador/' in request.path

        token = request.COOKIES.get('jwt')
        if not token:
            return None

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Signature expired.')

        if ((is_ambassador and payload['scope'] != 'ambassador') or (
                is_ambassador is False and payload['scope'] != 'admin')):
            raise AuthenticationFailed('Invalid scope!')

        user = get_user_model().objects.get(id=payload['user_id'])
        if user is None:
            raise AuthenticationFailed('User does not exist.')
        return user, None

    @staticmethod
    def generate_jwt(user_id, scope):
        """Generates a JWT token for a given user."""
        payload = {
            'user_id': user_id,
            'scope': scope,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1),
            'iat': datetime.datetime.utcnow()
        }
        return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
