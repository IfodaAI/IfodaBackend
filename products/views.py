from rest_framework.viewsets import ModelViewSet
from users.models import User,TelegramUser,Branch
from orders.models import Order
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser

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
            queryset=queryset.filter(name__icontains=name)
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

    def get_queryset(self):
        queryset = super().get_queryset()
        ids = self.request.query_params.get("ids")

        if ids:
            # ids=[1,2,3] yoki ids=1,2,3 formatda kelsa ham ishlaydi
            import json
            try:
                # Agar format ids=[1,2,3] bo‘lsa
                ids_list = json.loads(ids)
            except json.JSONDecodeError:
                # Agar format ids=1,2,3 bo‘lsa
                ids_list = ids.split(",")

            queryset = queryset.filter(id__in=ids_list)

        return queryset
        
class ProductImageViewSet(ModelViewSet):
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer
    filterset_fields=["product"]


class StatisticsAPIView(APIView):
    permission_classes=[IsAdminUser]

    def get(self, request):
        data = {
            "users": User.objects.count(),
            "telegram_users": TelegramUser.objects.count(),
            "orders": Order.objects.count(),
            "products": Product.objects.count(),
            "product_skus": ProductSKU.objects.count(),
            "diseases": Disease.objects.count(),
            "branches": Branch.objects.count(),
        }

        return Response(data, status=200)