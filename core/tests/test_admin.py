"""
Tests for the Django admin modifications.
"""
from django.test import TestCase
from django.test import Client

from django.contrib.auth import get_user_model
from django.urls import reverse


def create_sample_user(**kwargs):
    payload = {
        'email': 'user@example.com',
        'password': 'testpass123',
        'first_name': 'User',
        'last_name': 'Test'
    }
    payload.update(**kwargs)
    return get_user_model().objects.create_superuser(**payload)


class TestAdmin(TestCase):
    """Test admin from core"""

    def setUp(self):
        """Client and data initialization"""
        self.client = Client()
        self.admin = get_user_model().objects.create_superuser(
            email="admin@example.com",
            password="testpass123"
        )
        self.client.force_login(user=self.admin)
        self.user = create_sample_user()

    def test_list_users_page(self):
        """Test that users are listed on page."""
        url = reverse('admin:core_user_changelist')
        res = self.client.get(url)
        self.assertContains(res, self.user.first_name)
        self.assertContains(res, self.user.last_name)
        self.assertContains(res, self.user.email)

    def test_edit_user_page(self):
        """Test editing user on page."""
        url = reverse('admin:core_user_change', args=[self.user.userId])
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)

    def test_create_user_page(self):
        url = reverse('admin:core_user_add')
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)
