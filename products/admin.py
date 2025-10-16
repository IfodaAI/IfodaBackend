# from django.contrib import admin
# from unfold.admin import ModelAdmin, TabularInline

# from .models import (
#     Product,
#     ProductSKU,
#     ProductCategory,
#     ProductSubcategory,
#     ProductImage,
#     DiseaseCategory,
#     Disease
# )


# class ProductSKUInline(TabularInline):
#     model = ProductSKU
#     extra = 1  # nechta bo‘sh qator chiqsin
#     fields = ["quantity", "price", "is_small_package", "unit"]


# class ProductImageInline(TabularInline):
#     model = ProductImage
#     extra = 1
#     fields = ["product", "image"]


# @admin.register(ProductSKU)
# class ProductSKUAdminClass(ModelAdmin):
#     list_display = ["id", "quantity", "price", "is_small_package", "unit"]


# @admin.register(Product)
# class ProductAdminClass(ModelAdmin):
#     list_display = ["id", "name", "description", "category", "product_id"]
#     search_fields=["name"]
#     inlines = [ProductSKUInline, ProductImageInline]


# @admin.register(ProductCategory)
# class ProductCategoryAdminClass(ModelAdmin):
#     list_display = ["id", "title", "slug"]

# @admin.register(ProductSubcategory)
# class ProductSubcategoryAdminClass(ModelAdmin):
#     list_display = ["id", "title", "slug", "category"]

# @admin.register(DiseaseCategory)
# class DiseaseCategoryAdminClass(ModelAdmin):
#     list_display = ["id", "title", "slug"]

# @admin.register(Disease)
# class DiseaseAdminClass(ModelAdmin):
#     list_display = ["id", "name", "category"]
from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline, register
from unfold.forms import UnfoldModelForm
from unfold.widgets import UnfoldImageField

from .models import (
    Product,
    ProductSKU,
    ProductCategory,
    ProductSubcategory,
    ProductImage,
    DiseaseCategory,
    Disease
)


# 🔹 Inline uchun forma (drag-drop bilan)
class ProductImageInlineForm(UnfoldModelForm):
    image = UnfoldImageField(label="Rasm yuklash (drag & drop)")

    class Meta:
        model = ProductImage
        fields = "__all__"


class ProductImageInline(TabularInline):
    model = ProductImage
    form = ProductImageInlineForm
    extra = 1
    fields = ["product", "image"]


# 🔹 Product uchun forma
class ProductForm(UnfoldModelForm):
    image_thumbnail = UnfoldImageField(label="Mahsulot uchun thumbnail")

    class Meta:
        model = Product
        fields = "__all__"


@register(Product)
class ProductAdminClass(ModelAdmin):
    form = ProductForm
    list_display = ["id", "name", "description", "category", "product_id"]
    search_fields = ["name"]
    inlines = [ProductImageInline]


@register(ProductSKU)
class ProductSKUAdminClass(ModelAdmin):
    list_display = ["id", "quantity", "price", "is_small_package", "unit"]


@register(ProductCategory)
class ProductCategoryAdminClass(ModelAdmin):
    list_display = ["id", "title", "slug"]


@register(ProductSubcategory)
class ProductSubcategoryAdminClass(ModelAdmin):
    list_display = ["id", "title", "slug", "category"]


@register(DiseaseCategory)
class DiseaseCategoryAdminClass(ModelAdmin):
    list_display = ["id", "title", "slug"]


@register(Disease)
class DiseaseAdminClass(ModelAdmin):
    list_display = ["id", "name", "category"]
