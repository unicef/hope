import graphene
from core import utils
from targeting.models import TargetPopulation
from targeting.schema import TargetPopulationNode
from targeting.validators import TargetValidator


class CreateTargetPopulationInput(graphene.InputObjectType):
    """All attribute inputs to create a new entry."""

    # TODO(codecakes): To Implement.
    pass


class UpdateTargetPopulationInput(graphene.InputObjectType):
    """All attribute inputs to update an existing new entry."""

    id = graphene.ID()
    name = graphene.String()
    last_edited_at = graphene.DateTime()
    status = graphene.String()


class CreateTarget:
    # TODO(codecakes): Implement
    pass


class UpdateTarget(graphene.relay.ClientIDMutation, TargetValidator):
    target_population = graphene.Field(TargetPopulationNode)

    class Input:
        target_population_data = UpdateTargetPopulationInput()

    @classmethod
    # @is_authenticated
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
    # TODO(codecakes): implement others
