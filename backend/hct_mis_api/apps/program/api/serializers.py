from rest_framework import serializers

from hct_mis_api.api.utils import EncodedIdSerializerMixin
from hct_mis_api.apps.program.models import ProgramCycle


class ProgramCycleListSerializer(EncodedIdSerializerMixin):
    status = serializers.CharField(source="get_status_display")

    class Meta:
        model = ProgramCycle
        fields = (
            "id",
            "unicef_id",
            "title",
            "status",
            "start_date",
            "end_date",
            "created_at",
            "total_entitled_quantity_usd",
            "total_undelivered_quantity_usd",
            "total_delivered_quantity_usd",
        )
