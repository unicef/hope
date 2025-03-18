from rest_framework import serializers

from hct_mis_api.apps.account.api.fields import Base64ModelField
from hct_mis_api.apps.core.models import BusinessArea, DataCollectingType


class BusinessAreaSerializer(serializers.ModelSerializer):
    id = Base64ModelField(model_name="BusinessArea")

    class Meta:
        model = BusinessArea
        fields = (
            "id",
            "name",
            "code",
            "long_name",
            "slug",
            "parent",
            "is_split",
            "active",
        )


class DataCollectingTypeSerializer(serializers.ModelSerializer):
    type = serializers.CharField(source="get_type_display")

    class Meta:
        model = DataCollectingType
        fields = (
            "id",
            "label",
            "code",
            "type",
            "household_filters_available",
            "individual_filters_available",
        )
