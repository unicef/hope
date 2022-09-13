from django.db import models
from django.db.models import Q, Count

from django_filters import (
    CharFilter,
    ChoiceFilter,
    FilterSet,
    ModelChoiceFilter,
    ModelMultipleChoiceFilter,
    MultipleChoiceFilter,
    OrderingFilter,
    TypedMultipleChoiceFilter,
    UUIDFilter,
)

from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.es_filters import ElasticSearchFilterSet
from hct_mis_api.apps.core.filters import DateTimeRangeFilter, IntegerFilter
from hct_mis_api.apps.geo.models import Area, ValidityQuerySet
from hct_mis_api.apps.grievance.es_query import create_es_query, execute_es_query
from hct_mis_api.apps.grievance.constants import PRIORITY_CHOICES, URGENCY_CHOICES
from hct_mis_api.apps.grievance.models import GrievanceTicket, TicketNote
from hct_mis_api.apps.household.models import Household, Individual
from hct_mis_api.apps.payment.models import PaymentRecord
from hct_mis_api.apps.core.utils import choices_to_dict


class CustomOrderingFilter(OrderingFilter):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.extra['choices'] += [
            ('linked_tickets', 'Linked tickets'),
            ('-linked_tickets', 'Linked tickets (descending)'),
        ]

    def filter(self, qs, value):
        if any(v in ['linked_tickets', '-linked_tickets'] for v in value):
            return qs.annotate(linked_tickets_count=Count("linked_tickets")).order_by(f"{value[0]}_count")
        return super().filter(qs, value)


class GrievanceTicketElasticSearchFilterSet(ElasticSearchFilterSet):
    USE_SPECIFIC_FIELDS_AS_ELASTIC_SEARCH = (
        "search",
        "created_at_range",
        "assigned_to",
        "registration_data_import",
        "status",
        "issue_type",
        "category",
        "admin",
        "priority",
        "urgency",
        "grievance_type",
        "business_area",
    )

    def elasticsearch_filter_queryset(self):
        grievance_es_query_dict = create_es_query(self.prepare_filters(self.USE_SPECIFIC_FIELDS_AS_ELASTIC_SEARCH))
        grievance_ids = execute_es_query(grievance_es_query_dict)
        return grievance_ids

    def prepare_filters(self, allowed_fields):
        filters = {}
        for field in allowed_fields:
            if self.form.data.get(field):
                if field in (
                    "category",
                    "status",
                    "issue_type",
                    "priority",
                    "urgency",
                    "admin",
                    "registration_data_import",
                ):
                    filters[field] = self.form.data[field]
                else:
                    filters[field] = self.form.cleaned_data[field]

        if isinstance(filters.get("admin"), ValidityQuerySet):
            filters.pop("admin")

        return filters


