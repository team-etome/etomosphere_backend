from rest_framework import serializers
from .models import Category, Brand, ProductModel, ProductVariant, ProductImage


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class BrandSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    
    class Meta:
        model = Brand
        fields = '__all__'


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ('id', 'image', 'is_main', 'alt_text', 'created_at')


class ProductModelSerializer(serializers.ModelSerializer):
    brand = BrandSerializer(read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    main_image = serializers.SerializerMethodField()
    
    class Meta:
        model = ProductModel
        fields = '__all__'
    
    def get_main_image(self, obj):
        """Get the main product image"""
        main_image = obj.images.filter(is_main=True).first()
        if main_image:
            return ProductImageSerializer(main_image).data
        # If no main image, return the first image
        first_image = obj.images.first()
        if first_image:
            return ProductImageSerializer(first_image).data
        return None


class ProductVariantSerializer(serializers.ModelSerializer):
    product_model = ProductModelSerializer(read_only=True)
    
    class Meta:
        model = ProductVariant
        fields = '__all__'



