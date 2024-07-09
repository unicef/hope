from rest_framework import serializers

from hct_mis_api.apps.core.models import BusinessArea


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
