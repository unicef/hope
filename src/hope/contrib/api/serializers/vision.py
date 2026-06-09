from typing import Any

from rest_framework import serializers

from hope.apps.core.utils import to_camel_case
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


class PaymentPlanCallbackResponseSerializer(serializers.Serializer):
    business_area = serializers.CharField()
    vendor_number = serializers.CharField()
    payplan_sno = serializers.CharField()
    payplan_desc = serializers.CharField()
    currency = serializers.CharField()
    auth_amt = serializers.CharField()
    auth_amt_usd = serializers.CharField()
    status = serializers.CharField()
    head_vendor = serializers.CharField()
    creation_date = serializers.CharField()

    def to_representation(self, instance: Any) -> dict[str, Any]:
        data = super().to_representation(instance)
        return {to_camel_case(k): v for k, v in data.items()}


class PaymentPlanPayloadSerializer(serializers.Serializer):
    business_area = serializers.CharField(source="business_area.code")
    vendor_number = serializers.CharField(source="financial_service_provider.vision_vendor_number")
    payplan_sno = serializers.CharField(source="unicef_id")
    payplan_desc = serializers.CharField(source="name")
    currency = serializers.CharField(source="currency.code")
    auth_amt = serializers.CharField(source="total_entitled_quantity")
    auth_amt_usd = serializers.CharField(source="total_entitled_quantity_usd")
    status = serializers.CharField()
    head_vendor = serializers.CharField(source="financial_service_provider.name")
    creation_date = serializers.SerializerMethodField()

    def get_creation_date(self, obj: PaymentPlan) -> str:
        return obj.created_at.strftime("%Y%m%d")

    def to_representation(self, instance: Any) -> dict[str, Any]:
        data = super().to_representation(instance)
        return {to_camel_case(k): v for k, v in data.items()}
