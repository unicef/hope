import graphene
from django.shortcuts import get_object_or_404

from core.models import BusinessArea, AdminArea
from core.permissions import is_authenticated
from core.utils import decode_id_string
from core.airflow_api import AirflowApi

from account.permissions import Permissions, PermissionMutation
from reporting.schema import ReportNode
from reporting.models import Report
from program.models import Program


class CreateReportInput(graphene.InputObjectType):
    report_type = graphene.Int(required=True)
    business_area_slug = graphene.String(required=True)
    date_from = graphene.Date(required=True)
    date_to = graphene.Date(required=True)
    admin_area = graphene.List(graphene.ID)
    program = graphene.ID()
    country = graphene.String()


class CreateReport(PermissionMutation):
    report = graphene.Field(ReportNode)

    class Arguments:
        report_data = CreateReportInput(required=True)

    @classmethod
    @is_authenticated
    def mutate(cls, root, info, report_data):
        # do some basic validation for timeframe and report_type matching filter args
        business_area = BusinessArea.objects.get(slug=report_data.pop("business_area_slug"))
        cls.has_permission(info, Permissions.REPORTING_EXPORT, business_area)

        report_vars = {
            "business_area": business_area,
            "created_by": info.context.user,
            "status": Report.IN_PROGRESS,
            "report_type": report_data["report_type"],
            "date_from": report_data["date_from"],
            "date_to": report_data["date_to"],
        }
        admin_areas = None

        if report_data.get("program"):
            program_id = decode_id_string(report_data["program"])
            program = get_object_or_404(Program, id=program_id)
            report_vars["program"] = program
        if report_data.get("country"):
            report_vars["country"] = report_data["country"]
        if report_data.get("admin_area"):
            admin_areas = [
                get_object_or_404(AdminArea, id=decode_id_string(admin_area_id))
                for admin_area_id in report_data["admin_area"]
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
