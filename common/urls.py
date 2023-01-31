"""
URL mappings for common app.
It is the part that is shared by both administrator and ambassador app.
"""
from django.urls import path
from .views import (RegisterAPIView,
                    LoginAPIView,
                    UserAPIView,
                    LogoutAPIView,
                    UpdateProfileInfoAPIView,
                    UpdatePasswordAPIView)

app_name = 'common'

urlpatterns = [
    path('register/', RegisterAPIView.as_view(), name='register'),
    path('login/', LoginAPIView.as_view(), name='login'),
    path('logout/', LogoutAPIView.as_view(), name='logout'),
    path('user/', UserAPIView.as_view(), name='user'),
    path('user/info/', UpdateProfileInfoAPIView.as_view(), name='profile'),
    path('user/password/', UpdatePasswordAPIView.as_view(), name='password'),
]

