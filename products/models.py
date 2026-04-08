# D:\ETMOSHPHERE\BACKEND\etomosphere_backend\products\models.py

from django.db import models
from django.utils import timezone
from backend.storage_backends import CategoryImageStorage, ProductImageStorage
from app1.models import Solution


# ──────────────────────────────────────────────────────────────
# ABSTRACT BASE
# ──────────────────────────────────────────────────────────────

class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


# ──────────────────────────────────────────────────────────────
# LEVEL 1 — CATEGORY
# Eg: Hardware, Software
# Belongs to → Solution
# ──────────────────────────────────────────────────────────────

class Category(TimeStampedModel):
    """
    Eg: Hardware, Software
    Digital Conference Room → Hardware
    Digital Conference Room → Software
    """
    solution    = models.ForeignKey(
                    Solution,
                    on_delete=models.CASCADE,
                    related_name="categories",null=True,blank=True
                  )
    name        = models.CharField(max_length=120)
    slug        = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    sort_order  = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "name"]
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def __str__(self):
        return f"{self.solution.name} → {self.name}"


class CategoryImage(TimeStampedModel):
    """Images for a Category."""
    category = models.ForeignKey(
                 Category,
                 on_delete=models.CASCADE,
                 related_name="images"
               )
    image    = models.ImageField(
                 storage=CategoryImageStorage(),
                 upload_to='',
                 max_length=5000000
               )
    is_main  = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Category Image"
        verbose_name_plural = "Category Images"
        ordering = ["-created_at"]
        unique_together = ["category", "image"]

    def __str__(self):
        return f"{self.category.name} - Image"


# ──────────────────────────────────────────────────────────────
# LEVEL 2 — PRODUCT
# Eg: Interactive Display, PTZ Camera, Video Conferencing System
# Belongs to → Category
# ──────────────────────────────────────────────────────────────

class CatalogueProduct(TimeStampedModel):
    """
    The actual product type / item in the catalogue.
    Eg: 'Interactive Display', 'PTZ Camera', 'UPS / Power Backup'
    Hardware → Interactive Display
    Hardware → PTZ Camera
    Software → Video Conferencing Platform
    """
    category    = models.ForeignKey(
                    Category,
                    on_delete=models.CASCADE,
                    related_name="catalogue_products"
                  )
    name        = models.CharField(max_length=200)
    slug        = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    sort_order  = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "name"]
        verbose_name = "Catalogue Product"
        verbose_name_plural = "Catalogue Products"

    def __str__(self):
        return f"{self.category.name} → {self.name}"


class CatalogueProductImage(TimeStampedModel):
    """Images for a Catalogue Product."""
    product  = models.ForeignKey(
                 CatalogueProduct,
                 on_delete=models.CASCADE,
                 related_name="images"
               )
    image    = models.ImageField(
                 storage=ProductImageStorage(),
                 upload_to="",
                 max_length=5000000
               )
    is_main  = models.BooleanField(default=False)
    alt_text = models.CharField(max_length=200, blank=True)

    class Meta:
        verbose_name = "Catalogue Product Image"
        verbose_name_plural = "Catalogue Product Images"
        ordering = ["-is_main", "-created_at"]

    def __str__(self):
        return f"{self.product.name} - {self.alt_text or 'Image'}"


# ──────────────────────────────────────────────────────────────
# LEVEL 3 — BRAND
# Eg: BenQ, Samsung, Logitech, Hikvision
# Belongs to → CatalogueProduct
# ──────────────────────────────────────────────────────────────

