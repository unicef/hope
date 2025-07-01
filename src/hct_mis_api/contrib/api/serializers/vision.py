from rest_framework import serializers

from hct_mis_api.contrib.vision.models import FundsCommitmentItem


class FundsCommitmentItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = FundsCommitmentItem
        fields = "__all__"


class FundsCommitmentSerializer(serializers.Serializer):
    funds_commitment_number = serializers.CharField()
    funds_commitment_items = FundsCommitmentItemSerializer(many=True)
