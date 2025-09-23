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
from django.http import HttpRequest

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
    
    def __init__(self, *args, **kwargs):
        super(ProductSerializer, self).__init__(*args, **kwargs)
        request: HttpRequest = self.context.get("request")
        if request and request.method == "GET":
            product_skus = request.GET.get("product_skus")
            if product_skus == "true":
                self.fields["product_skus"] = ProductSKUSerializer(context=self.context,many=True)
            product_images = request.GET.get("product_images")
            if product_images == "true":
                self.fields["product_images"] = ProductImageSerializer(context=self.context,many=True)

class ProductSKUSerializer(BaseModelSerializer):
    class Meta(BaseModelSerializer.Meta):
        model = ProductSKU

class ProductImageSerializer(BaseModelSerializer):
    class Meta(BaseModelSerializer.Meta):
        model = ProductImage
