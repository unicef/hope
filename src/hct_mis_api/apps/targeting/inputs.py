import graphene


class CopyTargetPopulationInput(graphene.InputObjectType):
    """All attribute inputs to create a new entry."""
    id = graphene.ID()
    name = graphene.String()
    program_cycle_id = graphene.ID(required=True)
