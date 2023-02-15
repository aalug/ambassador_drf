"""
Tests for the administrator app.
"""
from _decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from core.models import Product, Link, Order

AMBASSADORS_URL = reverse('ambassadors')
PRODUCTS_URL = reverse('products')
ORDERS_URL = reverse('orders')


def get_product_url(pk: int):
    """Return the URL for a specific product."""
    return reverse('product', args=[pk])


def get_links_url(pk: int):
    """Return the URL for a specific link."""
    return reverse('links', args=[pk])


def create_user(**params):
    """Create and return a new user."""
    details = {
        'first_name': 'Test',
        'last_name': 'User',
        'email': 'amb@example.com',
        'password': 'password123',
        'is_ambassador': True
    }
    details.update(params)
    return get_user_model().objects.create(**details)


def create_product(**params):
    """Create and return a new product."""
    details = {
        'title': 'Test product',
        'price': Decimal('10.00'),
        'description': 'Product description',
        'image': 'https://example.com/image.png'
    }
    details.update(params)
    return Product.objects.create(**details)


class ApiTests(TestCase):
    """Tests for the administrator app."""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_superuser(
            email='user@example.com',
            password='password123',
        )
        self.client.force_authenticate(user=self.user)

    def test_ambassador_api_needs_auth(self):
        """Test that the Ambassador API requires authentication."""
        res_success = self.client.get(AMBASSADORS_URL)

        self.client.logout()
        res_failure = self.client.get(AMBASSADORS_URL)

        self.assertEqual(res_success.status_code, status.HTTP_200_OK)
        self.assertEqual(res_failure.status_code, status.HTTP_403_FORBIDDEN)

    def test_ambassadors_endpoint_returns_only_ambassadors(self):
        """Test that the Ambassador API returns ambassadors."""
        ambassador = create_user()
        create_user(is_ambassador=False, email='non-amb@example.com')

        res = self.client.get(AMBASSADORS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['id'], ambassador.id)

    def test_ambassadors_endpoint_ony_get_allowed(self):
        """test that only GET method is allowed in ambassadors endpoint."""
        r1 = self.client.get(AMBASSADORS_URL)
        r2 = self.client.post(AMBASSADORS_URL, {}, format='json')
        r3 = self.client.put(AMBASSADORS_URL, {}, format='json')
        r4 = self.client.patch(AMBASSADORS_URL, {}, format='json')
        r5 = self.client.delete(AMBASSADORS_URL)

        self.assertEqual(r1.status_code, status.HTTP_200_OK)
        self.assertEqual(r2.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(r3.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(r4.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(r5.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_retrieve_products_success(self):
        """Test retrieving products is successful."""
        product = create_product()
        res = self.client.get(PRODUCTS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['title'], product.title)

    def test_products_endpoint_requires_auth(self):
        """Test that the Products endpoints requires authentication."""
        product = create_product()
        products_pk_url = get_product_url(product.id)
        self.client.logout()
        r1 = self.client.get(PRODUCTS_URL)
        r2 = self.client.post(PRODUCTS_URL, {}, format='json')
        r3 = self.client.put(products_pk_url, {}, format='json')
        r4 = self.client.delete(products_pk_url)

        self.assertEqual(r1.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(r2.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(r3.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(r4.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_products_success(self):
        """Test retrieving product is successful."""
        product = create_product()
        product_url = get_product_url(product.id)
        res = self.client.get(product_url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['id'], product.id)

    def test_create_product_success(self):
        """Test creating a new product is successful."""
        payload = {
            'title': 'Test Product',
            'price': Decimal('2.50'),
            'description': 'Test Product Description'
        }
        res = self.client.post(PRODUCTS_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        product_exists = Product.objects.filter(title=payload['title']).exists()
        self.assertTrue(product_exists)

    def test_update_product_success(self):
        """Test updating a product is successful."""
        title = 'Old title'
        product = create_product(title=title)
        product_pk_url = get_product_url(product.id)
        payload = {'title': 'New title'}

        self.assertEqual(product.title, title)

        res = self.client.put(product_pk_url, payload, format='json')
        product.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['title'], payload['title'])
        self.assertEqual(product.title, payload['title'])

    def test_delete_product_success(self):
        """Test deleting a product is successful."""
        product = create_product()
        product_exists = Product.objects.filter(id=product.id).exists()

        self.assertTrue(product_exists)

        product_url = get_product_url(product.id)

        res = self.client.delete(product_url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        product_exist = Product.objects.filter(id=product.id).exists()
        self.assertFalse(product_exist)

    def test_retrieve_links(self):
        """Test retrieving links is successful."""
        link = Link.objects.create(
            code='test',
            user=self.user
        )
        link.products.add(create_product())
        res = self.client.get(get_links_url(self.user.id))

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(Link.objects.all().count(), 1)
        self.assertEqual(res.data[0]['id'], link.id)

    def test_retrieve_orders(self):
        """Test retrieving orders is successful."""
        order = Order.objects.create(
            transaction_id='asdqwe',
            user=self.user,
            code='abc123',
            ambassador_email='ambs@example.com',
            first_name='First',
            last_name='Last',
            email='email@example.com',
            address='some address 12',
            city='New York',
            country='USA',
            zip_code='10001',
            complete=True
        )
        res = self.client.get(ORDERS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(Order.objects.all().count(), 1)
        self.assertEqual(res.data[0]['id'], order.id)
        self.assertEqual(res.data[0]['user'], self.user.id)
        self.assertEqual(res.data[0]['transaction_id'], order.transaction_id)
        self.assertEqual(res.data[0]['code'], order.code)
        self.assertEqual(res.data[0]['email'], order.email)
        self.assertEqual(res.data[0]['address'], order.address)
        self.assertEqual(res.data[0]['ambassador_email'], order.ambassador_email)
