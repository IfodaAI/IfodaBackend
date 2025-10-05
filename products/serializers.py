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
from rest_framework.serializers import SerializerMethodField
from users.models import TelegramUser


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
    product_skus = SerializerMethodField()
    class Meta(BaseModelSerializer.Meta):
        model = Product
    
    def __init__(self, *args, **kwargs):
        super(ProductSerializer, self).__init__(*args, **kwargs)
        request: HttpRequest = self.context.get("request")
        if request and request.method == "GET":
            # product_skus = request.GET.get("product_skus")
            product_images = request.GET.get("product_images")
            category = request.GET.get("category")
            # if product_skus == "true":
            #     self.fields["product_skus"] = ProductSKUSerializer(context=self.context,many=True)
            if product_images == "true":
                self.fields["product_images"] = ProductImageSerializer(context=self.context,many=True)
            if category == "true":
                self.fields["category"] = ProductSubcategorySerializer(context=self.context)

    def get_product_skus(self, obj):
        request:HttpRequest = self.context.get("request")
        if not request:
            return []

        # Faqat GET methodda ishlaymiz
        if request.method != "GET":
            return []

        # Agar query param orqali filter berilsa:
        telegram_id = request.GET.get("telegram_id")

        # Filterni quramiz
        skus = obj.product_skus.all()
        if telegram_id:
            tg_user=TelegramUser.objects.get(telegram_id=telegram_id)
            if not tg_user.region.small_package and not tg_user.district.small_package:
                skus = skus.filter(is_small_package=False)

        # Natijani serialize qilamiz
        serializer = ProductSKUSerializer(skus, many=True, context=self.context)
        return serializer.data

class ProductSKUSerializer(BaseModelSerializer):
    class Meta(BaseModelSerializer.Meta):
        model = ProductSKU
        depth=1

class ProductImageSerializer(BaseModelSerializer):
    class Meta(BaseModelSerializer.Meta):
        model = ProductImage
