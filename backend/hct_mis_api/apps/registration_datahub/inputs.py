import graphene


class RegistrationXlsxImportMutationInput(graphene.InputObjectType):
    import_data_id = graphene.ID()
    name = graphene.String()
    business_area_slug = graphene.String()
    screen_beneficiary = graphene.Boolean()
    programId = graphene.String()


class RegistrationKoboImportMutationInput(graphene.InputObjectType):
    import_data_id = graphene.String()
    name = graphene.String()
    pull_pictures = graphene.Boolean()
    business_area_slug = graphene.String()
    screen_beneficiary = graphene.Boolean()
