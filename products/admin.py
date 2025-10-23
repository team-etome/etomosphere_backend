from django.contrib import admin
from .models import Category, CategoryImage, Brand, ProductModel, ProductVariant, ProductImage


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'created_at')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'description')


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'website', 'created_at')
    list_filter = ('category', 'created_at')
    search_fields = ('name', 'website')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(ProductModel)
class ProductModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'brand', 'short_code', 'lifecycle_status', 'created_at')
    list_filter = ('brand', 'lifecycle_status', 'created_at')
    search_fields = ('name', 'short_code', 'description')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Basic Information', {
            'fields': ('brand', 'name', 'short_code', 'description', 'lifecycle_status')
        }),
        ('Specifications', {
            'fields': ('spec_json',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ('variant_name', 'product_model', 'sku', 'stock_status', 'price', 'currency', 'created_at')
    list_filter = ('product_model', 'status', 'stock_status', 'currency', 'created_at')
    search_fields = ('variant_name', 'sku', 'mpn', 'upc')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Basic Information', {
            'fields': ('product_model', 'variant_name', 'status')
        }),
        ('Identifiers', {
            'fields': ('sku', 'mpn', 'upc')
        }),
        ('Pricing', {
            'fields': ('price', 'currency')
        }),
        ('Stock Status', {
            'fields': ('stock_status',)
        }),
        ('Specifications', {
            'fields': ('spec_json',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('product', 'alt_text', 'is_main', 'created_at')
    list_filter = ('product', 'is_main', 'created_at')
    search_fields = ('product__name', 'alt_text')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(CategoryImage)
class CategoryImageAdmin(admin.ModelAdmin):
    list_display = ('category', 'is_main', 'created_at')
    list_filter = ('category', 'is_main', 'created_at')
    search_fields = ('category__name',)
    readonly_fields = ('created_at', 'updated_at')