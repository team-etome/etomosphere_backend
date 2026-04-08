# D:\ETMOSHPHERE\BACKEND\etomosphere_backend\products\serializers.py

from rest_framework import serializers
from .models import (
    Category, CategoryImage,
    CatalogueProduct, CatalogueProductImage,
    Brand,
    Variant, VariantImage
)


# ──────────────────────────────────────────────────────────────
# CATEGORY
# ──────────────────────────────────────────────────────────────

class CategoryImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoryImage
        fields = ('id', 'image', 'is_main', 'created_at')


class CategorySerializer(serializers.ModelSerializer):
    images = CategoryImageSerializer(many=True, read_only=True)
    solution_name = serializers.CharField(source='solution.name', read_only=True)

    class Meta:
        model = Category
        fields = ('id', 'name', 'slug', 'description', 'sort_order', 'solution_name', 'images')


# ──────────────────────────────────────────────────────────────
# CATALOGUE PRODUCT
# ──────────────────────────────────────────────────────────────

class CatalogueProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = CatalogueProductImage
        fields = ('id', 'image', 'is_main', 'alt_text', 'created_at')


class CatalogueProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    images   = CatalogueProductImageSerializer(many=True, read_only=True)
    main_image = serializers.SerializerMethodField()

    class Meta:
        model = CatalogueProduct
        fields = ('id', 'name', 'slug', 'description', 'sort_order',
                  'category', 'images', 'main_image', 'created_at', 'updated_at')

    def get_main_image(self, obj):
        image = obj.images.filter(is_main=True).first() or obj.images.first()
        return CatalogueProductImageSerializer(image).data if image else None


# ──────────────────────────────────────────────────────────────
# BRAND
# ──────────────────────────────────────────────────────────────

class BrandSerializer(serializers.ModelSerializer):
    product = CatalogueProductSerializer(read_only=True)

    class Meta:
        model = Brand
        fields = ('id', 'name', 'logo', 'website', 'product', 'created_at', 'updated_at')


# ──────────────────────────────────────────────────────────────
# VARIANT
# ──────────────────────────────────────────────────────────────

class VariantImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = VariantImage
        fields = ('id', 'image', 'is_main', 'alt_text', 'created_at')


class VariantSerializer(serializers.ModelSerializer):
    brand        = BrandSerializer(read_only=True)
    images       = VariantImageSerializer(many=True, read_only=True)
    main_image   = serializers.SerializerMethodField()
    current_price       = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)
    discount_percentage = serializers.FloatField(read_only=True)
    profit_margin       = serializers.FloatField(read_only=True)

    class Meta:
        model = Variant
        fields = (
            'id', 'name', 'sku', 'mpn', 'description', 'spec_json',
            'price', 'sale_price', 'cost_price', 'currency',
            'is_on_sale', 'current_price', 'discount_percentage', 'profit_margin',
            'stock_status', 'lifecycle_status', 'sort_order',
            'brand', 'images', 'main_image',
            'created_at', 'updated_at'
        )

    def get_main_image(self, obj):
        image = obj.images.filter(is_main=True).first() or obj.images.first()
        return VariantImageSerializer(image).data if image else None


# ──────────────────────────────────────────────────────────────
# LIGHTWEIGHT SERIALIZERS (for cart, orders, etc.)
# ──────────────────────────────────────────────────────────────

class VariantMiniSerializer(serializers.ModelSerializer):
    """Lightweight Variant serializer — use in Cart, Orders, etc."""
    brand_name    = serializers.CharField(source='brand.name', read_only=True)
    product_name  = serializers.CharField(source='brand.product.name', read_only=True)
    current_price = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)
    main_image    = serializers.SerializerMethodField()

    class Meta:
        model = Variant
        fields = (
            'id', 'name', 'sku', 'brand_name', 'product_name',
            'price', 'current_price', 'currency', 'is_on_sale',
            'stock_status', 'main_image'
        )

    def get_main_image(self, obj):
        image = obj.images.filter(is_main=True).first() or obj.images.first()
        if image:
            return image.image.url
        # Fall back to catalogue product image
        prod_image = obj.brand.product.images.filter(is_main=True).first()
        return prod_image.image.url if prod_image else None