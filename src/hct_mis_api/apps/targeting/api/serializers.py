from rest_framework import serializers

from hct_mis_api.api.utils import EncodedIdSerializerMixin
from hct_mis_api.apps.targeting.models import TargetPopulation


class TargetPopulationListSerializer(EncodedIdSerializerMixin):
    status = serializers.CharField(source="get_status_display")
    created_by = serializers.CharField(source="created_by.get_full_name", default="")

    class Meta:
        model = TargetPopulation
        fields = (
            "id",
            "name",
            "status",
            "created_by",
            "created_at",
        )
