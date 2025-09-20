# from django.contrib import admin

# from unfold.admin import ModelAdmin

# from .models import Product, ProductSKU, ProductCategory, ProductSubcategory,ProductImage


# @admin.register(Product)
# class ProductAdminClass(ModelAdmin):
#     list_display = ["id", "name", "description", "category", "product_id"]


# @admin.register(ProductSKU)
# class ProductSKUAdminClass(ModelAdmin):
#     list_display = ["id", "quantity", "price", "unit", "product"]


# @admin.register(ProductCategory)
# class ProductCategoryAdminClass(ModelAdmin):
#     list_display = ["id", "title", "slug"]


# @admin.register(ProductSubcategory)
# class ProductSubcategoryAdminClass(ModelAdmin):
#     list_display = ["id", "title", "slug", "category"]

# @admin.register(ProductImage)
# class ProductImageAdminClass(ModelAdmin):
#     list_display = ["id", "productSKU", "image"]
from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import Product, ProductSKU, ProductCategory, ProductSubcategory, ProductImage


class ProductSKUInline(admin.TabularInline):
    model = ProductSKU
    extra = 1  # nechta bo‘sh qator chiqsin
    fields = ["quantity", "price", "unit"]


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ["product", "image"]


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
