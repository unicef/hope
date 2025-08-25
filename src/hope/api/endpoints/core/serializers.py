from rest_framework import serializers

from models.core import BusinessArea


class BusinessAreaSerializer(serializers.ModelSerializer):
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
