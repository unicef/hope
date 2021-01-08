import graphene
from graphene import relay
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from django_filters import CharFilter, DateFilter, FilterSet, MultipleChoiceFilter, OrderingFilter

from core.extended_connection import ExtendedConnection
from core.schema import ChoiceObject
from core.utils import to_choice_object
from reporting.models import Report


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


class ReportNode(DjangoObjectType):
    class Meta:
        model = Report
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection


class Query(graphene.ObjectType):
    report = relay.Node.Field(ReportNode)
    all_reports = DjangoFilterConnectionField(ReportNode, filterset_class=ReportFilter)

    report_types_choices = graphene.List(ChoiceObject)
    report_status_choices = graphene.List(ChoiceObject)

    def resolve_report_types_choices(self, info, **kwargs):
        return to_choice_object(Report.REPORT_TYPES)

    def resolve_report_status_choices(self, info, **kwargs):
        return to_choice_object(Report.STATUSES)
