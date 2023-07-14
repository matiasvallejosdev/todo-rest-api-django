"""
Test for user_api.
"""
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from django.contrib.auth import get_user_model

CREATE_USER_URL = reverse('user_api:create')
CONNECTION_URL = reverse('auth_api:connection-verify')
ME_URL = reverse('user_api:me')


class TestPublicUserAPI(TestCase):
    """User testing for public api views."""

    def setUp(self):
        """Setting up client for testing."""
        self.client = APIClient()

    def test_create_user_success(self):
        """Test create user successfully with all parameters."""
        payload = {
            'email': 'test@example.com',
            'password': 'testexample123',
            'first_name': 'Test',
            'last_name': 'Case'
        }
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        exists = get_user_model().objects.filter(user_id=res.data['user_id']).exists()
        self.assertTrue(exists)
        user = get_user_model().objects.get(user_id=res.data['user_id'])
        self.assertEqual(res.data['email'], payload['email'])
        self.assertEqual(res.data['first_name'], payload['first_name'])
        self.assertEqual(res.data['last_name'], payload['last_name'])
        self.assertTrue(user.check_password(payload['password']))

    def test_create_user_email_normalized(self):
        """Test create user with a normalized email."""
        payload = {
            'email': 'test@NORMALIZED.COM',
            'password': 'testexample123',
        }
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data['email'], payload['email'].lower())

    def test_create_duplicated_user_email_exists(self):
        """Test create duplicated user that email exists with error."""
        payload = {
            'email': 'test@example.com',
            'password': 'testexample123',
        }
        get_user_model().objects.create_user(**payload)
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_password_user_too_short(self):
        """Test create password user too short with error."""
        payload = {
            'email': 'test@example.com',
            'password': 'test',  # min_length = 5
        }
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_invalid_user(self):
        """Test create invalid user with error."""
        payload = {}
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_connection_invalid_credentials(self):
        """Test connection invalid credentials."""
        token = ""
        res = self.client.post(CONNECTION_URL, Authorization=token)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('Authentication credentials were not provided.', res.data['detail'])

    def test_get_me_not_authorized(self):
        """Not authorized get for met because is not authenticated."""
        res = self.client.get(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


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

    def test_user_api_connection(self):
        """Test connection valid credentials."""
        res = self.client.post(CONNECTION_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_retrieve_user_profile_success(self):
        """Test retrieve user profile with credentials."""
        res = self.client.get(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['email'], self.user.email)
        self.assertEqual(res.data['first_name'], self.user.first_name)
        self.assertEqual(res.data['last_name'], self.user.last_name)

    def test_update_user_profile_success(self):
        """Test update user profile successfully."""
        payload = {
            'first_name': 'John',
            'last_name': 'Walker'
        }
        res = self.client.patch(ME_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.user = get_user_model().objects.get(pk=self.user.pk)
        self.assertEqual(self.user.first_name, payload['first_name'])
        self.assertEqual(self.user.last_name, payload['last_name'])

    def test_update_user_profile_only_own(self):
        """Test update only own profile."""
        payload = {
            'first_name': 'John',
            'last_name': 'Walker'
        }
        res = self.client.patch(ME_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_delete_user_profile_success(self):
        """Delete user own successfully."""
        res = self.client.delete(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
