# D:\ETMOSHPHERE\BACKEND\etomosphere_backend\products\admin.py

from django.contrib import admin
from .models import (
    Category, CategoryImage,
    CatalogueProduct, CatalogueProductImage,
    Brand,
    Variant, VariantImage
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display        = ('name', 'solution', 'slug', 'sort_order', 'created_at')
    prepopulated_fields = {'slug': ('name',)}
    search_fields       = ('name', 'description')
    list_filter         = ('solution',)


@admin.register(CategoryImage)
class CategoryImageAdmin(admin.ModelAdmin):
    list_display     = ('category', 'is_main', 'created_at')
    list_filter      = ('category', 'is_main')
    search_fields    = ('category__name',)
    readonly_fields  = ('created_at', 'updated_at')


@admin.register(CatalogueProduct)
class CatalogueProductAdmin(admin.ModelAdmin):
    list_display        = ('name', 'category', 'slug', 'sort_order', 'created_at')
    prepopulated_fields = {'slug': ('name',)}
    list_filter         = ('category', 'category__solution')
    search_fields       = ('name', 'description')
    readonly_fields     = ('created_at', 'updated_at')
    fieldsets = (
        ('Basic Information', {
            'fields': ('category', 'name', 'slug', 'description', 'sort_order')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(CatalogueProductImage)
class CatalogueProductImageAdmin(admin.ModelAdmin):
    list_display    = ('product', 'alt_text', 'is_main', 'created_at')
    list_filter     = ('product', 'is_main')
    search_fields   = ('product__name', 'alt_text')
    readonly_fields = ('created_at', 'updated_at')
@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    # Changed 'product' to 'display_products' for the list view
    list_display    = ('name', 'display_products', 'website', 'created_at')
    
    # Changed 'product' to 'products' for the filter
    list_filter     = ('products', 'created_at')
    
    search_fields   = ('name', 'website')
    readonly_fields = ('created_at', 'updated_at')

    # Custom method to show the linked products in the admin list
    def display_products(self, obj):
        return ", ".join([p.name for p in obj.products.all()])
    
    # This sets the column header name in the admin panel
    display_products.short_description = 'Products'

@admin.register(Variant)
class VariantAdmin(admin.ModelAdmin):
    list_display    = ('name', 'brand', 'catalogue_product', 'sku', 'stock_status', 'lifecycle_status', 'price', 'is_on_sale', 'currency', 'created_at')
    list_filter     = ('brand', 'catalogue_product', 'stock_status', 'lifecycle_status', 'is_on_sale', 'currency')
    search_fields   = ('name', 'sku', 'mpn')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Basic Information', {
            'fields': ('brand', 'catalogue_product', 'name', 'sku', 'mpn', 'description', 'sort_order')
        }),
        ('Pricing', {
            'fields': ('price', 'sale_price', 'cost_price', 'currency', 'is_on_sale')
        }),
        ('Status', {
            'fields': ('stock_status', 'lifecycle_status')
        }),
        ('Specifications', {
            'fields': ('spec_json',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(VariantImage)
class VariantImageAdmin(admin.ModelAdmin):
    list_display    = ('variant', 'alt_text', 'is_main', 'created_at')
    list_filter     = ('variant', 'is_main')
    search_fields   = ('variant__name', 'alt_text')
    readonly_fields = ('created_at', 'updated_at')