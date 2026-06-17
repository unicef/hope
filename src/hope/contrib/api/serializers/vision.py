from typing import Any

from rest_framework import serializers

from hope.apps.core.utils import to_camel_case, to_snake_case
from hope.contrib.vision.models import FundsCommitmentItem
from hope.models import PaymentPlan

VISION_CALLBACK_FIELD_OVERRIDES = {
    "vision_payplanSno": "vision_payplan_sno",
    "vision_payplan_sno": "vision_payplanSno",
}


def vision_callback_internal_field_name(field_name: str) -> str:
    return VISION_CALLBACK_FIELD_OVERRIDES.get(field_name, to_snake_case(field_name))


def vision_callback_external_field_name(field_name: str) -> str:
    return VISION_CALLBACK_FIELD_OVERRIDES.get(field_name, to_camel_case(field_name))


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


class PaymentPlanCallbackRequestSerializer(serializers.Serializer):
    message_id = serializers.CharField(required=False, allow_blank=True)
    payplan_sno = serializers.CharField()
    vision_payplan_sno = serializers.CharField(required=False, allow_blank=True)
    status = serializers.CharField(required=False, allow_blank=True)
    fc_num = serializers.CharField(required=False, allow_blank=True)

    def to_internal_value(self, data: dict) -> dict[str, Any]:
        field_names: tuple[str, ...] = tuple(self.fields.keys())
        return super().to_internal_value(
            {field_name: data.get(vision_callback_external_field_name(field_name), "") for field_name in field_names}
        )

    def initial_value(self, field_name: str) -> Any:
        return self.initial_data.get(vision_callback_external_field_name(field_name), "")

    @property
    def initial_message_id(self) -> str:
        return self.initial_value("message_id")

    @property
    def initial_payplan_sno(self) -> str:
        return self.initial_value("payplan_sno")

    @property
    def validated_message_id(self) -> str:
        return self.validated_data.get("message_id", "")

    @property
    def validated_payplan_sno(self) -> str:
        return self.validated_data.get("payplan_sno", "")

    @property
    def validated_vision_payplan_sno(self) -> str:
        return self.validated_data.get("vision_payplan_sno", "")

    @property
    def external_payload(self) -> dict[str, Any]:
        return {
            vision_callback_external_field_name(field_name): value for field_name, value in self.validated_data.items()
        }

    def ack_payload(self, status: str) -> dict[str, Any]:
        validated_data = getattr(self, "_validated_data", {})
        return {
            "status": status,
            "message_id": validated_data.get("message_id") or self.initial_message_id,
            "payplan_sno": validated_data.get("payplan_sno") or self.initial_payplan_sno,
        }


class PaymentPlanCallbackAckSerializer(serializers.Serializer):
    status = serializers.CharField()
    message_id = serializers.CharField(allow_blank=True)
    payplan_sno = serializers.CharField(allow_blank=True)

    def to_representation(self, instance: Any) -> dict[str, Any]:
        data = super().to_representation(instance)
        return {vision_callback_external_field_name(field_name): value for field_name, value in data.items()}


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
