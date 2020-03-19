import graphene
from account.models import User
from core import utils
from core.permissions import is_authenticated
from django.db import transaction
from django.forms.models import model_to_dict
from targeting.models import TargetPopulation
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
    last_edited_at = graphene.DateTime()
    status = graphene.String()


class CreateTarget:
    # TODO(codecakes): Implement
    pass


class CopyTarget(graphene.relay.ClientIDMutation, TargetValidator):
    target_population = graphene.Field(TargetPopulationNode)

    class Input:
        target_population_data = CopyTargetPopulationInput()

    @classmethod
    @transaction.atomic
    @is_authenticated
    def mutate_and_get_payload(cls, _root, info, **kwargs):
        user = info.context.user
        target_population_data = kwargs["target_population_data"]
        target_id = utils.decode_id_string(target_population_data.pop("id"))
        target_population = TargetPopulation.objects.get(id=target_id)
        # Get relational fields
        exclude_foreign_fields = utils.filter_relational_fields(
            target_population
        )
        target_population_dict = model_to_dict(
            target_population,
            exclude=["id", "pk", "name"]
            + [field.name for field in exclude_foreign_fields],
        )
        # Update relevant details.
        target_population_dict["name"] = target_population_data["name"]
        target_population_dict["created_by"] = (
            user if isinstance(user, User) else target_population.created_by
        )
        # Create new record.
        new_target_population = TargetPopulation.objects.create(
            **target_population_dict
        )
        # Copy associations.
        new_target_population = utils.copy_associations(
            target_population, new_target_population, exclude_foreign_fields
        )
        return CopyTarget(new_target_population)


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


class DeleteTarget:
    # TODO(codecakes): implement
    pass


class Mutations(graphene.ObjectType):
    update_target = UpdateTarget.Field()
    copy_target = CopyTarget.Field()
    # TODO(codecakes): implement others
