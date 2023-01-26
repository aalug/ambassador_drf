from django.contrib.auth import get_user_model
from rest_framework import exceptions, status, generics
from rest_framework.response import Response
from rest_framework.views import APIView

from common.serializers import UserSerializer


class RegisterAPIView(APIView):
    """API view for registering users."""
    serializer_class = UserSerializer

    def post(self, request):
        """Register a new user."""
        data = request.data

        if data['password'] != data['confirm_password']:
            raise exceptions.ValidationError('Passwords do not match.')

        data['is_ambassador'] = 0

        serializer = self.serializer_class(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginAPIView(APIView):
    """API view for logging in users."""
    serializer_class = UserSerializer

    def post(self, request):
        """Login a user."""
        email = request.data['email']
        password = request.data['password']

        if not email or not password:
            raise exceptions.AuthenticationFailed('Provide both email and password.')

        user = get_user_model().objects.filter(email=email).first()
        if user is None:
            raise exceptions.AuthenticationFailed('User not found.')
        if not user.check_password(password):
            raise exceptions.AuthenticationFailed('Password is incorrect.')

        return Response(self.serializer_class(user).data, status=status.HTTP_200_OK)
