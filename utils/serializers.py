from rest_framework.serializers import ModelSerializer


class BaseModelSerializer(ModelSerializer):
    class Meta:
        abstract = True        
        fields = "__all__"
        read_only_fields = (
            "id",
            "created_date",
            "updated_date",
            "created_by",
            "updated_by",
        )
