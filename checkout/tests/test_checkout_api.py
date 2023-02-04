"""
Tests for the checkout API.
"""
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from core.models import Product, Link, Order, OrderItem

ORDERS_URL = reverse('checkout:orders')


def create_product(**params):
    """Create and return a new product."""
    details = {
        'title': 'test',
        'price': 10.00,
        'description': 'some details',
        'image': 'https://example.com/image.png'
    }
    details.update(params)
    return Product.objects.create(**details)


def get_links_url(code: str):
    """Create and return a links URL."""
    return reverse('checkout:links', args=[code])


class CheckoutAPITests(TestCase):
    """Tests for the checkout API."""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email='user@example.com',
            password='password'
        )
        self.client.force_authenticate(self.user)

    def test_fetching_links_success(self):
        """Test that fetching links works as expected."""
        link = Link.objects.create(
            user=self.user,
            code='abc123'
        )
        url = get_links_url(link.code)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('products', res.data)
        self.assertIn('user', res.data)
        self.assertIn('code', res.data)
        self.assertEqual(res.data['user']['email'], self.user.email)
        self.assertEqual(res.data['code'], link.code)

    def test_links_endpoint_only_get_allowed(self):
        """Test that for the links endpoint only get is allowed."""
        url = get_links_url('abc123')
        r1 = self.client.post(url, {})
        r2 = self.client.put(url, {})
        r3 = self.client.patch(url, {})
        r4 = self.client.delete(url)

        self.assertEqual(r1.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(r2.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(r3.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(r4.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_place_order_success(self):
        """Test placing an order is successful."""
        link = Link.objects.create(
            user=self.user,
            code='123456'
        )
        product = create_product(title='Product 1')

        data = {
            "code": "123456",
            "first_name": "John",
            "last_name": "Doe",
            "email": "johndoe@example.com",
            "address": "123 Main St",
            "country": "USA",
            "city": "New York",
            "zip_code": "10001",
            "products": [
                {
                    "product_id": product.id,
                    "quantity": 2.0
                }
            ]
        }
        res = self.client.post(ORDERS_URL, data, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        order = Order.objects.filter(code=data['code']).first()
        self.assertEqual(order.first_name, data['first_name'])
        self.assertEqual(order.last_name, data['last_name'])
        self.assertEqual(order.email, data['email'])
        self.assertEqual(order.address, data['address'])
        self.assertEqual(order.country, data['country'])
        self.assertEqual(order.city, data['city'])
        self.assertEqual(order.zip_code, data['zip_code'])

        order_item = OrderItem.objects.filter(order=order).first()
        self.assertEqual(order_item.product_title, product.title)
        self.assertEqual(order_item.price, 10.0)
        self.assertEqual(order_item.quantity, 2.0)
        self.assertEqual(order_item.ambassador_revenue, 2.0)
        self.assertEqual(order_item.admin_revenue, 18.0)

