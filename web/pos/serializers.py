from rest_framework import serializers
from .models import Order, Order_Item


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ('id', 'user', 'total_price', 'done', 'last_change')


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model=Order_Item
        fields = ('id', 'product', 'order', 'price', 'name', 'timestamp')
