from rest_framework.viewsets import ModelViewSet

from .models import (
    Disease,
    DiseaseCategory,
    Product,
    ProductCategory,
    ProductImage,
    ProductSKU,
    ProductSubcategory,
)
from .serializers import (
    DiseaseSerializer,
    DiseaseCategorySerializer,
    ProductCategorySerializer,
    ProductImageSerializer,
    ProductSKUSerializer,
    ProductSubcategorySerializer,
    ProductSerializer,
)


class DiseaseViewSet(ModelViewSet):
    queryset = Disease.objects.all()
    serializer_class = DiseaseSerializer


class DiseaseCategoryViewSet(ModelViewSet):
    queryset = DiseaseCategory.objects.all()
    serializer_class = DiseaseCategorySerializer


class ProductCategoryViewSet(ModelViewSet):
    queryset = ProductCategory.objects.all()
    serializer_class = ProductCategorySerializer


class ProductSubcategoryViewSet(ModelViewSet):
    queryset = ProductSubcategory.objects.all()
    serializer_class = ProductSubcategorySerializer


class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class ProductSKUViewSet(ModelViewSet):
    queryset = ProductSKU.objects.all()
    serializer_class = ProductSKUSerializer


class ProductImageViewSet(ModelViewSet):
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer
