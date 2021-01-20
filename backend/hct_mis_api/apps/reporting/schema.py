import graphene
from graphene import relay
from graphene_django import DjangoObjectType

from django_filters import CharFilter, DateFilter, FilterSet, MultipleChoiceFilter, OrderingFilter

from hct_mis_api.apps.account.permissions import (
    BaseNodePermissionMixin,
    hopePermissionClass,
    Permissions,
    DjangoPermissionFilterConnectionField,
)
from hct_mis_api.apps.core.extended_connection import ExtendedConnection
from hct_mis_api.apps.core.schema import ChoiceObject
from hct_mis_api.apps.core.utils import to_choice_object
from hct_mis_api.apps.reporting.models import Report


class ReportFilter(FilterSet):
    business_area = CharFilter(field_name="business_area__slug", required=True)
    created_from = DateFilter(field_name="created_at", lookup_expr="gte")
    created_to = DateFilter(field_name="created_at", lookup_expr="lte")
    status = MultipleChoiceFilter(field_name="status", choices=Report.STATUSES)
    report_type = MultipleChoiceFilter(field_name="report_type", choices=Report.REPORT_TYPES)

    class Meta:
        fields = ("created_by", "report_type", "status", "business_area")
        model = Report

    order_by = OrderingFilter(fields=("report_type", "status", "created_at", "created_by__first_name", "date_from"))


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

    def resolve_report_types_choices(self, info, **kwargs):
        return to_choice_object(Report.REPORT_TYPES)

    def resolve_report_status_choices(self, info, **kwargs):
        return to_choice_object(Report.STATUSES)
