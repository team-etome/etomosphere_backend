# D:\ETMOSHPHERE\BACKEND\etomosphere_backend\app1\models.py

from django.db import models


class Solution(models.Model):
    """
    Top-level solution.
    Eg: 'Digital Conference Room', 'Digital Auditorium', 'Projector Solution'
    """
    name        = models.CharField(max_length=255)
    slug        = models.SlugField(unique=True, blank=True)
    image       = models.ImageField(upload_to="solutions/", blank=True, null=True)
    description = models.TextField(blank=True)
    sort_order  = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "id"]

    def __str__(self):
        return self.name


class Product(models.Model):
    """
    Old flat Product model — kept as-is since it's used elsewhere.
    DO NOT remove until you've migrated all usages.
    """
    solution   = models.ForeignKey(
                   Solution,
                   related_name="products",
                   on_delete=models.CASCADE,
                 )
    category   = models.CharField(
                   max_length=100,
                   blank=True,
                   help_text="Eg: IFPS, Cameras, Accessories, E-Note, E-Board, Display, AV Solutions"
                 )
    title      = models.CharField(max_length=255)
    details    = models.TextField(blank=True)
    image      = models.ImageField(upload_to="products/", blank=True, null=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["solution", "category", "sort_order", "id"]

    def __str__(self):
        return f"{self.solution.name} - {self.category} - {self.title}"