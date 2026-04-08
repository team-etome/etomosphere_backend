# D:\ETMOSHPHERE\BACKEND\etomosphere_backend\orders\models.py

from django.db import models
from django.conf import settings


class Order(models.Model):

    ORDER_STATUS = [
        ('pending',    'Pending'),
        ('confirmed',  'Confirmed'),
        ('processing', 'Processing'),
        ('shipped',    'Shipped'),
        ('delivered',  'Delivered'),
        ('cancelled',  'Cancelled'),
    ]

    PAYMENT_STATUS = [
        ('pending',  'Pending'),
        ('paid',     'Paid'),
        ('failed',   'Failed'),
        ('refunded', 'Refunded'),
    ]

    user             = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    order_number     = models.CharField(max_length=20, unique=True)
    total_amount     = models.DecimalField(max_digits=10, decimal_places=2)
    status           = models.CharField(max_length=20, choices=ORDER_STATUS, default='pending')
    payment_status   = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')
    shipping_address = models.TextField()
    billing_address  = models.TextField()
    phone            = models.CharField(max_length=15)
    created_at       = models.DateTimeField(auto_now_add=True)
    updated_at       = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order {self.order_number}"


class OrderItem(models.Model):

    order    = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product  = models.ForeignKey('products.Variant', on_delete=models.CASCADE)  # ← was ProductVariant
    quantity = models.PositiveIntegerField()
    price    = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity}x {self.product.name}"  # ← variant_name → name