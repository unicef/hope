from typing import Optional

from rest_framework import serializers

from hct_mis_api.apps.account.api.fields import Base64ModelField
from hct_mis_api.apps.payment.models import PaymentPlan


class FollowUpPaymentPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentPlan
        fields = (
            "id",
            "unicef_id",
        )


class PaymentPlanSerializer(serializers.ModelSerializer):
    id = Base64ModelField(model_name="PaymentPlan")
    status = serializers.CharField(source="get_status_display")
    target_population = serializers.CharField(source="target_population.name")
    currency = serializers.CharField(source="get_currency_display")
    follow_ups = FollowUpPaymentPlanSerializer(many=True, read_only=True)
    program = serializers.CharField(source="program.name")
    program_id = Base64ModelField(model_name="Program")
    last_approval_process_by = serializers.SerializerMethodField()

    class Meta:
        model = PaymentPlan
        fields = (
            "id",
            "unicef_id",
            "name",
            "status",
            "target_population",
            "total_households_count",
            "currency",
            "total_entitled_quantity",
            "total_delivered_quantity",
            "total_undelivered_quantity",
            "dispersion_start_date",
            "dispersion_end_date",
            "is_follow_up",
            "follow_ups",
            "program",
            "program_id",
            "last_approval_process_date",
            "last_approval_process_by",
        )

    def get_last_approval_process_by(self, obj: PaymentPlan) -> Optional[str]:
        return str(obj.last_approval_process_by) if obj.last_approval_process_by else None


class PaymentPlanBulkActionSerializer(serializers.Serializer):
    ids = serializers.ListField(child=serializers.CharField())
    action = serializers.ChoiceField(PaymentPlan.Action.choices)
    comment = serializers.CharField(required=False, allow_blank=True)
