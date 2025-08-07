from rest_framework import serializers

from hope.apps.payment.models import PaymentPlan
from hope.apps.targeting.models import (
    TargetingCollectorBlockRuleFilter,
    TargetingCollectorRuleFilterBlock,
    TargetingCriteriaRule,
    TargetingCriteriaRuleFilter,
    TargetingIndividualBlockRuleFilter,
    TargetingIndividualRuleFilterBlock,
)


class TargetPopulationListSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField(method_name="get_status")
    created_by = serializers.CharField(source="created_by.get_full_name", default="")

    class Meta:
        model = PaymentPlan
        fields = (
            "id",
            "name",
            "status",
            "created_by",
            "created_at",
            "total_households_count",
            "total_individuals_count",
            "updated_at",
        )

    @staticmethod
    def get_status(obj: PaymentPlan) -> str:
        return obj.get_status_display().upper() if obj.status in PaymentPlan.PRE_PAYMENT_PLAN_STATUSES else "ASSIGNED"


class TargetingCollectorBlockRuleFilterSerializer(serializers.ModelSerializer):
    class Meta:
        model = TargetingCollectorBlockRuleFilter
        fields = (
            "comparison_method",
            "flex_field_classification",
            "field_name",
            "arguments",
        )


class TargetingCollectorRuleFilterBlockSerializer(serializers.ModelSerializer):
    collector_block_filters = TargetingCollectorBlockRuleFilterSerializer(many=True)

    class Meta:
        model = TargetingCollectorRuleFilterBlock
        fields = ("collector_block_filters",)


class TargetingIndividualBlockRuleFilterSerializer(serializers.ModelSerializer):
    class Meta:
        model = TargetingIndividualBlockRuleFilter
        fields = (
            "comparison_method",
            "flex_field_classification",
            "field_name",
            "arguments",
            "round_number",
        )


class TargetingIndividualRuleFilterBlockSerializer(serializers.ModelSerializer):
    individual_block_filters = TargetingIndividualBlockRuleFilterSerializer(many=True)

    class Meta:
        model = TargetingIndividualRuleFilterBlock
        fields = (
            "target_only_hoh",
            "individual_block_filters",
        )


class TargetingCriteriaRuleFilterSerializer(serializers.ModelSerializer):
    class Meta:
        model = TargetingCriteriaRuleFilter
        fields = (
            "comparison_method",
            "flex_field_classification",
            "field_name",
            "arguments",
            "round_number",
        )


class TargetingCriteriaRuleSerializer(serializers.ModelSerializer):
    households_filters_blocks = TargetingCriteriaRuleFilterSerializer(many=True, required=False)
    individuals_filters_blocks = TargetingIndividualRuleFilterBlockSerializer(many=True, required=False)
    collectors_filters_blocks = TargetingCollectorRuleFilterBlockSerializer(many=True, required=False)

    class Meta:
        model = TargetingCriteriaRule
        fields = (
            "household_ids",
            "individual_ids",
            "households_filters_blocks",
            "individuals_filters_blocks",
            "collectors_filters_blocks",
        )

    def to_representation(self, instance: TargetingCriteriaRule) -> dict:
        data = super().to_representation(instance)
        filters_data = instance.filters if hasattr(instance, "filters") else {}
        if filters_data:
            data["households_filters_blocks"] = TargetingCriteriaRuleFilterSerializer(filters_data, many=True).data

        return data
