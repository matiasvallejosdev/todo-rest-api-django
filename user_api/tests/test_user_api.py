"""
Test for user_api.
"""
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from django.contrib.auth import get_user_model

ME_URL = reverse('user_api:me')


class TestPublicUserAPI(TestCase):
    """User testing for public api views."""

    def setUp(self):
        """Setting up client for testing."""
        self.client = APIClient()


class TestPrivateUserAPI(TestCase):
    """User testing for private api views."""

    def setUp(self):
        """Setting up client and authenticate users."""
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email='test@example.com',
            password='testexample123',
            first_name='Test',
            last_name='Case'
        )
        self.client.force_authenticate(user=self.user)

    def test_user_me_post_not_allowed(self):
        """Test user me post is not allowed."""
        res = self.client.post(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_retrieve_user_profile_success(self):
        """Test retrieve user profile with credentials."""
        res = self.client.get(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['email'], self.user.email)
        self.assertEqual(res.data['first_name'], self.user.first_name)
        self.assertEqual(res.data['last_name'], self.user.last_name)
