from rest_framework import serializers

from hct_mis_api.apps.geo.models import Area


class AreaListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Area
        fields = ("id", "name", "p_code")


class AreaLevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Area
        fields = ("id", "level")
