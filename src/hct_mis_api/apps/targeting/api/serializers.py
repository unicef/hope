from typing import Any

from rest_framework import serializers

from hct_mis_api.apps.core.api.serializers import FieldAttributeSerializer

from hct_mis_api.apps.core.models import FlexibleAttribute
from hct_mis_api.apps.payment.models import PaymentPlan
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.targeting.api.utils import get_field_by_name, filter_choices
from hct_mis_api.apps.targeting.choices import FlexFieldClassification
from hct_mis_api.apps.targeting.models import (
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
    field_attribute = serializers.SerializerMethodField()

    class Meta:
        model = TargetingIndividualBlockRuleFilter
        fields = (
            "comparison_method",
            "flex_field_classification",
            "field_name",
            "arguments",
            "round_number",
            "field_attribute",
        )

    def get_field_attribute(self, obj: TargetingCriteriaRuleFilter) -> Any:
        if obj.flex_field_classification == FlexFieldClassification.NOT_FLEX_FIELD:
            field_attribute = get_field_by_name(
                obj.field_name, obj.individuals_filters_block.targeting_criteria_rule.payment_plan
            )
            result = filter_choices(field_attribute, obj.arguments)
            return FieldAttributeSerializer(result).data
        program = None
        if obj.flex_field_classification == FlexFieldClassification.FLEX_FIELD_PDU:
            request = self.context["request"]
            business_area_slug = request.parser_context["kwargs"]["business_area_slug"]
            program_slug = request.parser_context["kwargs"]["program_slug"]
            program = Program.objects.get(slug=program_slug, business_area__slug=business_area_slug)
        return FieldAttributeSerializer(FlexibleAttribute.objects.get(name=obj.field_name, program=program)).data


class TargetingIndividualRuleFilterBlockSerializer(serializers.ModelSerializer):
    individual_block_filters = TargetingIndividualBlockRuleFilterSerializer(many=True)

    class Meta:
        model = TargetingIndividualRuleFilterBlock
        fields = (
            "target_only_hoh",
            "individual_block_filters",
        )

    def to_representation(self, instance: TargetingCriteriaRule) -> dict:
        data = super().to_representation(instance)
        data["individual_block_filters"] = TargetingIndividualBlockRuleFilterSerializer(
            instance.individual_block_filters,
            many=True,
            context=self.context,
        ).data
        return data


class TargetingCriteriaRuleFilterSerializer(serializers.ModelSerializer):
    field_attribute = serializers.SerializerMethodField()

    class Meta:
        model = TargetingCriteriaRuleFilter
        fields = (
            "comparison_method",
            "flex_field_classification",
            "field_name",
            "arguments",
            "round_number",
            "field_attribute",
        )

    def get_field_attribute(self, obj: TargetingCriteriaRuleFilter) -> Any:
        if obj.flex_field_classification == FlexFieldClassification.NOT_FLEX_FIELD:
            field_attribute = get_field_by_name(obj.field_name, obj.targeting_criteria_rule.payment_plan)
            result = filter_choices(field_attribute, obj.arguments)
            return FieldAttributeSerializer(result).data
        program = None
        if obj.flex_field_classification == FlexFieldClassification.FLEX_FIELD_PDU:
            request = self.context["request"]
            business_area_slug = request.parser_context["kwargs"]["business_area_slug"]
            program_slug = request.parser_context["kwargs"]["program_slug"]
            program = Program.objects.get(slug=program_slug, business_area__slug=business_area_slug)
        return FieldAttributeSerializer(FlexibleAttribute.objects.get(name=obj.field_name, program=program)).data


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
            data["households_filters_blocks"] = TargetingCriteriaRuleFilterSerializer(
                filters_data,
                many=True,
                context=self.context,
            ).data
        data["individuals_filters_blocks"] = TargetingIndividualRuleFilterBlockSerializer(
            instance.individuals_filters_blocks,
            many=True,
            context=self.context,
        ).data
        return data
