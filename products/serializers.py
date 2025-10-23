from rest_framework import serializers
from .models import Category, Brand, ProductModel, ProductVariant


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class BrandSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    
    class Meta:
        model = Brand
        fields = '__all__'


class ProductModelSerializer(serializers.ModelSerializer):
    brand = BrandSerializer(read_only=True)
    
    class Meta:
        model = ProductModel
        fields = '__all__'


class ProductVariantSerializer(serializers.ModelSerializer):
    product_model = ProductModelSerializer(read_only=True)
    
    class Meta:
        model = ProductVariant
        fields = '__all__'



