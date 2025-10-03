from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline

from .models import (
    Product,
    ProductSKU,
    ProductCategory,
    ProductSubcategory,
    ProductImage,
)


class ProductSKUInline(TabularInline):
    model = ProductSKU
    extra = 1  # nechta bo‘sh qator chiqsin
    fields = ["quantity", "price", "is_small_package", "unit"]


class ProductImageInline(TabularInline):
    model = ProductImage
    extra = 1
    fields = ["product", "image"]


@admin.register(ProductSKU)
class ProductSKUAdminClass(ModelAdmin):
    list_display = ["id", "quantity", "price", "is_small_package", "unit"]


@admin.register(Product)
class ProductAdminClass(ModelAdmin):
    list_display = ["id", "name", "description", "category", "product_id"]
    inlines = [ProductSKUInline, ProductImageInline]


@admin.register(ProductCategory)
class ProductCategoryAdminClass(ModelAdmin):
    list_display = ["id", "title", "slug"]


@admin.register(ProductSubcategory)
class ProductSubcategoryAdminClass(ModelAdmin):
    list_display = ["id", "title", "slug", "category"]
