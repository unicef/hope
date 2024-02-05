import graphene


class PartnerProgramInput(graphene.InputObjectType):
    id = graphene.String(required=True, description="Partner ID")
    area_access = graphene.String(description="'ADMIN_AREA' or 'BUSINESS_AREA'")
    admin_areas = graphene.List(graphene.String)


class CreateProgramInput(graphene.InputObjectType):
    name = graphene.String()
    start_date = graphene.Date()
    end_date = graphene.Date()
    description = graphene.String()
    budget = graphene.Decimal()
    frequency_of_payments = graphene.String()
    sector = graphene.String()
    cash_plus = graphene.Boolean()
    population_goal = graphene.Int()
    administrative_areas_of_implementation = graphene.String()
    business_area_slug = graphene.String()
    individual_data_needed = graphene.Boolean()
    data_collecting_type_code = graphene.String()
    partners = graphene.List(PartnerProgramInput)
    programme_code = graphene.String()


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
    cash_plus = graphene.Boolean()
    population_goal = graphene.Int()
    administrative_areas_of_implementation = graphene.String()
    individual_data_needed = graphene.Boolean()
    data_collecting_type_code = graphene.String()
    partners = graphene.List(PartnerProgramInput)
    programme_code = graphene.String()


class CopyProgramInput(graphene.InputObjectType):
    id = graphene.String(required=True)
    name = graphene.String()
    start_date = graphene.Date()
    end_date = graphene.Date()
    description = graphene.String()
    budget = graphene.Decimal()
    frequency_of_payments = graphene.String()
    sector = graphene.String()
    cash_plus = graphene.Boolean()
    population_goal = graphene.Int()
    administrative_areas_of_implementation = graphene.String()
    business_area_slug = graphene.String()
    individual_data_needed = graphene.Boolean()
    data_collecting_type_code = graphene.String()
    partners = graphene.List(PartnerProgramInput)
    programme_code = graphene.String()
