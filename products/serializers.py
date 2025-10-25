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
    class Meta(BaseModelSerializer.Meta):
        model = Product

    def __init__(self, *args, **kwargs):
        super(ProductSerializer, self).__init__(*args, **kwargs)
        request: HttpRequest = self.context.get("request")

        if not request or request.method != "GET":
            return  # faqat GET bo‘lsa ishlasin

        product_skus = request.GET.get("product_skus")
        product_images = request.GET.get("product_images")
        category = request.GET.get("category")

        # === product_skus faqat true bo‘lgandagina qo‘shiladi ===
        if not product_skus == "true":
            # ya’ni product_skus field umuman chiqmaydi
            pass
        else:
            self.fields["product_skus"] = SerializerMethodField()

            def get_product_skus(inner_self, obj):
                telegram_id = request.GET.get("telegram_id")
                skus = obj.product_skus.all()

                if telegram_id:
                    try:
                        tg_user = TelegramUser.objects.get(telegram_id=telegram_id)
                        if not tg_user.region.small_package and not tg_user.district.small_package:
                            skus = skus.filter(is_small_package=False)
                    except TelegramUser.DoesNotExist:
                        pass

                return ProductSKUSerializer(skus, many=True, context=self.context).data

            setattr(self.__class__, "get_product_skus", get_product_skus)

        # === boshqa fieldlar ham shart bilan qo‘shiladi ===
        if product_images == "true":
            self.fields["product_images"] = ProductImageSerializer(context=self.context, many=True)

        if category == "true":
            self.fields["category"] = ProductSubcategorySerializer(context=self.context)

# class ProductSKUSerializer(BaseModelSerializer):
#     class Meta(BaseModelSerializer.Meta):
#         model = ProductSKU
#         depth=1
class ProductSKUSerializer(BaseModelSerializer):
    class Meta(BaseModelSerializer.Meta):
        model = ProductSKU
        depth = 0  # default chuqurlik

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get("request")

        if request and request.method == "GET":
            self.Meta.depth = 1
        else:
            self.Meta.depth = 0

class ProductImageSerializer(BaseModelSerializer):
    class Meta(BaseModelSerializer.Meta):
        model = ProductImage
