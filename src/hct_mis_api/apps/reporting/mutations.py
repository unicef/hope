import datetime
import logging
from typing import Any

from django.http import Http404
from django.shortcuts import get_object_or_404
from django.utils import timezone

import graphene
from graphql import GraphQLError

from hct_mis_api.apps.account.permissions import PermissionMutation, Permissions
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.core.permissions import is_authenticated
from hct_mis_api.apps.core.utils import decode_id_string
from hct_mis_api.apps.core.validators import CommonValidator
from hct_mis_api.apps.geo.models import Area
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.reporting.celery_tasks import report_export_task
from hct_mis_api.apps.reporting.inputs import (
    CreateReportInput,
    RestartCreateReportInput,
)
from hct_mis_api.apps.reporting.models import Report
from hct_mis_api.apps.reporting.schema import ReportNode
from hct_mis_api.apps.reporting.validators import ReportValidator

logger = logging.getLogger(__name__)


class CreateReport(ReportValidator, CommonValidator, PermissionMutation):
    report = graphene.Field(ReportNode)

    class Arguments:
        report_data = CreateReportInput(required=True)

    @classmethod
    @is_authenticated
    def mutate(cls, root: Any, info: Any, report_data: dict) -> "CreateReport":
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
        admin_area_ids = None
        program_id = report_data.pop("program", None)
        admin_area_1_id = report_data.pop("admin_area_1", None)
        admin_area_2_ids = report_data.pop("admin_area_2", None)
        if program_id:
            program = get_object_or_404(Program, id=decode_id_string(program_id), business_area=business_area)
            report_vars["program"] = program

        if admin_area_1_id and not admin_area_2_ids:
            parent = get_object_or_404(
                Area, id=decode_id_string(admin_area_1_id), area_type__country__name=business_area.name
            )
            admin_area_ids = Area.objects.filter(parent=parent).values_list("id", flat=True)
        if admin_area_2_ids:
            # remove duplications
            admin_area_2_ids = list(set(admin_area_2_ids))
            admin_area_ids = [decode_id_string(admin_area_id) for admin_area_id in admin_area_2_ids]

        if admin_area_ids:
            admin_areas = Area.objects.filter(id__in=admin_area_ids, area_type__country__name=business_area.name)
            if len(admin_area_ids) != len(admin_areas):
                raise Http404("No Area matches the given query.")

        report = Report.objects.create(**report_vars)
        if admin_areas:
            report.admin_area.set(admin_areas)

        report_export_task.delay(report_id=str(report.id))

        return CreateReport(report)


class RestartCreateReport(PermissionMutation):
    report = graphene.Field(ReportNode)

    class Arguments:
        report_data = RestartCreateReportInput(required=True)

    @classmethod
    @is_authenticated
    def mutate(cls, root: Any, info: Any, report_data: dict) -> "RestartCreateReport":
        business_area = BusinessArea.objects.get(slug=report_data.get("business_area_slug"))
        cls.has_permission(info, Permissions.REPORTING_EXPORT, business_area)
        report = get_object_or_404(Report, id=decode_id_string(report_data.get("report_id")))

        delta30 = timezone.now() - datetime.timedelta(minutes=30)
        if report.status is not Report.IN_PROGRESS and report.updated_at > delta30:
            msg = "Impossible restart now. Status must be 'Processing' and more than 30 mins after last running."
            logger.error(msg)
            raise GraphQLError(msg)
        report_export_task.delay(report_id=str(report.id))
        report.refresh_from_db()
        return RestartCreateReport(report)


class Mutations(graphene.ObjectType):
    create_report = CreateReport.Field()
    restart_create_report = RestartCreateReport.Field()
