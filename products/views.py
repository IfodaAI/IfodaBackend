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
    filterset_fields=["category"]

class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        name=request.GET.get("name")
        if name:
            queryset=queryset.filter(name__contains=name)
        category=request.GET.get("category")
        if category:
            queryset=queryset.filter(category__category__id=category)
        subcategory=request.GET.get("subcategory")
        if subcategory:
            queryset=queryset.filter(category__id=subcategory)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class ProductSKUViewSet(ModelViewSet):
    queryset = ProductSKU.objects.all()
    serializer_class = ProductSKUSerializer
    filterset_fields=["product"]

class ProductImageViewSet(ModelViewSet):
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer
    filterset_fields=["product"]
