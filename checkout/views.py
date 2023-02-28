"""
Views for the checkout app.
"""
import decimal

import stripe
from django.conf import settings
from django.db import transaction
from django.core.mail import send_mail
from rest_framework import status, exceptions
from rest_framework.response import Response
from rest_framework.views import APIView

from checkout.serializers import LinkSerializer
from core.models import Link, Order, Product, OrderItem


class LinkAPIView(APIView):
    """API View for fetching links."""
    serializer_class = LinkSerializer

    def get(self, _, code=''):
        link = Link.objects.filter(code=code).first()
        serializer = self.serializer_class(link)
        return Response(serializer.data, status=status.HTTP_200_OK)


class OrderAPIView(APIView):
    """API View for placing orders."""

    @transaction.atomic
    def post(self, request):
        data = request.data
        link = Link.objects.filter(code=data['code']).first()

        if not link:
            raise exceptions.APIException('Invalid code!')
        try:
            order = Order()
            order.code = link.code
            order.user_id = link.user.id
            order.ambassador_email = link.user.email
            order.first_name = data['first_name']
            order.last_name = data['last_name']
            order.email = data['email']
            order.address = data['address']
            order.country = data['country']
            order.city = data['city']
            order.zip_code = data['zip_code']
            order.save()

            line_items = []

            for item in data['products']:
                product = Product.objects.filter(pk=item['product_id']).first()
                quantity = decimal.Decimal(item['quantity'])

                order_item = OrderItem()
                order_item.order = order
                order_item.product_title = product.title
                order_item.price = product.price
                order_item.quantity = quantity
                order_item.ambassador_revenue = decimal.Decimal(.1) * product.price * quantity
                order_item.admin_revenue = decimal.Decimal(.9) * product.price * quantity
                order_item.save()

                line_items.append({
                    'name': product.title,
                    'description': product.description,
                    'images': [
                        product.image
                    ],
                    'amount': int(100 * product.price),
                    'currency': 'usd',
                    'quantity': quantity
                })

            stripe.api_key = settings.STRIPE_API_KEY

            source = stripe.checkout.Session.create(
                success_url=f'{settings.FRONTEND_URL}/checkout/success?source={CHECKOUT_SESSION_ID}',
                cancel_url=f'{settings.FRONTEND_URL}/checkout/error',
                payment_method_types=['card'],
                line_items=line_items
            )

            order.transaction_id = source['id']
            order.save()

            return Response(source, status=status.HTTP_200_OK)

        except Exception:
            transaction.rollback()

        return Response({
            'message': 'Error occurred while creating an Order or OrderItem'
        })


class ConfirmOrderAPIView(APIView):
    """API View for confirming orders."""

    def post(self, request):
        order = Order.objects.filter(transaction_id=request.data['source']).firtst()
        if not order:
            raise exceptions.APIException('Order not found.')

        order.complete = True
        order.save()

        # To admin
        send_mail(
            subject='An order has been completed.',
            message=f'Order #{order.id} with total of ${order.admin_revenue} has been completed.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.ADMIN_EMAIL]
        )

        # to ambassador
        send_mail(
            subject='An order has been completed.',
            message=f'You earned ${order.ambassador_revenue} from the link #{order.code}.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[order.ambassador_email]
        )

        return Response({
            'message': 'Success!'
        }, status=status.HTTP_200_OK)
