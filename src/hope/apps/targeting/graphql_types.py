import uuid
from typing import TYPE_CHECKING, Any

import graphene
from graphene_django import DjangoObjectType

import hope.apps.targeting.models as target_models
from hope.apps.core.field_attributes.core_fields_attributes import FieldFactory
from hope.apps.core.field_attributes.fields_types import Scope
from hope.apps.core.models import FlexibleAttribute
from hope.apps.core.schema import FieldAttributeNode
from hope.apps.core.utils import decode_id_string
from hope.apps.payment.models import AccountType, PaymentPlan
from hope.apps.program.models import Program
from hope.apps.targeting.choices import FlexFieldClassification
from hope.apps.utils.schema import Arg

if TYPE_CHECKING:
    from django.db.models.query import QuerySet
    from graphene.types.structures import List as GrapheneList

    from hope.apps.targeting.models import TargetingIndividualRuleFilterBlock


def get_field_by_name(field_name: str, payment_plan: PaymentPlan) -> dict:
    scopes = [Scope.TARGETING]
    if payment_plan.is_social_worker_program:
        scopes.append(Scope.XLSX_PEOPLE)
    factory = FieldFactory.from_only_scopes(scopes)
    factory.apply_business_area(payment_plan.business_area.slug)
    field = factory.to_dict_by("name")[field_name]
    choices = field.get("choices") or field.get("_choices")
    if choices and callable(choices):
        field["choices"] = choices()
    field["id"] = uuid.uuid4()
    return field


def filter_choices(field: dict | None, args: list) -> dict | None:
    if not field:
        return None
    choices = field.get("choices")
    if args and choices:
        field["choices"] = list(filter(lambda choice: str(choice["value"]) in args, choices))
    return field


class FlexFieldClassificationChoices(graphene.Enum):
    NOT_FLEX_FIELD = "NOT_FLEX_FIELD"
    FLEX_FIELD_BASIC = "FLEX_FIELD_BASIC"
    FLEX_FIELD_PDU = "FLEX_FIELD_PDU"


class TargetingCriteriaRuleFilterNode(DjangoObjectType):
    arguments = graphene.List(Arg)
    field_attribute = graphene.Field(FieldAttributeNode)

    def resolve_arguments(self, info: Any) -> "GrapheneList":
        return self.arguments

    def resolve_field_attribute(parent, info: Any) -> dict | None:
        if parent.flex_field_classification == FlexFieldClassification.NOT_FLEX_FIELD:
            field_attribute = get_field_by_name(parent.field_name, parent.targeting_criteria_rule.payment_plan)
            return filter_choices(
                field_attribute,
                parent.arguments,  # type: ignore # can't convert graphene list to list
            )
        program = None
        if parent.flex_field_classification == FlexFieldClassification.FLEX_FIELD_PDU:
            encoded_program_id = info.context.headers.get("Program")
            program = Program.objects.get(id=decode_id_string(encoded_program_id))
        return FlexibleAttribute.objects.get(name=parent.field_name, program=program)

    class Meta:
        model = target_models.TargetingCriteriaRuleFilter


class TargetingIndividualBlockRuleFilterNode(DjangoObjectType):
    arguments = graphene.List(Arg)
    field_attribute = graphene.Field(FieldAttributeNode)

    def resolve_arguments(self, info: Any) -> "GrapheneList":
        return self.arguments

    def resolve_field_attribute(parent, info: Any) -> Any:
        if parent.flex_field_classification == FlexFieldClassification.NOT_FLEX_FIELD:
            field_attribute = get_field_by_name(
                parent.field_name,
                parent.individuals_filters_block.targeting_criteria_rule.payment_plan,
            )
            return filter_choices(field_attribute, parent.arguments)  # type: ignore # can't convert graphene list to list

        program = None
        if parent.flex_field_classification == FlexFieldClassification.FLEX_FIELD_PDU:
            encoded_program_id = info.context.headers.get("Program")
            program = Program.objects.get(id=decode_id_string(encoded_program_id))
        return FlexibleAttribute.objects.get(name=parent.field_name, program=program)

    class Meta:
        model = target_models.TargetingIndividualBlockRuleFilter


class TargetingCollectorBlockRuleFilterNode(DjangoObjectType):
    arguments = graphene.List(Arg)
    comparison_method = graphene.String()
    label_en = graphene.String()

    def resolve_arguments(parent, info: Any) -> "GrapheneList":
        return parent.arguments

    def resolve_label_en(parent, info: Any) -> str:
        field_labels_dict = {
            field: field.replace("__", " ").title() for field in AccountType.get_targeting_field_names()
        }
        return field_labels_dict.get(parent.field_name, "")

    class Meta:
        model = target_models.TargetingCollectorBlockRuleFilter


class TargetingIndividualRuleFilterBlockNode(DjangoObjectType):
    individual_block_filters = graphene.List(TargetingIndividualBlockRuleFilterNode)

    def resolve_individual_block_filters(parent, info: Any) -> "QuerySet":
        return parent.individual_block_filters.all()

    class Meta:
        model = target_models.TargetingIndividualRuleFilterBlock


class TargetingCollectorRuleFilterBlockNode(DjangoObjectType):
    collector_block_filters = graphene.List(TargetingCollectorBlockRuleFilterNode)

    def resolve_collector_block_filters(parent, info: Any) -> "QuerySet":
        return parent.collector_block_filters.all()

    class Meta:
        model = target_models.TargetingCollectorRuleFilterBlock


class TargetingCriteriaRuleNode(DjangoObjectType):
    households_filters_blocks = graphene.List(TargetingCriteriaRuleFilterNode)
    individuals_filters_blocks = graphene.List(TargetingIndividualRuleFilterBlockNode)

    def resolve_individuals_filters_blocks(self, info: Any) -> "QuerySet[TargetingIndividualRuleFilterBlock]":
        return self.individuals_filters_blocks.all()

    def resolve_households_filters_blocks(self, info: Any) -> "QuerySet":
        return self.filters.all()

    class Meta:
        model = target_models.TargetingCriteriaRule
        exclude_fields = [
            "filters",
        ]


class TargetingCriteriaRuleFilterObjectType(graphene.InputObjectType):
    comparison_method = graphene.String(required=True)
    flex_field_classification = graphene.Field(FlexFieldClassificationChoices, required=True)
    field_name = graphene.String(required=True)
    arguments = graphene.List(Arg, required=True)
    round_number = graphene.Int()


class TargetingIndividualRuleFilterBlockObjectType(graphene.InputObjectType):
    individual_block_filters = graphene.List(TargetingCriteriaRuleFilterObjectType)


class TargetingCollectorRuleFilterBlockObjectType(graphene.InputObjectType):
    collector_block_filters = graphene.List(TargetingCriteriaRuleFilterObjectType)


class TargetingCriteriaRuleObjectType(graphene.InputObjectType):
    households_filters_blocks = graphene.List(TargetingCriteriaRuleFilterObjectType)
    household_ids = graphene.String()
    individuals_filters_blocks = graphene.List(TargetingIndividualRuleFilterBlockObjectType)
    individual_ids = graphene.String()
    collectors_filters_blocks = graphene.List(TargetingCollectorRuleFilterBlockObjectType)


class TargetingCriteriaObjectType(graphene.InputObjectType):
    rules = graphene.List(TargetingCriteriaRuleObjectType)
    flag_exclude_if_active_adjudication_ticket = graphene.Boolean()
    flag_exclude_if_on_sanction_list = graphene.Boolean()
