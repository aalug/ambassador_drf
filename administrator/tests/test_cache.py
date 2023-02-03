"""
Test cache in administrator app.
"""
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.core.cache import cache
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from core.models import Product

PRODUCTS_URL = reverse('products')


def get_product_url(pk: int):
    """Return the URL for a specific product."""
    return reverse('product', args=[pk])


def create_product(**params):
    """Create and return a new product."""
    details = {
        'title': 'Test product',
        'price': 10.00,
        'description': 'Product description',
        'image': 'https://example.com/image.png'
    }
    details.update(params)
    return Product.objects.create(**details)


class CacheTests(TestCase):
    """Test cache."""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create(
            email='user@example.com',
            password='password'
        )
        self.client.force_authenticate(self.user)
        self.product1 = create_product(title='product1')
        self.product2 = create_product(title='product2')

    def test_delete_cache_on_create(self):
        """Test that cache will be deleted after creating a product."""
        details = {
            'title': 'product3',
            'price': 14.00,
            'description': 'Product description',
            'image': 'https://example.com/image.png'
        }
        res = self.client.post(PRODUCTS_URL, details)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertFalse(cache.get('products_frontend'))
        self.assertFalse(cache.get('products_backend'))

    def test_delete_cache_on_update(self):
        """Test that cache will be deleted after updating a product."""
        url = get_product_url(self.product1.id)
        res = self.client.put(url, {'price': 20.50})

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertFalse(cache.get('products_frontend'))
        self.assertFalse(cache.get('products_backend'))

    def test_delete_cache_on_delete(self):
        """Test that cache will be deleted after deleting a product."""
        url = get_product_url(self.product2.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(cache.get('products_frontend'))
        self.assertFalse(cache.get('products_backend'))
