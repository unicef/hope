import graphene
from django.db import models
from django.db.models import Q
from django_filters import (
    FilterSet,
    CharFilter,
    ModelMultipleChoiceFilter,
    OrderingFilter,
    TypedMultipleChoiceFilter,
    ChoiceFilter,
    ModelChoiceFilter,
    UUIDFilter,
)
from graphene import relay
from graphene_django import DjangoObjectType

from account.permissions import BaseNodePermissionMixin, DjangoPermissionFilterConnectionField
from core.extended_connection import ExtendedConnection
from core.filters import DateTimeRangeFilter
from core.models import AdminArea
from core.schema import ChoiceObject
from core.utils import to_choice_object, choices_to_dict
from grievance.models import (
    GrievanceTicket,
    TicketNote,
    TicketSensitiveDetails,
    TicketComplaintDetails,
    TicketDeleteIndividualDetails,
    TicketIndividualDataUpdateDetails,
    TicketAddIndividualDetails,
    TicketHouseholdDataUpdateDetails,
)
from household.models import Household, Individual
from payment.models import ServiceProvider, PaymentRecord
from utils.schema import Arg


class GrievanceTicketFilter(FilterSet):
    SEARCH_TICKET_TYPES_LOOKUPS = {
        "complaint_ticket_details": {
            "individual": ("full_name", "id", "phone_no", "phone_no_alternative"),
            "household": ("id",),
        },
        "sensitive_ticket_details": {
            "individual": ("full_name", "id", "phone_no", "phone_no_alternative"),
            "household": ("id",),
        },
        "individual_data_update_ticket_details": {
            "individual": ("full_name", "id", "phone_no", "phone_no_alternative"),
        },
        "add_individual_ticket_details": {"household": ("id",)},
    }
    TICKET_TYPES_WITH_FSP = ("complaint_ticket_details", "sensitive_ticket_details")

    business_area = CharFilter(field_name="business_area__slug", required=True)
    search = CharFilter(method="search_filter")
    status = TypedMultipleChoiceFilter(field_name="status", choices=GrievanceTicket.STATUS_CHOICES, coerce=int)
    fsp = ModelMultipleChoiceFilter(method="fsp_filter", queryset=ServiceProvider.objects.all())
    admin = ModelMultipleChoiceFilter(
        field_name="admin", method="admin_filter", queryset=AdminArea.objects.filter(admin_area_type__admin_level=2)
    )
    created_at_range = DateTimeRangeFilter(field_name="created_at")

    class Meta:
        fields = {
            "id": ["exact", "icontains"],
            "category": ["exact"],
            "area": ["exact", "icontains"],
            "assigned_to": ["exact"],
        }
        model = GrievanceTicket

    order_by = OrderingFilter(
        fields=("id", "status", "assigned_to__full_name", "category", "created_at", "households_count", "user_modified")
    )

    def search_filter(self, qs, name, value):
        values = value.split(" ")
        q_obj = Q()
        for value in values:
            q_obj |= Q(id__icontains=value)
            for ticket_type, ticket_fields in self.SEARCH_TICKET_TYPES_LOOKUPS.items():
                for field, lookups in ticket_fields.items():
                    for lookup in lookups:
                        q_obj |= Q(**{f"{ticket_type}__{field}__{lookup}__icontains": value})

        return qs.filter(q_obj)

    def fsp_filter(self, qs, name, value):
        if value:
            q_obj = Q()
            for ticket_type in self.TICKET_TYPES_WITH_FSP:
                q_obj |= Q(**{f"{ticket_type}__payment_record__service_provider__in": value})

            return qs.filter(q_obj)
        return qs

    def admin_filter(self, qs, name, value):
        if value:
            return qs.filter(admin__in=[admin.title for admin in value])
        return qs


