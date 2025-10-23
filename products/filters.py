from django_filters.rest_framework import FilterSet, CharFilter
from .models import ProductSKU

class ProductSKUFilter(FilterSet):
    product__name = CharFilter(field_name="product__name", lookup_expr="icontains")

    class Meta:
        model = ProductSKU
        fields = ["product__name"]
