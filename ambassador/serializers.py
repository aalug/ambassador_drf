"""
Serializers for the ambassador app.
"""
from rest_framework import serializers

from core.models import Product, Link


class ProductSerializer(serializers.ModelSerializer):
    """Serializer for the Product model."""

    class Meta:
        model = Product
        fields = '__all__'


class LinkSerializer(serializers.ModelSerializer):
    """Serializer for the Link model."""

    class Meta:
        model = Link
        fields = '__all__'
