import graphene
from django.db import transaction

from account.models import User
from core import utils
from core.permissions import is_authenticated
from django.forms.models import model_to_dict
from targeting.models import (
    TargetPopulation,
    HouseholdSelection,
    TargetingCriteria,
    TargetingCriteriaRule,
)
from targeting.schema import TargetPopulationNode
from targeting.validators import TargetValidator


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


class CopyTarget(graphene.relay.ClientIDMutation, TargetValidator):
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
        target_population_copy.candidate_list_targeting_criteria = cls.copy_target_criteria(
            target_population.candidate_list_targeting_criteria
        )
        target_population_copy.final_list_targeting_criteria = cls.copy_target_criteria(
            target_population.final_list_targeting_criteria
        )
        target_population_copy.save()
        target_population_copy.refresh_from_db()
        return CopyTarget(target_population_copy)

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


class UpdateTarget(graphene.relay.ClientIDMutation, TargetValidator):
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
        return UpdateTarget(target_population=target_population)


class DeleteTarget(graphene.relay.ClientIDMutation, TargetValidator):
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
        return DeleteTarget(ok=True)


class Mutations(graphene.ObjectType):
    update_target_population = UpdateTarget.Field()
    copy_target_population = CopyTarget.Field()
    delete_target_population = DeleteTarget.Field()
    # TODO(codecakes): implement others
