import graphene


class RegistrationXlsxImportMutationInput(graphene.InputObjectType):
    import_data_id = graphene.ID()
    name = graphene.String()
    business_area_slug = graphene.String()
    screen_beneficiary = graphene.Boolean()


class RegistrationKoboImportMutationInput(graphene.InputObjectType):
    import_data_id = graphene.String()
    name = graphene.String()
    pull_pictures = graphene.Boolean()
    business_area_slug = graphene.String()
    screen_beneficiary = graphene.Boolean()


class RegistrationProgramPopulationImportMutationInput(graphene.InputObjectType):
    import_from_program_id = graphene.String()
    import_from_ids = graphene.String(description="String of Ind or HH ids separated by comma")
    name = graphene.String()
    business_area_slug = graphene.String()
    screen_beneficiary = graphene.Boolean()
