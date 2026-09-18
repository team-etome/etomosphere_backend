# D:\ETMOSHPHERE\BACKEND\etomosphere_backend\reviews\models.py

from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


class ProductReview(models.Model):

    user                = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews')
    product             = models.ForeignKey('products.Variant', on_delete=models.CASCADE, related_name='reviews')  # ← was ProductVariant
    rating              = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    title               = models.CharField(max_length=200)
    comment             = models.TextField()
    is_verified_purchase = models.BooleanField(default=False)
    created_at          = models.DateTimeField(auto_now_add=True)
    updated_at          = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.product.name} ({self.rating} stars)"  # ← variant_name → name


class PublicReview(models.Model):
    name        = models.CharField(max_length=150)
    school      = models.CharField(max_length=200, blank=True)
    rating      = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment     = models.TextField()
    is_approved = models.BooleanField(default=False)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        status = 'approved' if self.is_approved else 'pending'
        return f"{self.name} ({self.rating}★) [{status}]"