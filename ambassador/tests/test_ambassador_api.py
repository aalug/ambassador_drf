"""
Tests for the ambassador app.
"""
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from core.models import Product, Link

PRODUCTS_FRONTEND_URL = reverse('ambassador:products-frontend')
PRODUCTS_BACKEND_URL = reverse('ambassador:products-backend')
LINKS_URL = reverse('ambassador:links')
STATS_URL = reverse('ambassador:stats')
RANKINGS_URL = reverse('ambassador:rankings')


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


class PublicAmbassadorApiTests(TestCase):
    """Tests for the public endpoints of ambassador API."""

    def setUp(self):
        self.client = APIClient()
        create_product(title='product',
                       description='description',
                       price=10.00),
        create_product(title='something', price=20.00),
        create_product(title='something else', price=30.00)

    def test_get_products(self):
        """Test getting all products."""
        res = self.client.get(PRODUCTS_BACKEND_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data['data']), 3)

    def test_search_products(self):
        """Test search feature."""
        responses = [
            self.client.get(f'{PRODUCTS_BACKEND_URL}?search=product'),
            self.client.get(f'{PRODUCTS_BACKEND_URL}?search=PRODUCT'),
            self.client.get(f'{PRODUCTS_BACKEND_URL}?search=descrip')
        ]
        for res in responses:
            self.assertEqual(res.status_code, status.HTTP_200_OK)
            self.assertEqual(len(res.data['data']), 1)
            self.assertEqual(res.data['data'][0]['title'], 'product')

    def test_sort_products_by_price_ascending(self):
        """Test sorting by price in ascending order."""
        res = self.client.get(f'{PRODUCTS_BACKEND_URL}?sort=price-asc')
        price_1 = res.data['data'][0]['price']
        price_2 = res.data['data'][1]['price']
        price_3 = res.data['data'][2]['price']

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(price_1 < price_2)
        self.assertTrue(price_2 < price_3)

    def test_sort_products_by_price_descending(self):
        """Test sorting by price in descending order."""
        res = self.client.get(f'{PRODUCTS_BACKEND_URL}?sort=price-desc')
        price_1 = res.data['data'][0]['price']
        price_2 = res.data['data'][1]['price']
        price_3 = res.data['data'][2]['price']

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(price_1 > price_2)
        self.assertTrue(price_2 > price_3)

    def test_sort_products_by_title_ascending(self):
        """Test sorting by title in ascending order."""
        res = self.client.get(f'{PRODUCTS_BACKEND_URL}?sort=title-asc')
        title_1 = res.data['data'][0]['title']
        title_2 = res.data['data'][1]['title']
        title_3 = res.data['data'][2]['title']

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(title_1 < title_2)
        self.assertTrue(title_2 < title_3)

    def test_sort_products_by_title_descending(self):
        """Test sorting by title in descending order."""
        res = self.client.get(f'{PRODUCTS_BACKEND_URL}?sort=title-desc')
        title_1 = res.data['data'][0]['title']
        title_2 = res.data['data'][1]['title']
        title_3 = res.data['data'][2]['title']

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(title_1 > title_2)
        self.assertTrue(title_2 > title_3)


class PrivateAmbassadorApiTests(TestCase):
    """Tests for the private endpoints of ambassador API."""
    def setUp(self):
        self.client = APIClient()
        self.ambassador = get_user_model().objects.create_user(
            email='ambassador@example.com',
            password='password'
        )
        self.client.force_authenticate(self.ambassador)
        self.product = create_product(title='Product 1')

    def test_create_link_success(self):
        """Test creating Link is successful."""
        product2 = create_product(title='Product 2')
        payload = {
            'products': [self.product.id, product2.id]
        }
        res = self.client.post(LINKS_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data['products']), 2)
        self.assertEqual(Link.objects.all().count(), 1)

    def test_create_link_requires_auth(self):
        """Test that creating Link requires authentication."""
        self.client.logout()
        res = self.client.post(LINKS_URL, {}, format='json')

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_link_with_wrong_product(self):
        """Test creating a link with product that does not exist."""
        payload = {
            'products': [999, 9999]
        }
        res = self.client.post(LINKS_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_link_only_post_allowed(self):
        """Test that only POST methods are allowed for this endpoint."""
        r1 = self.client.get(LINKS_URL)
        r2 = self.client.put(LINKS_URL)
        r3 = self.client.patch(LINKS_URL)
        r4 = self.client.delete(LINKS_URL)

        self.assertEqual(r1.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(r2.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(r3.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(r4.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_get_stats(self):
        """Test getting stats, code, count and revenue."""
        payload = {
            'products': [self.product.id]
        }
        link_res = self.client.post(LINKS_URL, payload, format='json')
        link_coed = link_res.data['code']

        res = self.client.get(STATS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('code', res.data[0])
        self.assertIn('count', res.data[0])
        self.assertIn('revenue', res.data[0])
        self.assertEqual(link_coed, res.data[0]['code'])

    def test_stats_only_get_allowed(self):
        """Test that only GET method is allowed for this endpoint."""
        r1 = self.client.post(STATS_URL, {})
        r2 = self.client.put(STATS_URL, {})
        r3 = self.client.patch(STATS_URL, {})
        r4 = self.client.delete(STATS_URL)

        self.assertEqual(r1.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(r2.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(r3.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(r4.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_create_user_is_ambassador_true(self):
        """Test that creating a user via ambassador app will set
           user.is_ambassador to True."""
        payload = {
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'ambassadoar@example.com',
            'password': 'password123',
            'confirm_password': 'password123'
        }
        res = self.client.post('/api/ambassador/register/', payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(res.data['is_ambassador'])

    def test_only_ambassador_can_login_via_ambassador(self):
        """Test that user that is not an ambassador cannot log in via this endpoint."""
        not_ambassador = get_user_model().objects.create(
            first_name='Not',
            last_name='Ambassador',
            email='not_ambassador@example.com',
            password='password',
            is_ambassador=False
        )
        not_ambassador_credentials = {
            'email': not_ambassador.email,
            'password': not_ambassador.password
        }
        res = self.client.post('/api/ambassador/login/', not_ambassador_credentials, format='json')

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
