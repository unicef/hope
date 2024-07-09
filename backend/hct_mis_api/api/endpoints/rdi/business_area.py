from rest_framework import serializers
from rest_framework.generics import ListAPIView

from hct_mis_api.api.endpoints.base import HOPEAPIView
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


class BusinessAreaViewSet(HOPEAPIView, ListAPIView):
    serializer_class = BusinessAreaSerializer
    queryset = BusinessArea.objects.all()
