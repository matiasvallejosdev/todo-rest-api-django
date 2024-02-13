from django.test import SimpleTestCase
from core.utils import check_email


class TestUtils(SimpleTestCase):
    """Test utils module"""
    def test_valid_email(self):
        """Test if an email is valid"""
        self.assertTrue(check_email('test@example.com'))
        self.assertTrue(check_email('test_valid@example.com'))

    def test_invalid_email(self):
        """Test if an email is invalid"""
        sample_exception = [
            '',
            '@',
            'mati@',
            'mati@.com',
            '@example.com'
        ]
        for email in sample_exception:
            self.assertFalse(check_email(email))
