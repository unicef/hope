from typing import Optional

from rest_framework import serializers

from hct_mis_api.apps.core.utils import encode_id_base64, encode_id_base64_required
from hct_mis_api.apps.payment.models import PaymentPlan


class FollowUpPaymentPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentPlan
        fields = (
            "id",
            "unicef_id",
        )


class PaymentPlanSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()
    status = serializers.CharField(source="get_status_display")
    target_population = serializers.CharField(source="target_population.name")
    currency = serializers.CharField(source="get_currency_display")
    follow_ups = FollowUpPaymentPlanSerializer(many=True, read_only=True)
    program = serializers.CharField(source="program.name")
    program_id = serializers.SerializerMethodField()

    class Meta:
        model = PaymentPlan
        fields = (
            "id",
            "unicef_id",
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
        )

    def get_program_id(self, obj):
        return encode_id_base64(obj.program.id, "Program")

    def get_id(self, obj) -> str:
        return encode_id_base64_required(str(obj.id), "PaymentPlan")


class PaymentPlanBulkActionSerializer(serializers.Serializer):
    ids = serializers.ListField(child=serializers.CharField())
    action = serializers.ChoiceField(PaymentPlan.Action.choices)
    comment = serializers.CharField(required=False)


class PaymentVerificationSerializer(serializers.Serializer):
    obj_type = serializers.SerializerMethodField()
    id = serializers.SerializerMethodField()
    unicef_id = serializers.CharField(source="get_unicef_id")
    verification_status = serializers.SerializerMethodField()
    status = serializers.CharField()
    currency = serializers.CharField()
    total_delivered_quantity = serializers.DecimalField(max_digits=20, decimal_places=2)
    start_date = serializers.CharField()
    end_date = serializers.CharField()
    program_name = serializers.CharField(source="program.name")
    updated_at = serializers.CharField()
    total_number_of_households = serializers.SerializerMethodField()
    total_entitled_quantity = serializers.DecimalField(max_digits=20, decimal_places=2)
    total_undelivered_quantity = serializers.DecimalField(max_digits=20, decimal_places=2)
    program_id = serializers.SerializerMethodField()

    def get_id(self, obj) -> str:
        return encode_id_base64_required(str(obj.id), obj.__class__.__name__)

    def get_obj_type(self, obj) -> str:
        return obj.__class__.__name__

    def get_total_number_of_households(self, obj) -> int:
        return obj.payment_items.count()

    def get_verification_status(self, obj) -> Optional[str]:
        return obj.get_payment_verification_summary.status if obj.get_payment_verification_summary else None

    def get_program_id(self, obj) -> str:
        return encode_id_base64(str(obj.program.id), "Program")
