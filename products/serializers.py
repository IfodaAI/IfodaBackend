from utils.serializers import BaseModelSerializer
from .models import (
    Disease,
    DiseaseCategory,
    Product,
    ProductCategory,
    ProductImage,
    ProductSKU,
    ProductSubcategory,
)


class DiseaseSerializer(BaseModelSerializer):
    class Meta(BaseModelSerializer.Meta):
        model = Disease


class DiseaseCategorySerializer(BaseModelSerializer):
    class Meta(BaseModelSerializer.Meta):
        model = DiseaseCategory


class ProductCategorySerializer(BaseModelSerializer):
    class Meta(BaseModelSerializer.Meta):
        model = ProductCategory


class ProductSubcategorySerializer(BaseModelSerializer):
    class Meta(BaseModelSerializer.Meta):
        model = ProductSubcategory


class ProductSerializer(BaseModelSerializer):
    class Meta(BaseModelSerializer.Meta):
        model = Product


class ProductSKUSerializer(BaseModelSerializer):
    class Meta(BaseModelSerializer.Meta):
        model = ProductSKU


class ProductImageSerializer(BaseModelSerializer):
    class Meta(BaseModelSerializer.Meta):
        model = ProductImage
