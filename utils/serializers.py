from rest_framework.serializers import ModelSerializer


class BaseModelSerializer(ModelSerializer):
    """
    Barcha serializer'lar uchun asosiy klass.

    MUHIM: Child klasslar fields ni aniq ko'rsatishi SHART.
    `fields = "__all__"` ishlatmang - xavfsizlik uchun!
    """

    class Meta:
        abstract = True
        # fields ni child klasslar aniq ko'rsatishi kerak
        read_only_fields = (
            "id",
            "created_date",
            "updated_date",
            "created_by",
            "updated_by",
        )
