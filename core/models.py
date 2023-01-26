"""
Database models for the project.
"""
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models


class UserManager(BaseUserManager):
    """Manager for user model."""

    def create_user(self, email, password, **extra_fields):
        """Create a new user."""
        if not email:
            raise ValueError('Users must have an email address')
        if len(password) < 6:
            raise ValueError('Password must be at least 6 characters')
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.is_staff = False
        user.is_superuser = False
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        """Create and return a new superuser."""
        if not email:
            raise ValueError('Users must have an email address')
        if len(password) < 6:
            raise ValueError('Password must be at least 6 characters')
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractUser):
    """User model."""
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    is_ambassador = models.BooleanField(default=True)
    username = None

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
