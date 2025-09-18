from django.contrib import admin

from unfold.admin import ModelAdmin

from .models import Product, ProductSKU, ProductCategory, ProductSubcategory


@admin.register(Product)
class ProductAdminClass(ModelAdmin):
    list_display = ["id", "name", "description", "category", "product_id"]


@admin.register(ProductSKU)
class ProductSKUAdminClass(ModelAdmin):
    list_display = ["id", "quantity", "price", "unit", "product"]


@admin.register(ProductCategory)
class ProductCategoryAdminClass(ModelAdmin):
    list_display = ["id", "title", "slug"]


@admin.register(ProductSubcategory)
class ProductSubcategoryAdminClass(ModelAdmin):
    list_display = ["id", "title", "slug", "category"]
