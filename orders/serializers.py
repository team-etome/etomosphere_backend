from rest_framework import serializers
from .models import Order, OrderItem
from products.serializers import ProductVariantSerializer
from accounts.serializers import UserSerializer


class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductVariantSerializer(read_only=True)
    
    class Meta:
        model = OrderItem
        fields = ('id', 'product', 'quantity', 'price')


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Order
        fields = ('id', 'user', 'order_number', 'total_amount', 'status', 'payment_status',
                 'shipping_address', 'billing_address', 'phone', 'items', 'created_at', 'updated_at')