class GrievanceTicketFilter(GrievanceTicketElasticSearchFilterSet):
    SEARCH_TICKET_TYPES_LOOKUPS = {
        "complaint_ticket_details": {
            "individual": (
                "full_name",
                "unicef_id",
                "phone_no",
                "phone_no_alternative",
            ),
            "household": ("unicef_id",),
        },
        "sensitive_ticket_details": {
            "individual": (
                "full_name",
                "unicef_id",
                "phone_no",
                "phone_no_alternative",
            ),
            "household": ("unicef_id",),
        },
        "individual_data_update_ticket_details": {
            "individual": (
                "full_name",
                "unicef_id",
                "phone_no",
                "phone_no_alternative",
            ),
        },
        "add_individual_ticket_details": {"household": ("unicef_id",)},
        "system_flagging_ticket_details": {
            "golden_records_individual": (
                "full_name",
                "unicef_id",
                "phone_no",
                "phone_no_alternative",
            )
        },
        "needs_adjudication_ticket_details": {
            "golden_records_individual": (
                "full_name",
                "unicef_id",
                "phone_no",
                "phone_no_alternative",
            )
        },
    }
    TICKET_TYPES_WITH_FSP = (
        ("complaint_ticket_details", "payment_record__service_provider"),
        ("sensitive_ticket_details", "payment_record__service_provider"),
        (
            "payment_verification_ticket_details",
            "payment_verifications__payment_record__service_provider",
        ),
    )
    business_area = CharFilter(field_name="business_area__slug", required=True)
    search = CharFilter(method="search_filter")

    status = TypedMultipleChoiceFilter(field_name="status", choices=GrievanceTicket.STATUS_CHOICES, coerce=int)
    fsp = CharFilter(method="fsp_filter")
    admin = ModelMultipleChoiceFilter(
        field_name="admin",
        method="admin_filter",
        queryset=Area.objects.filter(area_type__area_level=2),
    )
    cash_plan = CharFilter(
        field_name="payment_verification_ticket_details",
        lookup_expr="payment_verifications__cash_plan_payment_verification__cash_plan",
    )
    created_at_range = DateTimeRangeFilter(field_name="created_at")
    permissions = MultipleChoiceFilter(choices=Permissions.choices(), method="permissions_filter")
    issue_type = ChoiceFilter(field_name="issue_type", choices=GrievanceTicket.ALL_ISSUE_TYPES)
    score_min = CharFilter(field_name="needs_adjudication_ticket_details__score_min", lookup_expr="gte")
    score_max = CharFilter(field_name="needs_adjudication_ticket_details__score_max", lookup_expr="lte")
    household = CharFilter(field_name="household_unicef_id")
    priority = ChoiceFilter(field_name="priority", choices=PRIORITY_CHOICES)
    urgency = ChoiceFilter(field_name="urgency", choices=URGENCY_CHOICES)
    grievance_type = CharFilter(method="filter_grievance_type")
    grievance_status = CharFilter(method="filter_grievance_status")
    total_days = IntegerFilter(field_name="total_days")

    class Meta:
        fields = {
            "id": ["exact", "startswith"],
            "category": ["exact"],
            "area": ["exact", "startswith"],
            "assigned_to": ["exact"],
            "registration_data_import": ["exact"],
        }
        model = GrievanceTicket

    order_by = CustomOrderingFilter(
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

    def search_filter(self, qs, name, value):
        label, value = tuple(value.split(" ", 1))
        if label == "ticket_id":
            q = Q(unicef_id=value)
        elif label == "ticket_hh_id":
            q = Q(household_unicef_id=value)
        else:
            ids = (
                Individual.objects.filter(Q(family_name=value) & Q(relationship="HEAD"))
                .select_related("household")
                .values_list("household__unicef_id", flat=True)
            )
            q = Q(household_unicef_id__in=ids)
        return qs.filter(q)

    def fsp_filter(self, qs, name, value):
        if value:
            q_obj = Q()
            for ticket_type, path_to_fsp in self.TICKET_TYPES_WITH_FSP:
                q_obj |= Q(**{f"{ticket_type}__{path_to_fsp}__full_name__istartswith": value})

            return qs.filter(q_obj)
        return qs

    def admin_filter(self, qs, name, value):
        if value:
            return qs.filter(admin2__in=[admin.id for admin in value])
        return qs

    def permissions_filter(self, qs, name, value):
        can_view_ex_sensitive_all = Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE.value in value
        can_view_sensitive_all = Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE.value in value
        can_view_ex_sensitive_creator = Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE_AS_CREATOR.value in value
        can_view_ex_sensitive_owner = Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE_AS_OWNER.value in value
        can_view_sensitive_creator = Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE_AS_CREATOR.value in value
        can_view_sensitive_owner = Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE_AS_OWNER.value in value

        # can view all
        if can_view_ex_sensitive_all and can_view_sensitive_all:
            return qs

        filters_1 = {}
        filters_1_exclude = {}
        filters_2 = {}
        filters_2_exclude = {}
        sensitive_category_filter = {"category": GrievanceTicket.CATEGORY_SENSITIVE_GRIEVANCE}
        created_by_filter = {"created_by": self.request.user}
        assigned_to_filter = {"assigned_to": self.request.user}

        # can view one group full and potentially some of other group
        if can_view_ex_sensitive_all or can_view_sensitive_all:
            if can_view_sensitive_creator or can_view_ex_sensitive_creator:
                filters_1.update(created_by_filter)
            if can_view_sensitive_owner or can_view_ex_sensitive_owner:
                filters_2.update(assigned_to_filter)

            if can_view_ex_sensitive_all:
                return qs.filter(~Q(**sensitive_category_filter) | Q(**filters_1) | Q(**filters_2))
            else:
                return qs.filter(Q(**sensitive_category_filter) | Q(**filters_1) | Q(**filters_1))

        else:
            # no full lists so only creator and/or owner lists
            if can_view_ex_sensitive_creator:
                filters_1.update(created_by_filter)
                if not can_view_sensitive_creator:
                    filters_1_exclude.update(sensitive_category_filter)
            if can_view_ex_sensitive_owner:
                filters_2.update(assigned_to_filter)
                if not can_view_sensitive_owner:
                    filters_2_exclude.update(sensitive_category_filter)
            if filters_1 or filters_2:
                return qs.filter(
                    Q(Q(**filters_1), ~Q(**filters_1_exclude)) | Q(Q(**filters_2), ~Q(**filters_2_exclude))
                )
            else:
                return GrievanceTicket.objects.none()

    def filter_grievance_type(self, qs, name, val):
        choices = choices_to_dict(GrievanceTicket.CATEGORY_CHOICES)
        user_generated = []
        for value in choices:
            if value in GrievanceTicket.MANUAL_CATEGORIES:
                user_generated.append(value)
        if val == "user":
            return qs.filter(category__in=user_generated)
        elif val == "system":
            return qs.filter(~Q(category__in=user_generated))
        return qs

    def filter_grievance_status(self, qs, name, val):
        if val == "active":
            return qs.filter(~Q(status=GrievanceTicket.STATUS_CLOSED))
        return qs


class ExistingGrievanceTicketFilter(FilterSet):
    business_area = CharFilter(field_name="business_area__slug", required=True)
    category = ChoiceFilter(field_name="category", choices=GrievanceTicket.CATEGORY_CHOICES)
    issue_type = ChoiceFilter(field_name="issue_type", choices=GrievanceTicket.ALL_ISSUE_TYPES)
    household = ModelChoiceFilter(queryset=Household.objects.all())
    individual = ModelChoiceFilter(queryset=Individual.objects.all())
    payment_record = ModelMultipleChoiceFilter(queryset=PaymentRecord.objects.all())
    permissions = MultipleChoiceFilter(choices=Permissions.choices(), method="permissions_filter")

    class Meta:
        fields = ("id",)
        model = GrievanceTicket

    order_by = OrderingFilter(fields=("id",))

    def prepare_ticket_filters(self, lookup, obj):
        types_and_lookups = GrievanceTicket.SEARCH_TICKET_TYPES_LOOKUPS

        q_obj = Q()
        for ticket_type, lookup_objs in types_and_lookups.items():
            real_lookup = lookup_objs.get(lookup)
            if real_lookup:
                q_obj |= Q(**{f"{ticket_type}__{real_lookup}": obj})
        return q_obj

    def filter_queryset(self, queryset):
        cleaned_data = self.form.cleaned_data

        payment_record_objects = cleaned_data.pop("payment_record", None)
        household_object = cleaned_data.pop("household", None)
        individual_object = cleaned_data.pop("individual", None)
        # if any of these filters were passed in as wrong ids we need to return an empty queryset instead of completely ignore that filter value
        # as expected in OtherRelatedTickets.tsx component when passing random household id
        if (household_object is None and self.form.data.get("household")) or (
            payment_record_objects is None
            and self.form.data.get("payment_record")
            or (individual_object is None and self.form.data.get("individual"))
        ):
            return queryset.none()
        if household_object is None:
            queryset.model.objects.none()
        for name, value in cleaned_data.items():
            queryset = self.filters[name].filter(queryset, value)
            assert isinstance(
                queryset, models.QuerySet
            ), "Expected '{}.{}' to return a QuerySet, but got a {} instead.".format(
                type(self).__name__,
                name,
                type(queryset).__name__,
            )

        if payment_record_objects:
            q_obj = Q()
            for payment_record in payment_record_objects:
                q_obj |= self.prepare_ticket_filters("payment_record", payment_record)
            queryset = queryset.filter(q_obj)
        if household_object:
            q_obj = self.prepare_ticket_filters("household", household_object)
            queryset = queryset.filter(q_obj)
        if individual_object:
            q_obj = self.prepare_ticket_filters("individual", individual_object)
            queryset = queryset.filter(q_obj)

        return queryset

    def permissions_filter(self, qs, name, value):
        return GrievanceTicketFilter.permissions_filter(self, qs, name, value)


class TicketNoteFilter(FilterSet):
    ticket = UUIDFilter(field_name="ticket", required=True)

    class Meta:
        fields = ("id",)
        model = TicketNote
