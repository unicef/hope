from pprint import pprint

import graphene
from django.db import transaction
from django.db.models import Q

from account.models import User
from core import utils
from core.permissions import is_authenticated
from django.forms.models import model_to_dict

from core.utils import decode_id_string
from household.models import Household
from targeting.models import (
    TargetPopulation,
    HouseholdSelection,
    TargetingCriteria,
    TargetingCriteriaRule,
)
from targeting.schema import TargetPopulationNode
from targeting.validators import (
    TargetValidator,
    ApproveTargetPopulationValidator,
    FinalizeTargetPopulationValidator,
    UnapproveTargetPopulationValidator,
)


class CreateTargetPopulationInput(graphene.InputObjectType):
    """All attribute inputs to create a new entry."""

    # TODO(codecakes): To Implement.
    pass


class CopyTargetPopulationInput(graphene.InputObjectType):
    """All attribute inputs to create a new entry."""

    id = graphene.ID()
    name = graphene.String()


class UpdateTargetPopulationInput(graphene.InputObjectType):
    """All attribute inputs to update an existing new entry."""

    id = graphene.ID()
    name = graphene.String()
    status = graphene.String()


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
        return cls.validated_mutate(root, info,model_object=model_object, **kwargs)

    @classmethod
    def get_object(cls, root, info, **kwargs):
        id = kwargs.get("id")
        if id is None:
            return None
        object = cls.model_class.objects.get(id=decode_id_string(id))
        for validator in cls.object_validators:
            validator.validate(object)
        return object


class ApproveTargetPopulationMutation(ValidatedMutation):
    target_population = graphene.Field(TargetPopulationNode)
    object_validators = [ApproveTargetPopulationValidator]
    model_class = TargetPopulation

    class Arguments:
        id = graphene.ID(required=True)


    @classmethod
    @transaction.atomic
    def validated_mutate(cls, root, info, **kwargs):
        target_population = kwargs.get("model_object")
        target_population.status = "APPROVED"
        households = Household.objects.filter(
            target_population.candidate_list_targeting_criteria.get_query()
        ).all()
        target_population.households.set(households)
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
                household__id__in=households_ids_queryset, target_population=target_population
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
            status=target_population.status,
            candidate_list_total_households=target_population.candidate_list_total_households,
            candidate_list_total_individuals=target_population.candidate_list_total_individuals,
            final_list_total_households=target_population.final_list_total_households,
            final_list_total_individuals=target_population.final_list_total_individuals,
            selection_computation_metadata=target_population.selection_computation_metadata,
            program=target_population.program,
        )
        target_population_copy.save()
        selections = HouseholdSelection.objects.filter(
            target_population=target_population
        )
        selections_copy = []
        for selection in selections:
            selections_copy.append(
                HouseholdSelection(
                    target_population=target_population_copy,
                    household=selection.household,
                    final=selection.final,
                )
            )
        HouseholdSelection.objects.bulk_create(selections_copy)
        if target_population.candidate_list_targeting_criteria:
            target_population_copy.candidate_list_targeting_criteria = cls.copy_target_criteria(
                target_population.candidate_list_targeting_criteria
            )
        if target_population.final_list_targeting_criteria:
            target_population_copy.final_list_targeting_criteria = cls.copy_target_criteria(
                target_population.final_list_targeting_criteria
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


class UpdateTargetPopulationMutation(
    graphene.relay.ClientIDMutation, TargetValidator
):
    target_population = graphene.Field(TargetPopulationNode)

    class Input:
        target_population_data = UpdateTargetPopulationInput()

    @classmethod
    @is_authenticated
    def mutate_and_get_payload(cls, _root, _info, **kwargs):
        target_population_data = kwargs["target_population_data"]
        target_id = utils.decode_id_string(target_population_data.pop("id"))
        target_population = TargetPopulation.objects.get(id=target_id)
        cls.validate_is_finalized(target_population.status)
        utils.update_model(target_population, target_population_data)
        return UpdateTargetPopulationMutation(
            target_population=target_population
        )


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
    update_target_population = UpdateTargetPopulationMutation.Field()
    copy_target_population = CopyTargetPopulationMutation.Field()
    delete_target_population = DeleteTargetPopulationMutation.Field()
    approve_target_population = ApproveTargetPopulationMutation.Field()
    unapprove_target_population = UnapproveTargetPopulationMutation.Field()
    finalize_target_population = FinalizeTargetPopulationMutation.Field()
    # TODO(codecakes): implement others
