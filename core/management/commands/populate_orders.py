"""
Django command to populate the database with ambassadors.
"""
from random import randrange

from django.contrib.auth import get_user_model
from django.core.management import BaseCommand

from faker import Faker

from core.models import Order, OrderItem


class Command(BaseCommand):
    """Django command to populate the database with orders."""

    def handle(self, *args, **options):
        faker = Faker()
        user = get_user_model().objects.create_user(
            email=faker.email(),
            password=faker.password()
        )

        for _ in range(3):
            order = Order.objects.create(
                user_id=user.id,
                code='code',
                ambassador_email='amb@example.com',
                first_name=faker.first_name(),
                last_name=faker.last_name(),
                email=faker.email(),
                complete=True
            )

            for i in range(randrange(1, 5)):
                price = randrange(10, 100)
                quantity = randrange(1, 5)
                OrderItem.objects.create(
                    order_id=order.id,
                    product_title=faker.name(),
                    price=price,
                    quantity=quantity,
                    admin_revenue=.9 * price * quantity,
                    ambassador_revenue=.1 * price * quantity
                )
