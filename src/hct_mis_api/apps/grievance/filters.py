import logging
from typing import Any, List

from django.db.models import Count, F, Func, Q, QuerySet, Window

from django_filters import (
    BooleanFilter,
    CharFilter,
    ChoiceFilter,
    FilterSet,
    MultipleChoiceFilter,
    OrderingFilter,
    UUIDFilter,
)
from django_filters import rest_framework as filters

from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.grievance.constants import PRIORITY_CHOICES, URGENCY_CHOICES
from hct_mis_api.apps.grievance.models import GrievanceTicket, TicketNote
from hct_mis_api.apps.household.models import HEAD, Individual
from hct_mis_api.apps.program.models import Program

logger = logging.getLogger(__name__)


class IsNull(Func):
    template = "%(expressions)s IS NULL"


class GrievanceOrderingFilter(OrderingFilter):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.extra["choices"] += [
            ("linked_tickets", "Linked tickets"),
            ("-linked_tickets", "Linked tickets (descending)"),
        ]

    def filter(self, qs: QuerySet, value: List[str]) -> QuerySet:
        if value and any(v in ["linked_tickets", "-linked_tickets"] for v in value):
            qs = super().filter(qs, value)
            qs = (
                qs.annotate(linked=Count("linked_tickets"))
                .annotate(linked_related=Count("linked_tickets"))
                .annotate(total_linked=F("linked") + F("linked_related"))
                .annotate(
                    household_unicef_id_count=Window(
                        expression=Count("household_unicef_id"),
                        partition_by=[F("household_unicef_id")],
                        order_by=[F("household_unicef_id")],
                    )
                )
                .order_by(F("total_linked") + F("household_unicef_id_count") - 1, "unicef_id")
            )

            if value == ["-linked_tickets"]:
                return qs.reverse()
            return qs
        return super().filter(qs, value)


