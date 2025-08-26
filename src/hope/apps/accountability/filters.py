import re

from django.db.models import Q, QuerySet
from django.db.models.functions import Lower
from django_filters import BooleanFilter, CharFilter, ChoiceFilter, FilterSet
from django_filters import rest_framework as filters

from hope.models.survey import Survey
from hope.models.feedback import Feedback
from hope.models.message import Message
from hope.apps.core.utils import CustomOrderingFilter
from hope.models.program import Program


class MessagesFilter(FilterSet):
    program = CharFilter(method="filter_program")
    created_at = filters.DateFromToRangeFilter(field_name="created_at")
    title = CharFilter(field_name="title", lookup_expr="icontains")
    body = CharFilter(field_name="body", lookup_expr="icontains")
    sampling_type = ChoiceFilter(field_name="sampling_type", choices=Message.SamplingChoices.choices)

    def filter_program(self, queryset: QuerySet, name: str, value: str) -> QuerySet[Message]:
        return queryset.filter(payment_plan__program_cycle__program=value)

    class Meta:
        model = Message
        fields = {
            "number_of_recipients": ["exact", "gte", "lte"],
            "payment_plan": ["exact"],
            "created_by": ["exact"],
        }

    order_by = CustomOrderingFilter(
        fields=(
            Lower("title"),
            "number_of_recipients",
            "sampling_type",
            "created_by",
            "id",
            "created_at",
        )
    )


class FeedbackFilter(FilterSet):
    issue_type = ChoiceFilter(field_name="issue_type", choices=Feedback.ISSUE_TYPE_CHOICES)
    created_at = filters.DateFromToRangeFilter(field_name="created_at")
    created_by = CharFilter(method="filter_created_by")
    is_active_program = BooleanFilter(method="filter_is_active_program")

    def filter_created_by(self, queryset: QuerySet, name: str, value: str) -> QuerySet[Feedback]:
        return queryset.filter(created_by__pk=value)

    def filter_is_active_program(self, qs: QuerySet, name: str, value: bool) -> QuerySet:
        filter_q = Q(program__isnull=True)
        if value is True:
            filter_q |= Q(program__status=Program.ACTIVE)
        else:
            filter_q |= Q(program__status=Program.FINISHED)
        return qs.filter(filter_q)

    class Meta:
        model = Feedback
        fields = ()

    order_by = CustomOrderingFilter(
        fields=(
            "unicef_id",
            "issue_type",
            "household_lookup",
            ("created_by__first_name", "created_by"),
            "created_at",
            "linked_grievance",
        )
    )


class SurveyFilter(FilterSet):
    created_at = filters.DateFromToRangeFilter(field_name="created_at")
    search = CharFilter(method="filter_search")
    created_by = CharFilter(method="filter_created_by")

    def filter_search(self, queryset: QuerySet, name: str, value: str) -> QuerySet[Survey]:
        if re.match(r"([\"\']).+\1", value):
            values = [value.replace('"', "").strip()]
        else:
            values = value.split(" ")
        q_obj = Q()
        for unstripped_value in values:
            value = unstripped_value.strip(",")
            inner_query = Q()
            inner_query |= Q(title__icontains=value)
            inner_query |= Q(unicef_id__istartswith=value)
            inner_query |= Q(unicef_id__iendswith=value)

            q_obj &= inner_query
        return queryset.filter(q_obj).distinct()

    def filter_created_by(self, queryset: QuerySet, name: str, value: str) -> QuerySet[Survey]:
        return queryset.filter(created_by__pk=value)

    class Meta:
        model = Survey
        fields = {
            "program": ["exact"],
            "payment_plan": ["exact"],
        }

    order_by = CustomOrderingFilter(
        fields=(
            "unicef_id",
            "title",
            "category",
            "number_of_recipient",
            ("created_by__first_name", "created_by"),
            "created_at",
        )
    )
