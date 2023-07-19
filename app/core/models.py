"""
Core models
"""
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from .utils import check_email
from uuid import uuid4





class UserManager(BaseUserManager):
    """Users manager to create user and superuser."""

    def create_user(self, email, password=None, **kwargs):
        """Create new user."""
        payload = {
            'username': self.create_random_username()
        }

        if not email:
            raise ValueError('Email must be provided')
        else:
            email = str(email).lower()
            if check_email(email) is False:
                raise ValueError('Email must be in the correct format')

        payload.update(kwargs)

        user = self.model(email=self.normalize_email(email), **payload)
        user.set_password(password)
        user.save(using=self.db)
        return user

    def create_superuser(self, email, password, **kwargs):
        """Using create_user method to create a superuser."""
        user = self.create_user(email, password, **kwargs)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self.db)
        return user


    def create_random_username(self):
        """Create random username."""
        return uuid4().hex[:30]

class User(AbstractBaseUser, PermissionsMixin):
    """Users in system."""
    id = None  # Set id field to None
    user_id = models.UUIDField(max_length=16, primary_key=True, default=uuid4, editable=False)
    email = models.EmailField(max_length=255, unique=True, null=False, blank=False)
    username = models.CharField(max_length=45, blank=False, null=False, unique=True)
    password = models.CharField(max_length=255)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    created_on = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return self.email
