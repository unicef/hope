import graphene
from django.shortcuts import get_object_or_404

from core.models import BusinessArea, AdminArea
from core.permissions import is_authenticated
from core.utils import decode_id_string

from account.permissions import Permissions, PermissionMutation
from reporting.schema import ReportNode
from reporting.models import Report
from program.models import Program


class CreateReportMutationInput(graphene.InputObjectType):
    report_type = graphene.Int(required=True)
    business_area_slug = graphene.String(required=True)
    date_from = graphene.Date(required=True)
    date_to = graphene.Date(required=True)
    admin_area = graphene.ID()
    program = graphene.ID()
    country = graphene.String()


class CreateReportMutation(PermissionMutation):
    new_report = graphene.Field(ReportNode)

    class Arguments:
        create_report_data = CreateReportMutationInput(required=True)

    @classmethod
    @is_authenticated
    def mutate(cls, root, info, create_report_data):
        # do some basic validation for timeframe and report_type matching filter args
        business_area = BusinessArea.objects.get(slug=create_report_data.pop("business_area_slug"))

        cls.has_permission(info, Permissions.REPORTING_EXPORT, business_area)

        report_vars = {
            "business_area": business_area,
            "created_by": info.context.user,
            "status": Report.IN_PROGRESS,
            "report_type": create_report_data["report_type"],
            "date_from": create_report_data["date_from"],
            "date_to": create_report_data["date_to"],
        }
        if create_report_data.get("admin_area"):
            admin_area_id = decode_id_string(create_report_data["admin_area"])
            admin_area = get_object_or_404(AdminArea, id=admin_area_id)
            report_vars["admin_area"] = admin_area
        if create_report_data.get("program"):
            program_id = decode_id_string(create_report_data["program"])
            program = get_object_or_404(Program, id=program_id)
            report_vars["program"] = program
        if create_report_data.get("country"):
            report_vars["country"] = create_report_data["country"]

        report = Report.objects.create(**report_vars)

        # AirflowApi.start_dag(
        #     dag_id="RegistrationDataImportDeduplication",
        #     context={"registration_data_import_id": str(registration_data_import_datahub_id)},
        # )

        return cls(report=report)


class Mutations(graphene.ObjectType):
    create_report = CreateReportMutation.Field()
