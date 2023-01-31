from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status, generics, mixins

from administrator.serializers import ProductSerializer, LinkSerializer
from common.authentication import JWTAuthentication
from common.serializers import UserSerializer
from core.models import Product, Link, Order


class AmbassadorAPIView(APIView):
    """API view for retrieving ambassadors."""
    serializer_class = UserSerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, _):
        ambassadors = get_user_model().objects.filter(is_ambassador=True)
        serializer = self.serializer_class(ambassadors, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ProductGenericAPIView(generics.GenericAPIView,
                            mixins.RetrieveModelMixin,
                            mixins.ListModelMixin,
                            mixins.CreateModelMixin,
                            mixins.UpdateModelMixin,
                            mixins.DestroyModelMixin):
    """API view for managing products (CRUD)."""
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = ProductSerializer
    queryset = Product.objects.all()

    def get(self, request, pk=None):
        if pk is not None:
            return self.retrieve(request, pk)
        return self.list(request)

    def post(self, request):
        return self.create(request)

    def put(self, request, pk=None):
        return self.partial_update(request, pk)

    def delete(self, request, pk=None):
        return self.destroy(request, pk)


class LinkAPIView(APIView):
    """View for linking products."""
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = LinkSerializer

    def get(self, request, pk=None):
        links = Link.objects.filter(user__id=pk)
        serializer = self.serializer_class(links, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class OrderAPIView(APIView):
    """View for retrieving products."""
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = LinkSerializer

    def get(self, request):
        orders = Order.objects.filter(complete=True)
        serializer = self.serializer_class(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
