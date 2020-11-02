import graphene
from django.db.models import Q
from django_filters import FilterSet, CharFilter, ModelMultipleChoiceFilter, OrderingFilter, TypedMultipleChoiceFilter
from graphene import relay
from graphene_django import DjangoObjectType

from account.permissions import BaseNodePermissionMixin, DjangoPermissionFilterConnectionField
from core.extended_connection import ExtendedConnection
from core.filters import DateTimeRangeFilter
from core.models import AdminArea
from grievance.models import GrievanceTicket, TicketNotes, TicketSensitiveDetails, TicketComplaintDetails
from payment.models import ServiceProvider


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
        fields = ("id", "category")
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


class GrievanceTicketNode(BaseNodePermissionMixin, DjangoObjectType):
    class Meta:
        model = GrievanceTicket
        convert_choices_to_enum = False
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection


class TicketNoteNode(DjangoObjectType):
    class Meta:
        model = TicketNotes
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


class Query(graphene.ObjectType):
    grievance_ticket = relay.Node.Field(GrievanceTicketNode)
    all_grievance_ticket = DjangoPermissionFilterConnectionField(
        GrievanceTicketNode,
        filterset_class=GrievanceTicketFilter,
        # TODO Enable permissions below
        # permission_classes=(hopePermissionClass("PERMISSION_PROGRAM.LIST"),)
    )
