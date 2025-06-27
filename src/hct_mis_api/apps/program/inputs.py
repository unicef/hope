import graphene


class ProgramPartnerThroughInput(graphene.InputObjectType):
    partner = graphene.String()
    areas = graphene.List(graphene.String)
    area_access = graphene.String(description="'ADMIN_AREA' or 'BUSINESS_AREA'")


class PeriodicFieldDataInput(graphene.InputObjectType):
    subtype = graphene.String()
    number_of_rounds = graphene.Int()
    rounds_names = graphene.List(graphene.String)


class PDUFieldInput(graphene.InputObjectType):
    id = graphene.String(required=False)
    label = graphene.String()
    pdu_data = PeriodicFieldDataInput()


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
    data_collecting_type_code = graphene.String()
    beneficiary_group = graphene.String()
    partners = graphene.List(ProgramPartnerThroughInput)
    partner_access = graphene.String()
    programme_code = graphene.String()
    pdu_fields = graphene.List(PDUFieldInput)


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
    data_collecting_type_code = graphene.String()
    beneficiary_group = graphene.String()
    programme_code = graphene.String()
    pdu_fields = graphene.List(PDUFieldInput)


class UpdateProgramPartnersInput(graphene.InputObjectType):
    id = graphene.String(required=True)
    partners = graphene.List(ProgramPartnerThroughInput)
    partner_access = graphene.String()


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
    data_collecting_type_code = graphene.String()
    partners = graphene.List(ProgramPartnerThroughInput)
    partner_access = graphene.String()
    programme_code = graphene.String()
    pdu_fields = graphene.List(PDUFieldInput)
