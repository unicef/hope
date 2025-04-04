from rest_framework import serializers

from hct_mis_api.apps.account.api.fields import Base64ModelField
from hct_mis_api.apps.geo.models import Area


class AreaListSerializer(serializers.ModelSerializer):
    id = Base64ModelField(model_name="Area")

    class Meta:
        model = Area
        fields = ("id", "name", "p_code")


class AreaLevelSerializer(serializers.ModelSerializer):
    id = Base64ModelField(model_name="Area")

    class Meta:
        model = Area
        fields = ("id", "level")
