"""
Database models for the project.
"""
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """User model."""
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    is_ambassador = models.BooleanField(default=True)
    username = None

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