class Brand(TimeStampedModel):
    """
    Brand that manufactures this product.
    Interactive Display → BenQ
    Interactive Display → Samsung
    PTZ Camera → Hikvision
    PTZ Camera → CP Plus
    """
    products = models.ManyToManyField(
        CatalogueProduct, 
        related_name="brands",
        blank=True
    )
    name    = models.CharField(max_length=150)
    logo    = models.ImageField(upload_to='brand_logos/', blank=True, null=True)
    website = models.URLField(blank=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Brand"
        verbose_name_plural = "Brands"

    def __str__(self):
        # Since it's ManyToMany, one brand could have many products. 
        # It's safer to just return the name.
        return self.name


# ──────────────────────────────────────────────────────────────
# LEVEL 4 — VARIANT
# Eg: BenQ RP8603 65" — ₹1,20,000 — In Stock
# Belongs to → Brand
# ──────────────────────────────────────────────────────────────

class Variant(TimeStampedModel):
    """
    A specific model/SKU from a brand.
    BenQ → RP8603 65 inch → ₹1,20,000 → In Stock
    BenQ → RP7503 75 inch → ₹1,80,000 → In Stock
    Samsung → WA65C 65 inch → ₹1,50,000 → In Stock
    """

    class StockStatus(models.TextChoices):
        IN_STOCK     = 'in_stock',     'In Stock'
        OUT_OF_STOCK = 'out_of_stock', 'Out of Stock'

    class Lifecycle(models.TextChoices):
        ACTIVE       = 'active',       'Active'
        DISCONTINUED = 'discontinued', 'Discontinued'
        END_OF_LIFE  = 'end_of_life',  'End of Life'

    brand            = models.ForeignKey(
                         Brand,
                         on_delete=models.CASCADE,
                         related_name="variants"
                       )
    name             = models.CharField(max_length=200)          # "RP8603 65 inch"
    sku              = models.CharField(max_length=80, blank=True)
    mpn              = models.CharField(max_length=80, blank=True)
    description      = models.TextField(blank=True)

    # Flexible specs
    # Eg: {"screen_size": "65 inch", "resolution": "4K", "touch_points": 20}
    spec_json        = models.JSONField(default=dict, blank=True, null=True)

    # Pricing
    price            = models.DecimalField(max_digits=14, decimal_places=2, blank=True, null=True)
    sale_price       = models.DecimalField(max_digits=14, decimal_places=2, blank=True, null=True, help_text="Discounted price")
    cost_price       = models.DecimalField(max_digits=14, decimal_places=2, blank=True, null=True, help_text="Internal cost — not shown on site")
    currency         = models.CharField(max_length=3, default="INR")
    is_on_sale       = models.BooleanField(default=False)

    # Status
    stock_status     = models.CharField(
                         max_length=20,
                         choices=StockStatus.choices,
                         default=StockStatus.IN_STOCK
                       )
    lifecycle_status = models.CharField(
                         max_length=20,
                         choices=Lifecycle.choices,
                         default=Lifecycle.ACTIVE
                       )
    sort_order       = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "name"]
        verbose_name = "Variant"
        verbose_name_plural = "Variants"

    def __str__(self):
        return f"{self.brand.name} {self.name}"

    @property
    def current_price(self):
        """Returns sale_price if on sale, otherwise regular price."""
        if self.is_on_sale and self.sale_price:
            return self.sale_price
        return self.price

    @property
    def discount_percentage(self):
        """Discount % off regular price."""
        if self.is_on_sale and self.sale_price and self.price:
            return round(((self.price - self.sale_price) / self.price) * 100, 2)
        return 0

    @property
    def profit_margin(self):
        """Internal profit margin % — admin use only, never expose to frontend."""
        if self.cost_price and self.current_price:
            return round(((self.current_price - self.cost_price) / self.current_price) * 100, 2)
        return None


class VariantImage(TimeStampedModel):
    """Images for a specific Variant."""
    variant  = models.ForeignKey(
                 Variant,
                 on_delete=models.CASCADE,
                 related_name="images"
               )
    image    = models.ImageField(
                 storage=ProductImageStorage(),
                 upload_to="",
                 max_length=5000000
               )
    is_main  = models.BooleanField(default=False)
    alt_text = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ["-is_main", "-created_at"]
        verbose_name = "Variant Image"
        verbose_name_plural = "Variant Images"

    def __str__(self):
        return f"{self.variant} - {self.alt_text or 'Image'}"