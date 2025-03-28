from rest_framework import serializers

from hct_mis_api.api.utils import EncodedIdSerializerMixin
from hct_mis_api.apps.payment.models import PaymentPlan
from hct_mis_api.apps.targeting.models import (
    TargetingCollectorBlockRuleFilter,
    TargetingCollectorRuleFilterBlock,
    TargetingCriteria,
    TargetingCriteriaRule,
    TargetingCriteriaRuleFilter,
    TargetingIndividualBlockRuleFilter,
    TargetingIndividualRuleFilterBlock,
)


class TargetPopulationListSerializer(EncodedIdSerializerMixin):
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
        )

    @staticmethod
    def get_status(obj: PaymentPlan) -> str:
        if obj.status in PaymentPlan.PRE_PAYMENT_PLAN_STATUSES:
            return obj.get_status_display()
        else:
            return "Assigned"


class TargetingCollectorBlockRuleFilterSerializer(EncodedIdSerializerMixin):
    class Meta:
        model = TargetingCollectorBlockRuleFilter
        fields = (
            "id",
            "comparison_method",
            "flex_field_classification",
            "field_name",
            "arguments",
        )


class TargetingCollectorRuleFilterBlockSerializer(EncodedIdSerializerMixin):
    collector_block_filters = TargetingCollectorBlockRuleFilterSerializer(many=True, read_only=True)

    class Meta:
        model = TargetingCollectorRuleFilterBlock
        fields = ("id", "collector_block_filters")


class TargetingIndividualBlockRuleFilterSerializer(EncodedIdSerializerMixin):
    class Meta:
        model = TargetingIndividualBlockRuleFilter
        fields = (
            "id",
            "comparison_method",
            "flex_field_classification",
            "field_name",
            "arguments",
            "round_number",
        )


class TargetingIndividualRuleFilterBlockSerializer(EncodedIdSerializerMixin):
    individual_block_filters = TargetingIndividualBlockRuleFilterSerializer(many=True, read_only=True)

    class Meta:
        model = TargetingIndividualRuleFilterBlock
        fields = (
            "id",
            "target_only_hoh",
            "individual_block_filters",
        )


class TargetingCriteriaRuleFilterSerializer(EncodedIdSerializerMixin):
    class Meta:
        model = TargetingCriteriaRuleFilter
        fields = (
            "id",
            "comparison_method",
            "flex_field_classification",
            "field_name",
            "arguments",
            "round_number",
        )


class TargetingCriteriaRuleSerializer(EncodedIdSerializerMixin):
    filters = TargetingCriteriaRuleFilterSerializer(many=True, read_only=True)
    individuals_filters_blocks = TargetingIndividualRuleFilterBlockSerializer(many=True, read_only=True)
    collectors_filters_blocks = TargetingCollectorRuleFilterBlockSerializer(many=True, read_only=True)

    class Meta:
        model = TargetingCriteriaRule
        fields = (
            "id",
            "household_ids",
            "individual_ids",
            "filters",
            "individuals_filters_blocks",
            "collectors_filters_blocks",
        )


class TargetingCriteriaSerializer(EncodedIdSerializerMixin):
    rules = TargetingCriteriaRuleSerializer(many=True, read_only=True)

    class Meta:
        model = TargetingCriteria
        fields = (
            "id",
            "flag_exclude_if_active_adjudication_ticket",
            "flag_exclude_if_on_sanction_list",
            "rules",
        )
