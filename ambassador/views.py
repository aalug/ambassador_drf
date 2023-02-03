"""
Views for ambassador app.
"""
import math
import random
import string

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django_redis import get_redis_connection

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from ambassador.serializers import ProductSerializer, LinkSerializer
from common.authentication import JWTAuthentication
from core.models import Product, Link, Order


class ProductFrontendAPIView(APIView):
    """Product API view. It will exist alongside ProductBackendAPIView
       to show differences in functionality."""
    serializer_class = ProductSerializer

    @method_decorator(cache_page(60 * 60 * 2, key_prefix='products_frontend'))
    def get(self, _):
        products = Product.objects.all()
        serializer = self.serializer_class(products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ProductBackendAPIView(APIView):
    """Product API view. It will exist alongside ProductFrontendAPIView
       to show differences in functionality."""
    serializer_class = ProductSerializer

    def get(self, request):
        products = cache.get('products_backend')
        if not products:
            products = list(Product.objects.all())
            cache.set('products_backend', products, timeout=60 * 30)

        search = request.query_params.get('search', '')
        if search:
            products = list([
                p for p in products
                if (search.lower() in p.title.lower()
                    or search.lower() in p.description.lower())
            ])

        total = len(products)

        sort = request.query_params.get('sort', None)
        if sort == 'price-asc':
            products.sort(key=lambda p: p.price)
        elif sort == 'price-desc':
            products.sort(key=lambda p: p.price, reverse=True)
        elif sort == 'title-asc':
            products.sort(key=lambda p: p.title)
        elif sort == 'title-desc':
            products.sort(key=lambda p: p.price, reverse=True)

        per_page = 9
        page = int(request.query_params.get('page', 1))
        start = (page - 1) * per_page
        end = page * per_page

        data = self.serializer_class(products[start:end], many=True).data
        return Response({
            'data': data,
            'meta': {
                'total': total,
                'page': page,
                'last_page': math.ceil(total / per_page)
            }
        }, status=status.HTTP_200_OK)


class LinkAPIView(APIView):
    """API View for creating links."""
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = LinkSerializer

    def post(self, request):
        user = request.user
        serializer = self.serializer_class(data={
            'user': user.id,
            'code': ''.join(random.choices(string.ascii_lowercase + string.digits, k=6)),
            'products': request.data['products']
        })
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)


class StatsAPIView(APIView):
    """API View for Link stats."""
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user = request.user
        links = Link.objects.filter(user__id=user.id)

        return Response([(self._format(link)) for link in links])

    @staticmethod
    def _format(link):
        orders = Order.objects.filter(code=link.code, complete=1)
        return {
            'code': link.code,
            'count': len(orders),
            'revenue': sum(o.ambassador_revenue for o in orders)
        }


class RankingsAPIView(APIView):
    """API View for getting ambassadors with revenues in order."""
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        con = get_redis_connection('default')

        rankings = con.zrevrangebyscore('rankings', min=0, max=10000, withscores=True)

        return Response({
            r[0].decode('utf-8'): r[1] for r in rankings
        })
