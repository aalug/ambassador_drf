"""
URL mappings for common app.
It is the part that is shared by both administrator and ambassador app.
"""
from django.urls import path
from .views import RegisterAPIView, LoginAPIView

app_name = 'common'

urlpatterns = [
    path('register/', RegisterAPIView.as_view(), name='register'),
    path('login/', LoginAPIView.as_view(), name='login'),
]

