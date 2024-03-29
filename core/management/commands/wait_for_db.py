"""
Django command to wait for the database to be available
"""
from django.core.management import BaseCommand
import time
from django.db.utils import OperationalError


class Command(BaseCommand):
    """Django command to wait for the database"""

    def handle(self, *args, **options):
        """Entrypoint for command."""
        self.stdout.write('waiting for the database...')
        db_up = False
        while db_up is False:
            try:
                self.check(databases=['default'])
                db_up = True
            except OperationalError:
                self.stdout.write(' Database unavailable, waiting 1s...')
                time.sleep(1)

        self.stdout.write(self.style.SUCCESS('Database available!'))
