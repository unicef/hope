from datetime import datetime

import graphene
from django.db.models.functions import ExtractYear
from django_filters import CharFilter, FilterSet, MultipleChoiceFilter, OrderingFilter, DateTimeFilter
from graphene import relay
from graphene_django import DjangoObjectType

from hct_mis_api.apps.account.permissions import (
    BaseNodePermissionMixin,
    hopePermissionClass,
    Permissions,
    DjangoPermissionFilterConnectionField,
)
from hct_mis_api.apps.core.extended_connection import ExtendedConnection
from hct_mis_api.apps.core.schema import ChoiceObject
from hct_mis_api.apps.core.utils import to_choice_object
from hct_mis_api.apps.grievance.models import GrievanceTicket
from hct_mis_api.apps.payment.models import PaymentRecord
from hct_mis_api.apps.reporting.models import Report, DashboardReport


class ReportFilter(FilterSet):
    business_area = CharFilter(field_name="business_area__slug", required=True)
    created_from = DateTimeFilter(field_name="created_at", lookup_expr="gte")
    created_to = DateTimeFilter(field_name="created_at", lookup_expr="lte")
    status = MultipleChoiceFilter(field_name="status", choices=Report.STATUSES)
    report_type = MultipleChoiceFilter(field_name="report_type", choices=Report.REPORT_TYPES)

    class Meta:
        fields = ("created_by",)
        model = Report

    order_by = OrderingFilter(
        fields=("report_type", "status", "created_at", "created_by__first_name", "date_from", "number_of_records")
    )


class ReportNode(BaseNodePermissionMixin, DjangoObjectType):
    permission_classes = (
        hopePermissionClass(
            Permissions.REPORTING_EXPORT,
        ),
    )

    class Meta:
        model = Report
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection
        convert_choices_to_enum = False

    file_url = graphene.String()

    def resolve_file_url(self, info, **kwargs):
        return self.file.url if self.file else ""


class Query(graphene.ObjectType):
    report = relay.Node.Field(ReportNode)
    all_reports = DjangoPermissionFilterConnectionField(
        ReportNode,
        filterset_class=ReportFilter,
        permission_classes=(
            hopePermissionClass(
                Permissions.REPORTING_EXPORT,
            ),
        ),
    )

    report_types_choices = graphene.List(ChoiceObject)
    report_status_choices = graphene.List(ChoiceObject)
    dashboard_report_types_choices = graphene.List(ChoiceObject, business_area_slug=graphene.String(required=True))
    dashboard_years_choices = graphene.List(graphene.String, business_area_slug=graphene.String(required=True))

    def resolve_report_types_choices(self, info, **kwargs):
        return to_choice_object(Report.REPORT_TYPES)

    def resolve_report_status_choices(self, info, **kwargs):
        return to_choice_object(Report.STATUSES)

    def resolve_dashboard_report_types_choices(self, info, business_area_slug, **kwargs):
        if business_area_slug == "global":
            return to_choice_object(
                [
                    report_type
                    for report_type in DashboardReport.REPORT_TYPES
                    if report_type[0] != DashboardReport.TOTAL_TRANSFERRED_BY_ADMIN_AREA
                ]
            )
        else:
            return to_choice_object(
                [
                    report_type
                    for report_type in DashboardReport.REPORT_TYPES
                    if report_type[0] != DashboardReport.TOTAL_TRANSFERRED_BY_COUNTRY
                ]
            )

    def resolve_dashboard_years_choices(self, info, business_area_slug, **kwargs):
        current_year = datetime.today().year
        years_list = [*range(current_year, current_year - 5, -1)]
        models = [
            (PaymentRecord, "delivery_date"),
            (GrievanceTicket, "created_at"),
        ]
        years_list_from_db = []
        for (model_name, field_name) in models:
            if business_area_slug == "global":
                years_list_from_db.extend(
                    list(
                        model_name.objects.annotate(year_value=ExtractYear(field_name)).values_list(
                            "year_value", flat=True
                        )
                    )
                )
            else:
                years_list_from_db.extend(
                    list(
                        model_name.objects.filter(business_area__slug=business_area_slug)
                        .annotate(year_value=ExtractYear(field_name))
                        .values_list("year_value", flat=True)
                    )
                )
        years_list_choices = [year for year in years_list if year in years_list_from_db]
        years_list_choices = list(set(years_list_choices))
        years_list_choices.sort(reverse=True)
        if not years_list_choices:
            # if no records in db, simply returning current year
            return [current_year]
        return years_list_choices
