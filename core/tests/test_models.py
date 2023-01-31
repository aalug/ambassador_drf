"""
Test fpr models.
"""
from _decimal import Decimal
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import TestCase

from core.models import Product, Link, Order, OrderItem


def get_products_data():
    return {
        'title': 'Test Product',
        'description': 'This is a test product',
        'image': 'http://testproduct.com/image.jpg',
        'price': Decimal('19.99')
    }


def create_user(**params):
    """Create and return a new user."""
    return get_user_model().objects.create_user(**params)


def create_link(user, **params):
    """Create and return a link."""
    details = {
        'code': 'test',
        'user': user,
    }
    details.update(params)
    return Link.objects.create(**details)


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


def create_order_and_order_item(user):
    """Create and return a new order and order item."""
    order = Order.objects.create(user=user, code='TEST123', ambassador_email='test@example.com',
                                 first_name='Test', last_name='User', email='test@example.com')
    order_item = OrderItem.objects.create(order=order, product_title='Test Product',
                                          price=10.99, quantity=2, admin_revenue=1.50,
                                          ambassador_revenue=2.50)
    return order, order_item


class ModelTest(TestCase):
    """Test models."""

    def test_create_user_with_email_successful(self):
        """Test creating a user with an email is successful."""
        email = 'user@example.com'
        password = 'password123'
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test email is normalized for new users."""
        sample_emails = [
            ['test1@EXAMPLE.com', 'test1@example.com'],
            ['Test2@Example.com', 'Test2@example.com'],
            ['TEST3@EXAMPLE.COM', 'TEST3@example.com'],
            ['test4@example.COM', 'test4@example.com']
        ]
        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(email, 'password123')
            self.assertEqual(user.email, expected)

    def test_new_user_without_email_raise_error(self):
        """Test that creating a user without an email raises a ValueError."""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('', 'password123')

    def test_new_user_with_too_short_password_raise_error(self):
        """Test that creating a user without a password raises a ValueError."""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('user@example.com', 'test1')

    def test_new_user_with_6_chars_password_success(self):
        """Test that creating a user with a password 6 characters
           does not raise a ValueError."""
        get_user_model().objects.create_user(
            'user@example.com',
            'test12'
        )
        self.assertEqual(get_user_model().objects.count(), 1)

    def test_create_superuser(self):
        """Test creating a superuser."""
        user = get_user_model().objects.create_superuser(
            email='superuser@example.com',
            password='admin123'
        )
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_user_xtra_fields(self):
        """Test creating user with extra fields."""
        user_details = {
            'email': 'user@example.com',
            'password': 'password123',
            'first_name': 'First',
            'last_name': 'Last'
        }

        user = get_user_model().objects.create_user(**user_details)

        self.assertEqual(user.first_name, user_details['first_name'])
        self.assertEqual(user.last_name, user_details['last_name'])

    def test_product_creation(self):
        """Test creating a product."""
        data = get_products_data()
        Product.objects.create(**data)

        self.assertEqual(Product.objects.count(), 1)
        product_exists = Product.objects.filter(title=data['title']).exists()
        self.assertTrue(product_exists)


class RequireUserModelTests(TestCase):
    """Tests that require user to test. It is seperated
       to make it easier to test with no need to create
       new user every time."""

    def setUp(self):
        params = {
            'email': 'user@example.com',
            'password': 'password123',
            'first_name': 'First',
            'last_name': 'Last'
        }
        self.user = create_user(**params)

    def test_link_created(self):
        """Test if the link was created successfully."""
        create_link(self.user)
        self.assertTrue(Link.objects.filter(user=self.user).exists())

    def test_link_code_is_unique(self):
        """Test if the code for the link is unique."""
        Link.objects.create(code='abc', user=self.user)
        with self.assertRaises(IntegrityError):
            Link.objects.create(code='abc', user=self.user)

    def test_link_has_user(self):
        """Test if the link is associated with a user."""
        link = create_link(self.user)

        self.assertEqual(link.user, self.user)

    def test_link_has_products(self):
        """Test if the link is associated with products."""
        product = create_product()
        link = create_link(self.user)
        link.products.add(product)

        self.assertEqual(link.products.first(), product)

    def test_created_at_is_auto_now_add(self):
        """Test if the created_at field is automatically set on creation."""
        link = create_link(self.user)

        self.assertIsNotNone(link.created_at)

    def test_create_order(self):
        order = Order.objects.create(
            transaction_id='T12345',
            user=self.user,
            code='12345',
            ambassador_email='ambassador@example.com',
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            address='123 Main St',
            city='New York',
            country='USA',
            zip_code='10001',
        )

        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(order.transaction_id, 'T12345')
        self.assertEqual(order.user, self.user)
        self.assertEqual(order.code, '12345')
        self.assertEqual(order.ambassador_email, 'ambassador@example.com')
        self.assertEqual(order.first_name, 'John')
        self.assertEqual(order.last_name, 'Doe')
        self.assertEqual(order.email, 'john@example.com')
        self.assertEqual(order.address, '123 Main St')
        self.assertEqual(order.city, 'New York')
        self.assertEqual(order.country, 'USA')
        self.assertEqual(order.zip_code, '10001')
        self.assertFalse(order.complete)

    def test_order_str_representation(self):
        order = Order.objects.create(
            transaction_id='T12345',
            user=self.user,
            code='12345',
            ambassador_email='ambassador@example.com',
            first_name='John',
            last_name='Doe',
            email='john.doe@example.com',
            address='123 Main St',
            city='New York',
            country='USA',
            zip_code='10001',
        )

        self.assertEqual(str(order), 'T12345')

    def test_order_item_created(self):
        """Test if the order item was created successfully."""
        order, order_item = create_order_and_order_item(self.user)

        self.assertEqual(OrderItem.objects.count(), 1)
        self.assertEqual(order_item.product_title, 'Test Product')
        self.assertEqual(order_item.price, 10.99)
        self.assertEqual(order_item.quantity, 2)
        self.assertEqual(order_item.admin_revenue, 1.50)
        self.assertEqual(order_item.ambassador_revenue, 2.50)

    def test_order_item_str(self):
        """Test if the order item string representation is correct."""
        order, order_item = create_order_and_order_item(self.user)
        self.assertEqual(str(order_item), f'Order Item {order_item.id}')

    def test_order_item_delete(self):
        """Test if the order item can be deleted."""
        order, order_item = create_order_and_order_item(self.user)
        order_item.delete()
        self.assertEqual(OrderItem.objects.count(), 0)
