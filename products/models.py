from django.db import models
from django.utils import timezone
from backend.storage_backends import CategoryImageStorage, ProductImageStorage

class Lifecycle(models.TextChoices):
    ACTIVE = 'active', 'Active'
    DISCONTINUED = 'discontinued', 'Discontinued'
    END_OF_LIFE = 'end_of_life', 'End of Life'


class StockStatus(models.TextChoices):
    IN_STOCK = 'in_stock', 'In Stock'
    OUT_OF_STOCK = 'out_of_stock', 'Out of Stock'




class TimeStampedModel(models.Model):
    created_at       = models.DateTimeField(default=timezone.now)
    updated_at       = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True



class Category(TimeStampedModel):

    slug            = models.SlugField(unique=True)
    name            = models.CharField(max_length=120)
    description     = models.TextField(blank=True)
    

class CategoryImage(models.Model):

    category        = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="images")
    image           = models.ImageField(storage=CategoryImageStorage(), upload_to='', max_length=5000000)
    is_main         = models.BooleanField(default=False)
    created_at      = models.DateTimeField(default=timezone.now)
    updated_at      = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Category Image"
        verbose_name_plural = "Category Images"
        ordering = ["-created_at"]
        unique_together = ["category", "image"]
        
        
        


class Brand(TimeStampedModel):

    category        = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="brands")
    name            = models.CharField(max_length=150)
    website         = models.URLField(blank=True)



class ProductModel(TimeStampedModel):
    
    brand                     = models.ForeignKey(Brand, on_delete=models.CASCADE)
    name                      = models.CharField(max_length=200)
    short_code                = models.CharField(max_length=60, blank=True)
    description               = models.TextField(blank=True)
    lifecycle_status          = models.CharField(choices=Lifecycle.choices)
    spec_json                 = models.JSONField(default=dict,blank=True, null=True)




class ProductVariant(TimeStampedModel):
    product_model                             = models.ForeignKey(ProductModel, on_delete=models.CASCADE)
    variant_name                              = models.CharField(max_length=120)
    sku                                       = models.CharField(max_length=80, blank=True)
    mpn                                       = models.CharField(max_length=80, blank=True)
    upc                                       = models.CharField(max_length=80, blank=True)
    status                                    = models.CharField(max_length=20, default="active")
    # Pricing Fields
    price                                     = models.DecimalField(max_digits=14, decimal_places=2, blank=True, null=True)
    sale_price                                = models.DecimalField(max_digits=14, decimal_places=2, blank=True, null=True, help_text="Discounted price")
    cost_price                                = models.DecimalField(max_digits=14, decimal_places=2, blank=True, null=True, help_text="Cost price for profit calculation")
    currency                                  = models.CharField(max_length=3, default="INR")
    is_on_sale                                = models.BooleanField(default=False, help_text="Is this product on sale?")
    spec_json                                 = models.JSONField(default=dict,blank=True, null=True)
    stock_status                              = models.CharField(max_length=20, choices=StockStatus.choices, default=StockStatus.IN_STOCK)
    

    def __str__(self):
        return f"{self.product_model.name} - {self.variant_name}"
    
    @property
    def current_price(self):
        """Returns the current selling price (sale_price if on sale, otherwise regular price)"""
        if self.is_on_sale and self.sale_price:
            return self.sale_price
        return self.price
    
    @property
    def discount_percentage(self):
        """Calculate discount percentage if on sale"""
        if self.is_on_sale and self.sale_price and self.price:
            discount = ((self.price - self.sale_price) / self.price) * 100
            return round(discount, 2)
        return 0
    
    @property
    def profit_margin(self):
        """Calculate profit margin if cost_price is provided"""
        if self.cost_price and self.current_price:
            margin = ((self.current_price - self.cost_price) / self.current_price) * 100
            return round(margin, 2)
        return None



class ProductImage(models.Model):
    product      = models.ForeignKey(ProductModel, on_delete=models.CASCADE, related_name="images")
    image        = models.ImageField(storage=ProductImageStorage(), upload_to="", max_length=5000000)
    is_main      = models.BooleanField(default=False)
    alt_text     = models.CharField(max_length=200, blank=True, help_text="Alternative text for accessibility")
    created_at   = models.DateTimeField(default=timezone.now)
    updated_at   = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Product Image"
        verbose_name_plural = "Product Images"
        ordering = ["-is_main", "-created_at"]
    
    def __str__(self):
        return f"{self.product.name} - {self.alt_text or 'Image'}"

