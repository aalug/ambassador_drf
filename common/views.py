from django.contrib.auth import get_user_model
from rest_framework import exceptions, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from common.authentication import JWTAuthentication
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

        token = JWTAuthentication.generate_jwt(user.id)

        response = Response()
        response.set_cookie(key='jwt', value=token, httponly=True)
        response.data = {'message': 'Login successful.'}
        response.status_code = status.HTTP_200_OK

        return response


class UserAPIView(APIView):
    """API view for retrieving users.."""
    serializer_class = UserSerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        """Retrieve a user."""
        serializer = self.serializer_class(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class LogoutAPIView(APIView):
    """API view for logging out users."""
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        """Logout a user."""
        response = Response()
        response.delete_cookie(key='jwt')
        response.data = {'message': 'Logout successful.'}
        response.status_code = status.HTTP_200_OK
        return response


class UpdateProfileInfoAPIView(APIView):
    """API view for managing profile information."""
    serializer_class = UserSerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def put(self, request, pk=None):
        """Retrieve profile information."""
        data = request.data
        if 'password' in data or 'confirm_password' in data:
            raise exceptions.ValidationError('Password update not allowed via this endpoint.')

        user = request.user
        serializer = self.serializer_class(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)


class UpdatePasswordAPIView(APIView):
    """API view for updating passwords."""
    serializer_class = UserSerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def put(self, request, pk=None):
        """Retrieve profile information."""
        user = request.user
        data = request.data

        if data['password'] != data['confirm_password']:
            raise exceptions.ValidationError('Passwords do not match.')

        user.set_password(data['password'])
        user.save()
        return Response(self.serializer_class(user).data, status=status.HTTP_200_OK)
