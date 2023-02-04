"""
Serializers for the checkout app.
"""
from rest_framework import serializers

from common.serializers import UserSerializer
from core.models import Product, Link


class ProductSerializer(serializers.ModelSerializer):
    """Serializer for the Product model and for this particular app."""

    class Meta:
        model = Product
        fields = '__all__'


class LinkSerializer(serializers.ModelSerializer):
    """Serializer for the Link model and for this particular app."""
    products = ProductSerializer(many=True)
    user = UserSerializer()

    class Meta:
        model = Link
        fields = '__all__'
