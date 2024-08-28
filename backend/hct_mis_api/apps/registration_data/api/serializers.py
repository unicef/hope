from rest_framework import serializers

from hct_mis_api.api.utils import EncodedIdSerializerMixin
from hct_mis_api.apps.registration_data.models import RegistrationDataImport


class RegistrationDataImportListSerializer(EncodedIdSerializerMixin):
    status = serializers.CharField(source="get_status_display")
    data_source = serializers.CharField(source="get_data_source_display")
    imported_by = serializers.CharField(source="imported_by.get_full_name", default="")

    class Meta:
        model = RegistrationDataImport
        fields = (
            "id",
            "name",
            "status",
            "data_source",
            "imported_by",
            "created_at",
        )


class DeduplicationEngineStatusSerializer(serializers.Serializer):
    state = serializers.DecimalField(max_digits=5, decimal_places=2)
    error = serializers.CharField(required=False, allow_blank=True)
