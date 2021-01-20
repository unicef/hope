import graphene
from django.shortcuts import get_object_or_404

from hct_mis_api.apps.core.models import BusinessArea, AdminArea
from hct_mis_api.apps.core.permissions import is_authenticated
from hct_mis_api.apps.core.utils import decode_id_string
from hct_mis_api.apps.core.airflow_api import AirflowApi

from hct_mis_api.apps.account.permissions import Permissions, PermissionMutation
from hct_mis_api.apps.reporting.schema import ReportNode
from hct_mis_api.apps.reporting.models import Report
from hct_mis_api.apps.reporting.validators import ReportValidator
from hct_mis_api.apps.program.models import Program


class CreateReportInput(graphene.InputObjectType):
    report_type = graphene.Int(required=True)
    business_area_slug = graphene.String(required=True)
    date_from = graphene.Date(required=True)
    date_to = graphene.Date(required=True)
    admin_area = graphene.List(graphene.ID)
    program = graphene.ID()


class CreateReport(ReportValidator, PermissionMutation):
    report = graphene.Field(ReportNode)

    class Arguments:
        report_data = CreateReportInput(required=True)

    @classmethod
    @is_authenticated
    def mutate(cls, root, info, report_data):
        business_area = BusinessArea.objects.get(slug=report_data.pop("business_area_slug"))
        cls.has_permission(info, Permissions.REPORTING_EXPORT, business_area)

        cls.validate(
            start_date=report_data.get("date_from"), end_date=report_data.get("date_to"), report_data=report_data
        )

        report_vars = {
            "business_area": business_area,
            "created_by": info.context.user,
            "status": Report.IN_PROGRESS,
            "report_type": report_data["report_type"],
            "date_from": report_data["date_from"],
            "date_to": report_data["date_to"],
        }
        admin_areas = None

        program_id = report_data.pop("program", None)
        admin_area_ids = report_data.pop("admin_area", None)
        if program_id:
            program = get_object_or_404(Program, id=decode_id_string(program_id), business_area=business_area)
            report_vars["program"] = program

        if admin_area_ids:
            admin_areas = [
                get_object_or_404(
                    AdminArea, id=decode_id_string(admin_area_id), admin_area_type__business_area=business_area
                )
                for admin_area_id in admin_area_ids
            ]

        report = Report.objects.create(**report_vars)
        if admin_areas:
            report.admin_area.set(admin_areas)

        AirflowApi.start_dag(
            dag_id="ReportExport",
            context={"report_id": str(report.id)},
        )

        return CreateReport(report)


class Mutations(graphene.ObjectType):
    create_report = CreateReport.Field()
