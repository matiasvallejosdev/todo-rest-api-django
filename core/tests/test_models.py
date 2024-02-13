from django.test import TestCase
from django.contrib.auth import get_user_model


class TestModels(TestCase):
    """Test models"""

    def test_create_user_with_email_successfully(self):
        """Test creating user with email successfully"""
        email = 'test@example.com'
        password = '1a9r86'
        user = get_user_model().objects.create_user(email=email, password=password)

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_normalize_user_email(self):
        """Test normalize emails"""
        sample_emails = [
            ['test1@EXAMPLE.COM', 'test1@example.com'],
            ['Test2@example.com', 'test2@example.com'],
            ['test_3@example.com', 'test_3@example.com'],
            ['test4@EXample.COM', 'test4@example.com'],
        ]
        password = '1a9r86'
        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(email=email, password=password)
            self.assertEqual(user.email, expected)

    def test_new_user_invalid_email(self):
        """Test invalid or empty email raises error"""
        sample_exception = [
            '',
            '@',
            'mati@',
            'mati@.com',
            '@example.com'
        ]
        password = '1a9r86'
        for email in sample_exception:
            with self.assertRaises(ValueError):
                get_user_model().objects.create_user(email=email, password=password)

    def test_create_user_without_username(self):
        """Test creating user without username successfully instancing new random username"""
        sample_emails = [
            ['test1@EXAMPLE.COM', 'test1@example.com'],
            ['Test2@example.com', 'test2@example.com'],
            ['test_3@example.com', 'test_3@example.com'],
            ['test4@EXample.COM', 'test4@example.com'],
        ]
        password = '1a9r86'
        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(email=email, password=password)
            self.assertIsNotNone(user.username)

    def test_create_superuser(self):
        """Test create superuser with password"""
        email = 'test@example.com'
        password = 'test1954'
        user = get_user_model().objects.create_superuser(email=email, password=password)

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
