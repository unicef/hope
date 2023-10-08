from typing import List

from rest_framework import serializers, mixins
from rest_framework.viewsets import GenericViewSet

from hct_mis_api.apps.core.models import DataCollectingType


class DataCollectingTypeSerializer(serializers.ModelSerializer):
    limit_to = serializers.SerializerMethodField()

    class Meta:
        model = DataCollectingType
        fields = "__all__"

    def get_limit_to(self, obj) -> List[str]:
        return list(obj.limit_to.all().values_list("slug", flat=True))


class DataCollectingTypeViewSet(mixins.ListModelMixin, GenericViewSet):
    queryset = DataCollectingType.objects.all()
    serializer_class = DataCollectingTypeSerializer
