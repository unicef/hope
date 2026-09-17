from rest_framework import serializers
from timezone_field.rest_framework import TimeZoneSerializerField

from hope.models import BusinessArea


class BusinessAreaSerializer(serializers.ModelSerializer):
    timezone = TimeZoneSerializerField(read_only=True)

    class Meta:
        model = BusinessArea
        fields = (
            "id",
            "name",
            "code",
            "long_name",
            "slug",
            "timezone",
            "parent",
            "is_split",
            "active",
        )
