from django.contrib import admin
from django.apps import apps
from .models import Solution, Product


class ProductInline(admin.TabularInline):
    model = Product
    extra = 1  # show one empty row by default
    fields = ("category", "title", "details", "image", "sort_order")
    show_change_link = True


@admin.register(Solution)
class SolutionAdmin(admin.ModelAdmin):
    list_display = ("name", "sort_order")
    inlines = [ProductInline]
    search_fields = ("name",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("title", "solution", "category", "sort_order")
    list_filter = ("solution", "category")
    search_fields = ("title", "details")


APP_LABELS = [
    'employees'
]

for app_label in APP_LABELS:
    try:
        app_config = apps.get_app_config(app_label)
    except LookupError:
        # app not installed; skip
        continue

    for model in app_config.get_models():
        try:
            admin.site.register(model)
        except admin.sites.AlreadyRegistered:
            pass
