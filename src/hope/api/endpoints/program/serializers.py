from rest_framework import serializers

from hope.apps.program.api.serializers import PayeeTypeSerializer
from hope.models import Program


class ProgramGlobalSerializer(serializers.ModelSerializer):
    business_area_code = serializers.CharField(source="business_area.code", read_only=True)
    payee_type = PayeeTypeSerializer(source="data_collecting_type.payee_type", read_only=True)

    class Meta:
        model = Program
        fields = (
            "id",
            "name",
            "code",
            "status",
            "start_date",
            "end_date",
            "budget",
            "frequency_of_payments",
            "sector",
            "scope",
            "cash_plus",
            "population_goal",
            "business_area_code",
            "beneficiary_group",
            "payee_type",
            "biometric_deduplication_enabled",
        )
