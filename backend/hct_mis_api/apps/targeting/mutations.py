import graphene
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404

from core import utils
from core.permissions import is_authenticated
from core.utils import decode_id_string
from household.models import Household
from program.models import Program
from targeting.models import (
    TargetPopulation,
    HouseholdSelection,
    TargetingCriteria,
    TargetingCriteriaRule,
    TargetingCriteriaRuleFilter,
)
from targeting.schema import TargetPopulationNode, TargetingCriteriaObjectType
from targeting.validators import (
    TargetValidator,
    ApproveTargetPopulationValidator,
    FinalizeTargetPopulationValidator,
    UnapproveTargetPopulationValidator,
    TargetingCriteriaInputValidator,
)


class CopyTargetPopulationInput(graphene.InputObjectType):
    """All attribute inputs to create a new entry."""

    id = graphene.ID()
    name = graphene.String()


class CreateTarget:
    # TODO(codecakes): Implement
    pass


class ValidatedMutation(graphene.Mutation):
    arguments_validators = []
    object_validators = []

    model_class = None

    @classmethod
    @is_authenticated
    def mutate(cls, root, info, **kwargs):
        for validator in cls.arguments_validators:
            validator.validate(kwargs)
        model_object = cls.get_object(root, info, **kwargs)
        return cls.validated_mutate(
            root, info, model_object=model_object, **kwargs
        )

    @classmethod
    def get_object(cls, root, info, **kwargs):
        id = kwargs.get("id")
        if id is None:
            return None
        object = get_object_or_404(cls.model_class, id=decode_id_string(id))
        for validator in cls.object_validators:
            validator.validate(object)
        return object


class UpdateTargetPopulationInput(graphene.InputObjectType):

    id = graphene.ID(required=True)
    name = graphene.String()
    targeting_criteria = TargetingCriteriaObjectType()


class CreateTargetPopulationInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    targeting_criteria = TargetingCriteriaObjectType(required=True)


class CreateTargetPopulationMutation(graphene.Mutation):
    target_population = graphene.Field(TargetPopulationNode)

    class Arguments:
        input = CreateTargetPopulationInput(required=True)

    @classmethod
    @is_authenticated
    @transaction.atomic
    def mutate(cls, root, info, **kwargs):
        user = info.context.user
        input = kwargs.pop("input")

        targeting_criteria_input = input.get("targeting_criteria")
        TargetingCriteriaInputValidator.validate(targeting_criteria_input)
        targeting_criteria = TargetingCriteria()
        targeting_criteria.save()
        for rule_input in targeting_criteria_input.get("rules"):
            rule = TargetingCriteriaRule(targeting_criteria=targeting_criteria)
            rule.save()
            for filter_input in rule_input.get("filters"):
                rule_filter = TargetingCriteriaRuleFilter(
                    targeting_criteria_rule=rule, **filter_input
                )
                rule_filter.save()
        target_population = TargetPopulation(
            name=input.get("name"), created_by=user,
        )
        target_population.candidate_list_targeting_criteria = targeting_criteria
        target_population.save()
        return cls(target_population=target_population)


class UpdateTargetPopulationMutation(graphene.Mutation):
    target_population = graphene.Field(TargetPopulationNode)

    class Arguments:
        input = UpdateTargetPopulationInput(required=True)

    @classmethod
    @is_authenticated
    @transaction.atomic
    def mutate(cls, root, info, **kwargs):
        input = kwargs.get("input")
        id = input.get("id")
        target_population = cls.get_object(id)
        name = input.get("name")
        if target_population.status == "APPROVED" and name:
            raise ValidationError(
                "Name can't be changed when Target Population is in APPROVED status"
            )
        if target_population.status == "FINALIZED":
            raise ValidationError(
                "Finalized Target Population can't be changed"
            )
        if name:
            target_population.name = name
        targeting_criteria_input = input.get("targeting_criteria")
        TargetingCriteriaInputValidator.validate(targeting_criteria_input)
        if targeting_criteria_input:
            targeting_criteria = TargetingCriteria()
            targeting_criteria.save()
            for rule_input in targeting_criteria_input.get("rules"):
                rule = TargetingCriteriaRule(
                    targeting_criteria=targeting_criteria
                )
                rule.save()
                for filter_input in rule_input.get("filters"):
                    rule_filter = TargetingCriteriaRuleFilter(
                        targeting_criteria_rule=rule, **filter_input
                    )
                    rule_filter.save()
            if target_population.status == "DRAFT":
                if target_population.candidate_list_targeting_criteria:
                    target_population.candidate_list_targeting_criteria.delete()
                target_population.candidate_list_targeting_criteria = (
                    targeting_criteria
                )
            elif target_population.status == "APPROVED":
                if target_population.final_list_targeting_criteria:
                    target_population.final_list_targeting_criteria.delete()
                target_population.final_list_targeting_criteria = (
                    targeting_criteria
                )
        target_population.save()
        return cls(target_population=target_population)

    @classmethod
    def get_object(cls, id):
        if id is None:
            return None
        object = get_object_or_404(TargetPopulation, id=decode_id_string(id))
        return object


