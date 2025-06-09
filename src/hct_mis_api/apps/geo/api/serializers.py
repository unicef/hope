from typing import List

from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from hct_mis_api.apps.geo.models import Area


class AreaListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Area
        fields = ("id", "name", "p_code", "area_type", "updated_at")


class AreaLevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Area
        fields = ("id", "level")


class AreaSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Area
        fields = ("id", "name")


class AreaTreeSerializer(serializers.ModelSerializer):
    level = serializers.SerializerMethodField()
    areas = serializers.SerializerMethodField()

    class Meta:
        model = Area
        fields = (
            "id",
            "name",
            "p_code",
            "areas",
            "level",
        )

    @extend_schema_field(serializers.ListSerializer(child=serializers.Serializer()))
    def resolve_areas(self, obj: Area) -> List[Area]:
        return obj.get_children()

    @staticmethod
    def get_level(obj: Area) -> int:
        return obj.area_type.area_level

    def get_fields(self):
        fields = super().get_fields()
        fields["areas"] = AreaTreeSerializer(many=True)
        return fields
