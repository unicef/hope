from rest_framework import serializers

from hope.contrib.vision.models import FundsCommitmentItem


class FundsCommitmentItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = FundsCommitmentItem
        fields = [
            "id",
            "rec_serial_number",
            "funds_commitment_item"
        ]


class FundsCommitmentSerializer(serializers.Serializer):
    funds_commitment_number = serializers.CharField()
    funds_commitment_items = FundsCommitmentItemSerializer(many=True)