class ApproveTargetPopulationMutation(ValidatedMutation):
    target_population = graphene.Field(TargetPopulationNode)
    object_validators = [ApproveTargetPopulationValidator]
    model_class = TargetPopulation

    class Arguments:
        id = graphene.ID(required=True)
        program_id = graphene.ID(required=True)

    @classmethod
    @transaction.atomic
    def validated_mutate(cls, root, info, **kwargs):
        program = get_object_or_404(
            Program, pk=decode_id_string(kwargs.get("program_id"))
        )
        target_population = kwargs.get("model_object")
        target_population.status = "APPROVED"
        households = Household.objects.filter(
            target_population.candidate_list_targeting_criteria.get_query()
        )
        target_population.households.set(households)
        target_population.program = program
        target_population.save()
        return cls(target_population=target_population)


class UnapproveTargetPopulationMutation(ValidatedMutation):
    target_population = graphene.Field(TargetPopulationNode)
    object_validators = [UnapproveTargetPopulationValidator]
    model_class = TargetPopulation

    class Arguments:
        id = graphene.ID(required=True)

    @classmethod
    def validated_mutate(cls, root, info, **kwargs):
        target_population = kwargs.get("model_object")
        target_population.status = "DRAFT"
        target_population.save()
        return cls(target_population=target_population)


class FinalizeTargetPopulationMutation(ValidatedMutation):
    target_population = graphene.Field(TargetPopulationNode)
    object_validators = [FinalizeTargetPopulationValidator]
    model_class = TargetPopulation

    class Arguments:
        id = graphene.ID(required=True)

    @classmethod
    @transaction.atomic
    def validated_mutate(cls, root, info, **kwargs):
        target_population = kwargs.get("model_object")
        target_population.status = "FINALIZED"
        if target_population.final_list_targeting_criteria:
            """Gets all households from candidate list which 
            don't meet final_list_targeting_criteria and set them (HouseholdSelection m2m model)
             final=False (final list is candidate list filtred by final=True"""
            households_ids_queryset = target_population.households.filter(
                ~Q(target_population.final_list_targeting_criteria.get_query())
            ).values_list("id")
            HouseholdSelection.objects.filter(
                household__id__in=households_ids_queryset,
                target_population=target_population,
            ).update(final=False)
        target_population.save()
        return cls(target_population=target_population)


class CopyTargetPopulationMutation(
    graphene.relay.ClientIDMutation, TargetValidator
):
    target_population = graphene.Field(TargetPopulationNode)

    class Input:
        target_population_data = CopyTargetPopulationInput()

    @classmethod
    @is_authenticated
    @transaction.atomic
    def mutate_and_get_payload(cls, _root, info, **kwargs):
        user = info.context.user
        target_population_data = kwargs["target_population_data"]
        name = target_population_data.pop("name")
        target_id = utils.decode_id_string(target_population_data.pop("id"))
        target_population = TargetPopulation.objects.get(id=target_id)
        target_population_copy = TargetPopulation(
            name=name,
            created_by=user,
            status="DRAFT",
            candidate_list_total_households=target_population.candidate_list_total_households,
            candidate_list_total_individuals=target_population.candidate_list_total_individuals,
        )
        target_population_copy.save()
        if target_population.candidate_list_targeting_criteria:
            target_population_copy.candidate_list_targeting_criteria = cls.copy_target_criteria(
                target_population.candidate_list_targeting_criteria
            )
        target_population_copy.save()
        target_population_copy.refresh_from_db()
        return CopyTargetPopulationMutation(target_population_copy)

    @classmethod
    def copy_target_criteria(cls, targeting_criteria):
        targeting_criteria_copy = TargetingCriteria()
        targeting_criteria_copy.save()
        for rule in targeting_criteria.rules.all():
            rule_copy = TargetingCriteriaRule(
                targeting_criteria=targeting_criteria_copy
            )
            rule_copy.save()
            for filter in rule.filters.all():
                filter.pk = None
                filter.targeting_criteria_rule = rule_copy
                filter.save()
        return targeting_criteria_copy


class DeleteTargetPopulationMutation(
    graphene.relay.ClientIDMutation, TargetValidator
):
    ok = graphene.Boolean()

    class Input:
        target_id = graphene.ID(required=True)

    @classmethod
    @is_authenticated
    def mutate_and_get_payload(cls, _root, _info, **kwargs):
        target_id = utils.decode_id_string(kwargs["target_id"])
        target_population = TargetPopulation.objects.get(id=target_id)
        cls.validate_is_finalized(target_population.status)
        target_population.delete()
        return DeleteTargetPopulationMutation(ok=True)


class Mutations(graphene.ObjectType):
    create_target_population = CreateTargetPopulationMutation.Field()
    update_target_population = UpdateTargetPopulationMutation.Field()
    copy_target_population = CopyTargetPopulationMutation.Field()
    delete_target_population = DeleteTargetPopulationMutation.Field()
    approve_target_population = ApproveTargetPopulationMutation.Field()
    unapprove_target_population = UnapproveTargetPopulationMutation.Field()
    finalize_target_population = FinalizeTargetPopulationMutation.Field()
