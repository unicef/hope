from typing import Any

from rest_framework import serializers

from hope.contrib.vision.models import FundsCommitmentItem


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
        return {
            "businessArea": data["business_area"],
            "vendorNumber": data["vendor_number"],
            "payplanSno": data["payplan_sno"],
            "payplanDesc": data["payplan_desc"],
            "currency": data["currency"],
            "authAmt": data["auth_amt"],
            "authAmtUsd": data["auth_amt_usd"],
            "status": data["status"],
            "headVendor": data["head_vendor"],
            "creationDate": data["creation_date"],
        }
