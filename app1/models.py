from django.db import models


class Solution(models.Model):
    """
    Example: 'Classroom', 'Auditorium & Seminar Hall', etc.
    """
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to="solutions/", blank=True, null=True)
    description = models.TextField(blank=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "id"]

    def __str__(self):
        return self.name


class Product(models.Model):
    """
    Individual product/item under a solution.
    Example:
      - title: 'Economical Series'
      - category: 'IFPS'
      - belongs to: 'Classroom'
    """
    solution = models.ForeignKey(
        Solution,
        related_name="products",
        on_delete=models.CASCADE,
    )
    # This replaces "sections" like IFPS, Cameras, Accessories, etc.
    category = models.CharField(
        max_length=100,
        blank=True,  # keep flexible: you can leave empty if not needed
        help_text="Eg: IFPS, Cameras, Accessories, E-Note, E-Board, Display, AV Solutions…",
    )
    title = models.CharField(max_length=255)
    details = models.TextField(blank=True)
    image = models.ImageField(upload_to="products/", blank=True, null=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["solution", "category", "sort_order", "id"]

    def __str__(self):
        return f"{self.solution.name} - {self.category} - {self.title}"
