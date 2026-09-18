from django.contrib import admin
from .models import ProductReview, PublicReview


@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'rating', 'title', 'is_verified_purchase', 'created_at')
    list_filter = ('rating', 'is_verified_purchase', 'created_at')
    search_fields = ('user__username', 'product__name', 'title', 'comment')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(PublicReview)
class PublicReviewAdmin(admin.ModelAdmin):
    list_display  = ('name', 'school', 'rating', 'is_approved', 'created_at')
    list_filter   = ('is_approved', 'rating')
    search_fields = ('name', 'school', 'comment')
    readonly_fields = ('created_at',)
    actions = ['approve_reviews', 'reject_reviews']

    @admin.action(description='Approve selected reviews')
    def approve_reviews(self, request, queryset):
        queryset.update(is_approved=True)

    @admin.action(description='Reject selected reviews')
    def reject_reviews(self, request, queryset):
        queryset.update(is_approved=False)