class GrievanceTicketFilter(FilterSet):
    SEARCH_TICKET_TYPES_LOOKUPS = {
        "complaint_ticket_details": {
            "individual": ("preferred_language",),
        },
        "sensitive_ticket_details": {
            "individual": ("preferred_language",),
        },
        "individual_data_update_ticket_details": {
            "individual": ("preferred_language",),
        },
        "system_flagging_ticket_details": {"golden_records_individual": ("preferred_language",)},
        "needs_adjudication_ticket_details": {"golden_records_individual": ("preferred_language",)},
    }
    TICKET_TYPES_WITH_FSP = (
        ("complaint_ticket_details", "payment__service_provider__full_name"),
        ("complaint_ticket_details", "payment__financial_service_provider__name"),
        ("sensitive_ticket_details", "payment__service_provider__full_name"),
        ("sensitive_ticket_details", "payment__financial_service_provider__name"),
        (
            "payment_verification_ticket_details",
            "payment_verification__payment__financial_service_provider__name",
        ),
    )
    search = CharFilter(method="search_filter")
    document_type = CharFilter(method="document_type_filter")
    document_number = CharFilter(method="document_number_filter")

    status = MultipleChoiceFilter(field_name="status", choices=GrievanceTicket.STATUS_CHOICES)
    fsp = CharFilter(method="fsp_filter")
    cash_plan = CharFilter(
        field_name="payment_verification_ticket_details",
        lookup_expr="payment_verification__payment_verification_plan__payment_plan_id",
    )
    created_at = filters.DateFromToRangeFilter(field_name="created_at")

    issue_type = ChoiceFilter(field_name="issue_type", choices=GrievanceTicket.ALL_ISSUE_TYPES)
    score_min = CharFilter(field_name="needs_adjudication_ticket_details__score_min", lookup_expr="gte")
    score_max = CharFilter(field_name="needs_adjudication_ticket_details__score_max", lookup_expr="lte")
    household = CharFilter(field_name="household_unicef_id")
    preferred_language = CharFilter(method="preferred_language_filter")
    priority = ChoiceFilter(field_name="priority", choices=PRIORITY_CHOICES)
    urgency = ChoiceFilter(field_name="urgency", choices=URGENCY_CHOICES)
    grievance_type = CharFilter(method="filter_grievance_type")
    grievance_status = CharFilter(method="filter_grievance_status")
    program = CharFilter(method="filter_by_program")
    is_active_program = BooleanFilter(method="filter_is_active_program")
    is_cross_area = BooleanFilter(method="filter_is_cross_area")
    admin1 = CharFilter(field_name="admin2__parent_id")
    household_id = CharFilter(method="filter_by_household")
    individual_id = CharFilter(method="filter_by_individual")
    payment_record_ids = filters.BaseInFilter(method="filter_by_payment_record")

    class Meta:
        fields = {
            "id": ["exact", "startswith"],
            "category": ["exact"],
            "area": ["exact", "startswith"],
            "assigned_to": ["exact"],
            "registration_data_import": ["exact"],
            "admin2": ["exact"],
            "created_by": ["exact"],
        }
        model = GrievanceTicket

    order_by = GrievanceOrderingFilter(
        fields=(
            "unicef_id",
            "status",
            "assigned_to__last_name",
            "category",
            "created_at",
            "households_count",
            "user_modified",
            "household_unicef_id",
            "issue_type",
            "priority",
            "urgency",
            "total_days",
        )
    )

    def filter_by_program(self, qs: QuerySet, name: str, value: str) -> QuerySet:
        if value:
            return qs.filter(programs__slug=value)
        return qs

    def preferred_language_filter(self, qs: QuerySet, name: str, value: str) -> QuerySet:  # pragma: no cover
        q_obj = Q()
        for ticket_type, ticket_fields in self.SEARCH_TICKET_TYPES_LOOKUPS.items():
            for field, lookups in ticket_fields.items():
                for lookup in lookups:
                    if lookup == "preferred_language":
                        q_obj |= Q(**{f"{ticket_type}__{field}__{lookup}": value})
        return qs.filter(q_obj)

    def search_filter(self, qs: QuerySet, name: str, value: str) -> QuerySet:
        search = value.strip()
        query = Q()

        values = list(map(str.strip, search.split(",")))
        if len(values) > 1:
            query |= Q(unicef_id__in=values)
        else:
            query |= Q(unicef_id__icontains=search)
            if search.startswith("HH-"):
                return qs.filter(household_unicef_id__istartswith=search)
            if search.startswith("IND-"):
                household_unicef_ids = (
                    Individual.objects.filter(unicef_id__istartswith=search)
                    .distinct("household__unicef_id")
                    .values_list("household__unicef_id", flat=True)
                )
                return qs.filter(household_unicef_id__in=household_unicef_ids)
            if search.startswith("GRV-"):
                return qs.filter(unicef_id__istartswith=search)

        query |= Q(household_unicef_id__icontains=search)
        unicef_ids = (
            Individual.objects.filter(relationship=HEAD)
            .filter(
                Q(full_name__icontains=search)
                | Q(detail_id__icontains=search)
                | Q(program_registration_id__icontains=search)
                | Q(phone_no__icontains=search)
                | Q(phone_no_alternative__icontains=search)
                | Q(unicef_id=search)
            )
            .select_related("household")
            .values_list("household__unicef_id", flat=True)
        )
        query |= Q(household_unicef_id__in=unicef_ids)
        return qs.filter(query)

    def document_type_filter(self, qs: QuerySet, name: str, value: str) -> QuerySet:
        return qs

    def document_number_filter(self, qs: QuerySet, name: str, value: str) -> QuerySet:
        document_number = value.strip()
        document_type = self.data.get("document_type")
        unicef_ids = (
            Individual.objects.filter(
                Q(relationship=HEAD)
                & Q(documents__type__key=document_type)
                & Q(documents__document_number__icontains=document_number)
            )
            .select_related("household")
            .values_list("household__unicef_id", flat=True)
        )
        return qs.filter(household_unicef_id__in=unicef_ids)

    def fsp_filter(self, qs: QuerySet, name: str, value: str) -> QuerySet:
        if value:
            q_obj = Q()
            for ticket_type, path_to_fsp in self.TICKET_TYPES_WITH_FSP:
                q_obj |= Q(**{f"{ticket_type}__{path_to_fsp}__istartswith": value})

            return qs.filter(q_obj)
        return qs

    def filter_grievance_type(self, qs: QuerySet, name: Any, val: str) -> QuerySet:
        choices = dict(GrievanceTicket.CATEGORY_CHOICES)
        user_generated = [value for value in choices if value in dict(GrievanceTicket.MANUAL_CATEGORIES)]

        if val == "system":
            return qs.filter(~Q(category__in=user_generated))
        elif val == "user":
            return qs.filter(category__in=user_generated)
        return qs

    def filter_grievance_status(self, qs: QuerySet, name: Any, val: str) -> QuerySet:
        if val == "active":
            return qs.filter(~Q(status=GrievanceTicket.STATUS_CLOSED))
        return qs

    def filter_is_active_program(self, qs: QuerySet, name: str, value: bool) -> QuerySet:
        if value is True:
            return qs.filter(programs__status=Program.ACTIVE)
        elif value is False:
            return qs.filter(programs__status=Program.FINISHED)
        else:
            return qs

    def filter_is_cross_area(self, qs: QuerySet, name: str, value: bool) -> QuerySet:
        user = self.request.user
        business_area = BusinessArea.objects.get(slug=self.request.parser_context["kwargs"]["business_area_slug"])
        program_slug = self.request.parser_context["kwargs"].get("program_slug")
        program = Program.objects.filter(slug=program_slug, business_area=business_area).first()

        perm = Permissions.GRIEVANCES_CROSS_AREA_FILTER.value
        if (
            value is True
            and user.has_perm(perm, program or business_area)
            and (not program or not user.partner.has_area_limits_in_program(program.id))
        ):
            return qs.filter(needs_adjudication_ticket_details__is_cross_area=True)
        else:
            return qs

    def _get_ticket_filters(self, lookup: str, value: str) -> Q:
        query = Q()
        for ticket_type, lookup_objs in GrievanceTicket.SEARCH_TICKET_TYPES_LOOKUPS.items():
            if real_lookup := lookup_objs.get(lookup):
                query |= Q(**{f"{ticket_type}__{real_lookup}": value})
        return query

    def filter_by_individual(self, qs: QuerySet, name: str, value: str) -> QuerySet:
        individual_q = self._get_ticket_filters("individual", value)
        return qs.filter(individual_q)

    def filter_by_household(self, qs: QuerySet, name: str, value: str) -> QuerySet:
        household_q = self._get_ticket_filters("household", value)
        return qs.filter(household_q)

    def filter_by_payment_record(self, qs: QuerySet, name: str, value: List[str]) -> QuerySet:
        return qs.filter(
            Q(complaint_ticket_details__payment_id__in=value) | Q(sensitive_ticket_details__payment_id__in=value)
        )


class TicketNoteFilter(FilterSet):
    ticket = UUIDFilter(field_name="ticket", required=True)

    class Meta:
        fields = ("id",)
        model = TicketNote
