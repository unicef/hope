from rest_framework import serializers

from hope.contrib.vision.models import FundsCommitmentItem
from hope.models import PaymentPlan


class FundsCommitmentItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = FundsCommitmentItem
        fields = [
            "wbs_element",
            "grant_number",
            "currency_code",
            "commitment_amount_local",
            "commitment_amount_usd",
            "total_open_amount_local",
            "total_open_amount_usd",
            "rec_serial_number",
            "funds_commitment_item",
            "sponsor",
            "sponsor_name",
        ]


class FundsCommitmentSerializer(serializers.Serializer):
    funds_commitment_number = serializers.CharField()
    funds_commitment_items = FundsCommitmentItemSerializer(many=True)


class PaymentPlanCallbackSerializer(serializers.Serializer):
    payment_plan_id = serializers.UUIDField()
    status = serializers.ChoiceField(
        choices=[choice.value for choice in PaymentPlan.Status],
        required=False,
    )
    comment = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    funds_commitment_number = serializers.CharField(required=False, allow_null=True)
    funds_commitment_items = serializers.ListField(
        child=serializers.CharField(),
        required=False,
    )
