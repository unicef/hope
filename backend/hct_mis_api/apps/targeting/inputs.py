import graphene

from hct_mis_api.apps.targeting.graphql_types import TargetingCriteriaObjectType


class CopyTargetPopulationInput(graphene.InputObjectType):
    """All attribute inputs to create a new entry."""

    id = graphene.ID()
    name = graphene.String()


class UpdateTargetPopulationInput(graphene.InputObjectType):
    id = graphene.ID(required=True)
    name = graphene.String()
    targeting_criteria = TargetingCriteriaObjectType()
    program_id = graphene.ID()
    vulnerability_score_min = graphene.Decimal()
    vulnerability_score_max = graphene.Decimal()
    excluded_ids = graphene.String()
    exclusion_reason = graphene.String()


class CreateTargetPopulationInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    targeting_criteria = TargetingCriteriaObjectType(required=True)
    business_area_slug = graphene.String(required=True)
    program_id = graphene.ID(required=True)
    excluded_ids = graphene.String(required=True)
    exclusion_reason = graphene.String()
