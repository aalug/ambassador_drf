"""
Django command to populate the database with ambassadors.
"""
from django.contrib.auth import get_user_model
from django.core.management import BaseCommand

from faker import Faker


class Command(BaseCommand):
    """Django command to populate the database with ambassadors."""

    def handle(self, *args, **options):
        faker = Faker()

        for _ in range(30):
            user = get_user_model().objects.create(
                first_name=faker.first_name(),
                last_name=faker.last_name(),
                email=faker.email(),
                password='',
                is_ambassador=True
            )
            user.set_password('123456')
            user.save()
