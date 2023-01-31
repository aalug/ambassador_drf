"""
Serializers for the administrator app.
"""
from rest_framework import serializers

from core.models import Product, Link, OrderItem, Order


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


class OrderItemSerializer(serializers.ModelSerializer):
    """Serializer for the OrderItem model."""

    class Meta:
        model = OrderItem
        fields = '__all__'


class OrderSerializer(serializers.ModelSerializer):
    """Serializer for the Order model."""
    order_items = OrderItemSerializer(many=True)
    total = serializers.SerializerMethodField('get_total')

    def get_total(self, obj):
        """Get the total value."""
        items = OrderItem.objects.filter(order__id=obj.id)
        return sum((i.price * i.quantity for i in items))

    class Meta:
        model = Order
        fields = '__all__'
