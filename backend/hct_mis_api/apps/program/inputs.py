import graphene


class CreateProgramInput(graphene.InputObjectType):
    name = graphene.String()
    start_date = graphene.Date()
    end_date = graphene.Date()
    description = graphene.String()
    budget = graphene.Decimal()
    frequency_of_payments = graphene.String()
    sector = graphene.String()
    scope = graphene.String()
    cash_plus = graphene.Boolean()
    population_goal = graphene.Int()
    administrative_areas_of_implementation = graphene.String()
    business_area_slug = graphene.String()
    individual_data_needed = graphene.Boolean()


class UpdateProgramInput(graphene.InputObjectType):
    id = graphene.String(required=True)
    name = graphene.String()
    status = graphene.String()
    start_date = graphene.Date()
    end_date = graphene.Date()
    description = graphene.String()
    budget = graphene.Decimal()
    frequency_of_payments = graphene.String()
    sector = graphene.String()
    scope = graphene.String()
    cash_plus = graphene.Boolean()
    population_goal = graphene.Int()
    administrative_areas_of_implementation = graphene.String()
    individual_data_needed = graphene.Boolean()
