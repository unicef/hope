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
