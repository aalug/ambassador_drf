"""
Tests custom Django management commands.
"""
from unittest.mock import patch

from django.core.management import call_command
from django.test import SimpleTestCase, TestCase
from django.db.utils import OperationalError
from django.contrib.auth import get_user_model

from core.models import Product


@patch('core.management.commands.wait_for_db.Command.check')
class WaitForDbCommandTests(SimpleTestCase):
    """Tests for wait_for_db command."""

    def test_wait_for_db_ready(self, patched_check):
        """Test waiting for database if database ready."""
        patched_check.return_value = True
        call_command('wait_for_db')
        patched_check.assert_called_once_with(databases=['default'])

    @patch('time.sleep')
    def test_for_db_delay(self, patched_sleep, patched_check):
        """Test waiting for database when getting  OperationError"""
        patched_check.side_effect = [OperationalError] * 3 + [True]

        call_command('wait_for_db')

        self.assertEqual(patched_check.call_count, 4)
        patched_check.assert_called_with(databases=['default'])


class PopulateCommandsTests(TestCase):
    """Tests for populate commands."""

    def test_handle_creates_ambassadors(self):
        """Tests populate ambassadors."""

        # Ensure no ambassadors exist before running the command
        self.assertEqual(get_user_model().objects
                         .filter(is_ambassador=True).count(), 0)

        call_command('populate_ambassadors')

        # Check that 30 ambassadors have been created
        self.assertEqual(get_user_model().objects
                         .filter(is_ambassador=True).count(), 30)

    def test_handle_creates_products(self):
        """Tests populate products."""
        self.assertEqual(Product.objects.all().count(), 0)
        call_command('populate_products')
        self.assertEqual(Product.objects.all().count(), 30)
