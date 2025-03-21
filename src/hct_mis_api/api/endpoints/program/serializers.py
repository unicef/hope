from rest_framework import serializers

from hct_mis_api.apps.program.models import Program


class ProgramGlobalSerializer(serializers.ModelSerializer):
    business_area_code = serializers.CharField(source="business_area.code", read_only=True)

    class Meta:
        model = Program
        fields = (
            "id",
            "name",
            "programme_code",
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
        )
