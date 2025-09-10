from typing import Any

from django.db.models import Q, QuerySet
import django_filters
from django_filters import FilterSet

from hope.apps.payment.models import (
    DeliveryMechanism,
    PaymentPlan,
    PaymentVerificationSummary,
)


class PaymentPlanFilter(FilterSet):
    search = django_filters.CharFilter(method="search_filter")
    status = django_filters.ChoiceFilter(
        choices=PaymentPlan.Status.choices,
    )
    program = django_filters.CharFilter(method="filter_by_program", help_text="Filter by program slug")
    program_cycle = django_filters.CharFilter(method="filter_by_program_cycle")
    name = django_filters.CharFilter(field_name="name", lookup_expr="startswith")
    fsp = django_filters.CharFilter(field_name="financial_service_provider__name")
    delivery_mechanism = django_filters.ModelMultipleChoiceFilter(
        field_name="delivery_mechanism__code",
        queryset=DeliveryMechanism.objects.all(),
        to_field_name="code",
    )
    payment_verification_summary_status = django_filters.MultipleChoiceFilter(
        field_name="payment_verification_summary__status",
        choices=PaymentVerificationSummary.STATUS_CHOICES,
    )
    program_cycle_start_date = django_filters.DateFilter(field_name="program_cycle__start_date", lookup_expr="gte")
    program_cycle_end_date = django_filters.DateFilter(field_name="program_cycle__end_date", lookup_expr="lte")
    total_entitled_quantity_usd_from = django_filters.NumberFilter(
        field_name="total_entitled_quantity_usd", lookup_expr="gte"
    )
    total_entitled_quantity_usd_to = django_filters.NumberFilter(
        field_name="total_entitled_quantity_usd", lookup_expr="lte"
    )
    start_date = django_filters.DateFilter(field_name="dispersion_start_date", lookup_expr="gte")
    end_date = django_filters.DateFilter(field_name="dispersion_end_date", lookup_expr="lte")

    class Meta:
        model = PaymentPlan
        fields = {
            "total_entitled_quantity": ["gte", "lte"],
            "is_follow_up": ["exact"],
            "updated_at": ["gte", "lte"],
        }

    def filter_by_program(self, qs: QuerySet, name: str, value: str) -> QuerySet:
        return qs.filter(program_cycle__program__slug=value)

    def filter_by_program_cycle(self, qs: QuerySet, name: str, value: str) -> QuerySet:
        return qs.filter(program_cycle_id=value)

    def search_filter(self, qs: QuerySet, name: str, value: str) -> "QuerySet[PaymentPlan]":
        return qs.filter(Q(id__icontains=value) | Q(unicef_id__icontains=value) | Q(name__istartswith=value))


class TargetPopulationFilter(PaymentPlanFilter):
    status = django_filters.ChoiceFilter(
        method="filter_by_status",
        choices=PaymentPlan.Status.choices + [("ASSIGNED", "Assigned")],
    )

    class Meta:
        model = PaymentPlan
        fields = {
            "created_at": ["gte", "lte"],
            "total_households_count": ["gte", "lte"],
            "total_individuals_count": ["gte", "lte"],
            "updated_at": ["gte", "lte"],
        }

    @staticmethod
    def filter_by_status(queryset: "QuerySet", model_field: str, value: Any) -> "QuerySet":
        # assigned TP statuses
        is_assigned = [
            PaymentPlan.Status.PREPARING.value,
            PaymentPlan.Status.OPEN.value,
            PaymentPlan.Status.LOCKED.value,
            PaymentPlan.Status.LOCKED_FSP.value,
            PaymentPlan.Status.IN_APPROVAL.value,
            PaymentPlan.Status.IN_AUTHORIZATION.value,
            PaymentPlan.Status.IN_REVIEW.value,
            PaymentPlan.Status.ACCEPTED.value,
            PaymentPlan.Status.FINISHED.value,
        ]
        value_list = is_assigned if value == "ASSIGNED" else [value]
        return queryset.filter(status__in=value_list)
