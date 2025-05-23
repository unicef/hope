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
