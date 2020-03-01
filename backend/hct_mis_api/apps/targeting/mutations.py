import graphene
import targeting.models as target_models
from core.permissions import is_authenticated
from targeting.models import TargetPopulation
from targeting.schema import TargetPopulationNode


class TargetFilterInput(graphene.InputObjectType):
    """Defines filtering attributes."""
    intake_group = graphene.String()
    sex = graphene.String()
    age_min = graphene.Int()
    age_max = graphene.Int()
    school_distance_min = graphene.Int()
    school_distance_max = graphene.Int()
    num_individuals_min = graphene.Int()
    num_individuals_max = graphene.Int()


class TargetFilterListInput(graphene.InputObjectType):
    """Defines List of rules as string."""
    target_filters = graphene.List(TargetFilterInput, required=True)


class TargetHouseholdInput(graphene.InputObjectType):
    """Target Household Entries attributes."""
    household_ca_id = graphene.String()
    # TODO(codecakes): modify based on what admin level is.
    # admin_level = graphene.String()


class TargetHouseHoldList(graphene.InputObjectType):
    """List of TargetHouseholdInput entries."""
    household_list = graphene.List(TargetHouseholdInput, required=True)


class CreateTargetPopulationInput(graphene.InputObjectType):
    """All attribute inputs to create a new entry."""
    target_population_name = graphene.String()
    last_edited_at = graphene.DateTime()
    status = graphene.String()
    target_filter_rules = graphene.InputField(TargetFilterListInput)
    target_households = graphene.InputField(TargetHouseHoldList)


class CreateTarget(graphene.relay.ClientIDMutation):
    target_population = graphene.Field(TargetPopulationNode)

    class Input:
        target_population_data = CreateTargetPopulationInput()

    @staticmethod
    @is_authenticated
    def mutate_and_get_payload(self, root, info, **target_population_data):

        # get all household models by conditional attributes.
        households = TargetPopulation.bulk_get_households(
            target_population_data["target_households"])
        # create a new target population entry.
        target = TargetPopulation.objects.create(
            name=target_population_data["target_population_name"],
            status = target_population_data["status"],
            last_edited_at = target_population_data["last_edited_at"],
            created_by=info.context.user)
        # add associated household results to target entry.
        target.households.add(*households)

        for target_filer_rule in (
                target_population_data["target_filter_rules"]):
            target_filer = target_filer_rule["target_filters"]
            # add TargetFilter models to a target.
            target_filter_model = target_models.TargetFilter.objects.create(
                **target_filer)
            target_filter_model.target_population = target
            target_filter_model.save()

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
