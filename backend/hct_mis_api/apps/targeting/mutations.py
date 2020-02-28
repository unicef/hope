import graphene
import targeting.models as target_models
from core.permissions import is_authenticated
from targeting.models import TargetPopulation
from targeting.schema import TargetPopulationNode


class TargetFilterInput(graphene.InputObjectType):
    """Defines filtering attributes."""
    intake_group = graphene.String()
    sex = graphene.String()
    age = graphene.Int()
    school_distance_min = graphene.Int()
    school_distance_max = graphene.Int()
    num_individuals_household_min = graphene.Int()
    num_individuals_household_max = graphene.Int()


class TargetFilterListInput(graphene.InputObjectType):
    """Defines List of rules as string."""
    target_filters = graphene.List(TargetFilterInput, required=True)


class TargetHouseHoldInput(graphene.InputObjectType):
    """Target Household Entries attributes."""
    household_ca_id = graphene.String()


class CreateTargetPopulationInput(graphene.InputObjectType):
    """All attribute inputs to create a new entry."""
    target_population_name = graphene.String()
    target_filter_rules = graphene.InputField(TargetFilterListInput,
                                              required=True)
    target_household = graphene.InputField(TargetHouseHoldInput, required=True)


class CreateTarget(graphene.relay.ClientIDMutation):
    target_population = graphene.Field(TargetPopulationNode)

    class Input:
        target_population_data = CreateTargetPopulationInput()

    @staticmethod
    @is_authenticated
    def mutate_and_get_payload(self, root, info, **target_population_data):
        num_individuals_household_min = float('inf')
        num_individuals_household_max = float('-inf')

        households = TargetPopulation.bulk_add_households(
            target_population_data["target_household"])
        target = TargetPopulation.objects.create(
            name=target_population_data["target_population_name"],
            created_by=info.context.user)
        target.households.add(*households)

        for target_filer in (target_population_data["target_filter_rules"]
                             ["target_filters"]):
            # add TargetFilter models to a target.
            target_filter_model = target_models.TargetFilter.objects.create(
                **target_filer)
            target_filter_model.target_population = target
            target_filter_model.save()

            # get min and max family size from all households.
            num_individuals_household_min = min(
                num_individuals_household_min,
                target_filer['num_individuals_household_min'])
            num_individuals_household_max = max(
                num_individuals_household_max,
                target_filer['num_individuals_household_max'])

        num_individuals_household = target_models.get_serialized_range(
            min_range=num_individuals_household_min,
            max_range=num_individuals_household_max)
        target.num_individuals_household = num_individuals_household
        target.save()

        return CreateTarget(target)


class UpdateTargetPopulation():
    # TODO(codecakes): implement
    pass


class DeleteTargetPopulation():
    # TODO(codecakes): implement
    pass


class Mutations(graphene.ObjectType):
    create_target = CreateTarget.Field()
    # TODO(codecakes): implement update/delete
