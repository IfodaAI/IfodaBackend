from django.urls import path, include

from rest_framework import routers

from .views import DiseaseCategoryViewSet, DiseaseViewSet, ProductViewSet, ProductCategoryViewSet, ProductSubcategoryViewSet, ProductSKUViewSet, ProductImageViewSet

router = routers.DefaultRouter()

router.register(r"disease-categories", DiseaseCategoryViewSet)
router.register(r"diseases", DiseaseViewSet)
router.register(r"product-categories", ProductCategoryViewSet)
router.register(r"product-subcategories", ProductSubcategoryViewSet)
router.register(r"products", ProductViewSet)
router.register(r"product-skus", ProductSKUViewSet)
router.register(r"product-images", ProductImageViewSet)

urlpatterns = [path("", include(router.urls))]
