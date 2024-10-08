import graphene


class CreateReportInput(graphene.InputObjectType):
    report_type = graphene.Int(required=True)
    business_area_slug = graphene.String(required=True)
    date_from = graphene.Date(required=True)
    date_to = graphene.Date(required=True)
    program = graphene.ID()
    admin_area_1 = graphene.ID()
    admin_area_2 = graphene.List(graphene.ID)


class RestartCreateReportInput(graphene.InputObjectType):
    report_id = graphene.ID(required=True)
    business_area_slug = graphene.String(required=True)


class CreateDashboardReportInput(graphene.InputObjectType):
    report_types = graphene.List(graphene.String, required=True)
    business_area_slug = graphene.String(required=True)
    year = graphene.Int(required=True)
    admin_area = graphene.ID()
    program = graphene.ID()
