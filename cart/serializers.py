from rest_framework import serializers
from .models import Cart, CartItem
from products.serializers import ProductVariantSerializer
from products.models import ProductVariant


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductVariantSerializer(read_only=True)
    total_price = serializers.ReadOnlyField()
    product_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = CartItem
        fields = ('id', 'product', 'product_id', 'quantity', 'total_price', 'added_at')
    
    def create(self, validated_data):
        product_id = validated_data.pop('product_id')
        product = ProductVariant.objects.get(id=product_id)
        validated_data['product'] = product
        return super().create(validated_data)


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_items = serializers.ReadOnlyField()
    total_price = serializers.ReadOnlyField()
    
    class Meta:
        model = Cart
        fields = ('id', 'user', 'items', 'total_items', 'total_price', 'created_at', 'updated_at')