class ExistingGrievanceTicketFilter(FilterSet):
    SEARCH_TICKET_TYPES_LOOKUPS = {
        "complaint_ticket_details": ("individual", "household", "payment_record",),
        "sensitive_ticket_details": ("individual", "household", "payment_record",),
        "individual_data_update_ticket_details": ("individual",),
        "add_individual_ticket_details": ("household",),
    }

    business_area = CharFilter(field_name="business_area__slug", required=True)
    category = ChoiceFilter(field_name="category", required=True, choices=GrievanceTicket.CATEGORY_CHOICES)
    issue_type = ChoiceFilter(field_name="issue_type", choices=GrievanceTicket.ALL_ISSUE_TYPES)
    household = ModelChoiceFilter(queryset=Household.objects.all())
    individual = ModelChoiceFilter(queryset=Individual.objects.all())
    payment_record = ModelMultipleChoiceFilter(queryset=PaymentRecord.objects.all())

    class Meta:
        fields = ("id",)
        model = GrievanceTicket

    order_by = OrderingFilter(fields=("id",))

    def prepare_ticket_filters(self, lookup, obj):
        types_and_lookups = self.SEARCH_TICKET_TYPES_LOOKUPS
        ticket_types = types_and_lookups.keys()

        q_obj = Q()
        for ticket_type in ticket_types:
            has_lookup = lookup in types_and_lookups[ticket_type]
            if has_lookup:
                q_obj |= Q(**{f"{ticket_type}__{lookup}": obj})

        return q_obj

    def filter_queryset(self, queryset):
        cleaned_data = self.form.cleaned_data

        payment_record_objects = cleaned_data.pop("payment_record")
        household_object = cleaned_data.pop("household")
        individual_object = cleaned_data.pop("individual")

        for name, value in cleaned_data.items():
            queryset = self.filters[name].filter(queryset, value)
            assert isinstance(queryset, models.QuerySet), (
                "Expected '%s.%s' to return a QuerySet, but got a %s instead."
                % (type(self).__name__, name, type(queryset).__name__)
            )

        if payment_record_objects:
            q_obj = Q()
            for payment_record in payment_record_objects:
                q_obj |= self.prepare_ticket_filters("payment_record", payment_record)
            return queryset.filter(q_obj)
        elif household_object:
            q_obj = self.prepare_ticket_filters("household", household_object)
            return queryset.filter(q_obj)
        elif individual_object:
            q_obj = self.prepare_ticket_filters("individual", individual_object)
            return queryset.filter(q_obj)

        return queryset


class TicketNoteFilter(FilterSet):
    ticket = UUIDFilter(field_name="ticket", required=True)

    class Meta:
        fields = ("id",)
        model = TicketNote


class GrievanceTicketNode(BaseNodePermissionMixin, DjangoObjectType):
    class Meta:
        model = GrievanceTicket
        convert_choices_to_enum = False
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection


class TicketNoteNode(DjangoObjectType):
    class Meta:
        model = TicketNote
        exclude = ("ticket",)
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection


class TicketComplaintDetailsNode(DjangoObjectType):
    class Meta:
        model = TicketComplaintDetails
        exclude = ("ticket",)
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection


class TicketSensitiveDetailsNode(DjangoObjectType):
    class Meta:
        model = TicketSensitiveDetails
        exclude = ("ticket",)
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection


class TicketIndividualDataUpdateDetailsNode(DjangoObjectType):
    individual_data = Arg()

    class Meta:
        model = TicketIndividualDataUpdateDetails
        exclude = ("ticket",)
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection


class TicketAddIndividualDetailsNode(DjangoObjectType):
    individual_data = Arg()

    class Meta:
        model = TicketAddIndividualDetails
        exclude = ("ticket",)
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection


class TicketDeleteIndividualDetailsNode(DjangoObjectType):
    individual_data = Arg()

    class Meta:
        model = TicketDeleteIndividualDetails
        exclude = ("ticket",)
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection


class TicketHouseholdDataUpdateDetailsNode(DjangoObjectType):
    household_data = Arg()

    class Meta:
        model = TicketHouseholdDataUpdateDetails
        exclude = ("ticket",)
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection


class IssueTypesObject(graphene.ObjectType):
    category = graphene.String()
    label = graphene.String()
    sub_categories = graphene.List(ChoiceObject)

    def resolve_sub_categories(self, info):
        return [{"name": value, "value": key} for key, value in self.get("sub_categories").items()]


class Query(graphene.ObjectType):
    grievance_ticket = relay.Node.Field(GrievanceTicketNode)
    all_grievance_ticket = DjangoPermissionFilterConnectionField(
        GrievanceTicketNode,
        filterset_class=GrievanceTicketFilter,
        # TODO Enable permissions below
        # permission_classes=(hopePermissionClass("PERMISSION_PROGRAM.LIST"),)
    )
    existing_grievance_tickets = DjangoPermissionFilterConnectionField(
        GrievanceTicketNode,
        filterset_class=ExistingGrievanceTicketFilter,
        # TODO Enable permissions below
        # permission_classes=(hopePermissionClass("PERMISSION_PROGRAM.LIST"),))
    )
    all_ticket_notes = DjangoPermissionFilterConnectionField(TicketNoteNode, filterset_class=TicketNoteFilter,)
    grievance_ticket_status_choices = graphene.List(ChoiceObject)
    grievance_ticket_category_choices = graphene.List(ChoiceObject)
    grievance_ticket_issue_type_choices = graphene.List(IssueTypesObject)

    def resolve_grievance_ticket_status_choices(self, info, **kwargs):
        return to_choice_object(GrievanceTicket.STATUS_CHOICES)

    def resolve_grievance_ticket_category_choices(self, info, **kwargs):
        return to_choice_object(GrievanceTicket.CATEGORY_CHOICES)

    def resolve_grievance_ticket_issue_type_choices(self, info, **kwargs):
        categories = choices_to_dict(GrievanceTicket.CATEGORY_CHOICES)
        return [
            {"category": key, "label": categories[key], "sub_categories": value}
            for (key, value) in GrievanceTicket.ISSUE_TYPES_CHOICES.items()
        ]
