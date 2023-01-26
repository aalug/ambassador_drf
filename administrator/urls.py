"""
URL mappings for administrator app.
"""
from django.urls import path, include

urlpatterns = [
    path('', include('common.urls')),
]

