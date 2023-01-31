"""
Django command to populate the database with products.
"""
from django.core.management import BaseCommand
from faker import Faker
from random import randrange
from core.models import Product


class Command(BaseCommand):
    """Django command to populate the database with ambassadors."""

    def handle(self, *args, **options):
        faker = Faker()

        for _ in range(30):
            Product.objects.create(
                title=faker.name(),
                description=faker.text(),
                image=faker.image_url(),
                price=randrange(10, 100),
            )
