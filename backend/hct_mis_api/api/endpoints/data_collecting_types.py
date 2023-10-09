from typing import List

from rest_framework import mixins, serializers
from rest_framework.viewsets import GenericViewSet

from hct_mis_api.apps.core.models import DataCollectingType


class DataCollectingTypeSerializer(serializers.ModelSerializer):
    limit_to = serializers.SerializerMethodField()

    class Meta:
        model = DataCollectingType
        fields = (
            "id",
            "label",
            "code",
            "description",
            "active",
            "individual_filters_available",
            "household_filters_available",
            "recalculate_composition",
            "compatible_types",
            "limit_to",
        )

    def get_limit_to(self, obj: DataCollectingType) -> List[str]:
        return list(obj.limit_to.all().values_list("slug", flat=True))


class DataCollectingTypeViewSet(mixins.ListModelMixin, GenericViewSet):
    queryset = DataCollectingType.objects.all().order_by("code")
    serializer_class = DataCollectingTypeSerializer
