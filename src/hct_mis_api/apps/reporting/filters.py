from django_filters import (
    CharFilter,
    DateTimeFilter,
    FilterSet,
    MultipleChoiceFilter,
    OrderingFilter,
)

from hct_mis_api.apps.reporting.models import Report


class ReportFilter(FilterSet):
    business_area = CharFilter(field_name="business_area__slug", required=True)
    created_from = DateTimeFilter(field_name="created_at", lookup_expr="gte")
    created_to = DateTimeFilter(field_name="created_at", lookup_expr="lte")
    status = MultipleChoiceFilter(field_name="status", choices=Report.STATUSES)
    report_type = MultipleChoiceFilter(field_name="report_type", choices=Report.REPORT_TYPES)

    class Meta:
        fields = ("created_by", "report_type", "status", "business_area")
        model = Report

    order_by = OrderingFilter(
        fields=("report_type", "status", "created_at", "created_by__first_name", "date_from", "number_of_records")
    )
