from typing import Any

from django.db.models import Q, QuerySet
import django_filters
from django_filters import FilterSet, OrderingFilter

from hope.apps.core.api.filters import OfficeSearchFilterMixin
from hope.apps.grievance.models import GrievanceTicket
from hope.models import (
    DeliveryMechanism,
    Payment,
    PaymentPlan,
    PaymentVerification,
    PaymentVerificationPlan,
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


class PendingPaymentFilter(FilterSet):
    ordering = OrderingFilter(
        fields=(
            ("household__unicef_id", "household_unicef_id"),
            ("household__size", "household_size"),
            ("household__admin2__name", "household_admin2"),
            ("head_of_household__full_name", "head_of_household"),
            ("vulnerability_score", "vulnerability_score"),
        )
    )

    class Meta:
        model = Payment
        fields = []


class PaymentPlanOfficeSearchFilter(OfficeSearchFilterMixin, PaymentPlanFilter):
    class Meta(PaymentPlanFilter.Meta):
        pass

    def filter_by_payment_plan_for_office_search(self, queryset: QuerySet, unicef_id: str) -> QuerySet:
        return queryset.filter(unicef_id=unicef_id)

    def filter_by_household_for_office_search(self, queryset: QuerySet, value: str) -> QuerySet:
        return queryset.filter(
            Q(payment_items__household__unicef_id=value)
            | Q(payment_items__household__head_of_household__full_name__icontains=value)
            | Q(payment_items__household__head_of_household__given_name__icontains=value)
            | Q(payment_items__household__head_of_household__middle_name__icontains=value)
            | Q(payment_items__household__head_of_household__family_name__icontains=value)
            | Q(payment_items__household__head_of_household__phone_no__icontains=value)
            | Q(payment_items__household__head_of_household__phone_no_alternative__icontains=value)
            | Q(payment_items__household__head_of_household__documents__document_number__icontains=value)
        ).distinct()

    def filter_by_individual_for_office_search(self, queryset: QuerySet, value: str) -> QuerySet:
        return queryset.filter(
            Q(payment_items__head_of_household__unicef_id=value)
            | Q(payment_items__head_of_household__full_name__icontains=value)
            | Q(payment_items__head_of_household__given_name__icontains=value)
            | Q(payment_items__head_of_household__middle_name__icontains=value)
            | Q(payment_items__head_of_household__family_name__icontains=value)
            | Q(payment_items__head_of_household__phone_no__icontains=value)
            | Q(payment_items__head_of_household__phone_no_alternative__icontains=value)
            | Q(payment_items__head_of_household__documents__document_number__icontains=value)
        ).distinct()

    def filter_by_payment_for_office_search(self, queryset: QuerySet, unicef_id: str) -> QuerySet:
        return queryset.filter(payment_items__unicef_id=unicef_id).distinct()


class PaymentOfficeSearchFilter(OfficeSearchFilterMixin, FilterSet):
    class Meta:
        model = Payment
        fields = []

    def filter_by_payment_for_office_search(self, queryset: QuerySet, unicef_id: str) -> QuerySet:
        return queryset.filter(unicef_id=unicef_id)

    def filter_by_household_for_office_search(self, queryset: QuerySet, value: str) -> QuerySet:
        return queryset.filter(
            Q(household__unicef_id=value)
            | Q(household__head_of_household__full_name__icontains=value)
            | Q(household__head_of_household__given_name__icontains=value)
            | Q(household__head_of_household__middle_name__icontains=value)
            | Q(household__head_of_household__family_name__icontains=value)
            | Q(household__head_of_household__phone_no__icontains=value)
            | Q(household__head_of_household__phone_no_alternative__icontains=value)
            | Q(household__head_of_household__documents__document_number__icontains=value)
        ).distinct()

    def filter_by_individual_for_office_search(self, queryset: QuerySet, value: str) -> QuerySet:
        return queryset.filter(
            Q(head_of_household__unicef_id=value)
            | Q(head_of_household__full_name__icontains=value)
            | Q(head_of_household__given_name__icontains=value)
            | Q(head_of_household__middle_name__icontains=value)
            | Q(head_of_household__family_name__icontains=value)
            | Q(head_of_household__phone_no__icontains=value)
            | Q(head_of_household__phone_no_alternative__icontains=value)
            | Q(head_of_household__documents__document_number__icontains=value)
        ).distinct()

    def filter_by_payment_plan_for_office_search(self, queryset: QuerySet, unicef_id: str) -> QuerySet:
        return queryset.filter(parent__unicef_id=unicef_id)

    def filter_by_grievance_for_office_search(self, queryset: QuerySet, unicef_id: str) -> QuerySet:
        try:
            ticket = GrievanceTicket.objects.get(unicef_id=unicef_id)
        except GrievanceTicket.DoesNotExist:
            return queryset.none()

        payment_ids = set()

        for ticket_type, lookups in GrievanceTicket.SEARCH_TICKET_TYPES_LOOKUPS.items():
            if (
                "payment_record" in lookups
                and hasattr(ticket, ticket_type)
                and (details := getattr(ticket, ticket_type))
            ):
                payment_field = lookups["payment_record"]
                obj = details
                for field in payment_field.split("__"):
                    obj = getattr(obj, field, None)
                    if obj is None:
                        break
                if obj and hasattr(obj, "id"):
                    payment_ids.add(obj.id)

        if payment_ids:
            return queryset.filter(id__in=payment_ids)

        return queryset.none()


class PaymentVerificationRecordFilter(FilterSet):
    search = django_filters.CharFilter(method="search_filter")
    verification_status = django_filters.MultipleChoiceFilter(
        field_name="payment_verifications__status",
        choices=PaymentVerification.STATUS_CHOICES,
    )
    verification_channel = django_filters.MultipleChoiceFilter(
        field_name="payment_verifications__payment_verification_plan__verification_channel",
        choices=PaymentVerificationPlan.VERIFICATION_CHANNEL_CHOICES,
    )
    verification_plan_id = django_filters.UUIDFilter(
        field_name="payment_verifications__payment_verification_plan__id",
    )
    ordering = OrderingFilter(
        fields=(
            ("unicef_id", "unicef_id"),
            (
                "payment_verifications__payment_verification_plan__verification_channel",
                "verification_channel",
            ),
            (
                "payment_verifications__payment_verification_plan__id",
                "verification_plan_id",
            ),
            ("payment_verifications__status", "verification_status"),
            ("head_of_household__full_name", "head_of_household"),
            ("household__unicef_id", "household_unicef_id"),
            ("delivered_quantity", "delivered_quantity"),
            ("payment_verifications__received_amount", "received_amount"),
            ("head_of_household__phone_no", "phone_no"),
            ("head_of_household__phone_no_alternative", "phone_no_alternative"),
        )
    )

    class Meta:
        model = Payment
        fields = []

    def search_filter(self, qs: QuerySet, name: str, value: str) -> "QuerySet[Payment]":
        return qs.filter(unicef_id__istartswith=value)
