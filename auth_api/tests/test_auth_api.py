from rest_framework.test import APIClient
from rest_framework import status

from django.urls import reverse
from django.test import TestCase

from django.contrib.auth import get_user_model

CONNECTION_URL = reverse("auth_api:connection-verify")


class TestPublicAuthAPI(TestCase):
    """Auth testing for public api views."""

    def setUp(self):
        """Setting up client for testing."""
        self.client = APIClient()

    def test_unauthenticated_connection_error(self):
        """Test unautehnticated connection error."""
        res = self.client.post(CONNECTION_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class TestPrivateAuthAPI(TestCase):
    """Auth testing for private api views."""

    def setUp(self):
        """Setting up client for testing."""
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="matias@email.com", password="pass12345"
        )
        self.client.force_authenticate(user=self.user)

    def test_authenticated_connection_success(self):
        """Test authenticated connection success."""
        res = self.client.post(CONNECTION_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {"message": "Connection successfully!"})
