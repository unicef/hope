import graphene


class RegistrationXlsxImportMutationInput(graphene.InputObjectType):
    import_data_id = graphene.ID()
    name = graphene.String()
    business_area_slug = graphene.String()
    screen_beneficiary = graphene.Boolean()
    # True - create/merge RDI with delivery mechanism validation errors, create Grievance needs adjudication tickets
    # False - fail RDI create/merge on delivery mechanism validation errors
    allow_delivery_mechanisms_validation_errors = graphene.Boolean()


class RegistrationKoboImportMutationInput(graphene.InputObjectType):
    import_data_id = graphene.String()
    name = graphene.String()
    pull_pictures = graphene.Boolean()
    business_area_slug = graphene.String()
    screen_beneficiary = graphene.Boolean()
    allow_delivery_mechanisms_validation_errors = graphene.Boolean()
