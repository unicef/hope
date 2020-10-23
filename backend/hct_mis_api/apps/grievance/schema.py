import graphene
from django_filters import FilterSet, CharFilter
from graphene import relay
from graphene_django import DjangoObjectType

from account.permissions import BaseNodePermissionMixin, DjangoPermissionFilterConnectionField
from core.extended_connection import ExtendedConnection
from grievance.models import GrievanceTicket, TicketNotes, TicketSensitiveDetails, TicketComplaintDetails


class GrievanceTicketFilter(FilterSet):
    business_area = CharFilter(field_name="business_area__slug")

    class Meta:
        fields = ("id", "status")
        model = GrievanceTicket


class GrievanceTicketNode(BaseNodePermissionMixin, DjangoObjectType):
    class Meta:
        model = GrievanceTicket
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection


class TicketNoteNode(BaseNodePermissionMixin, DjangoObjectType):
    class Meta:
        model = TicketNotes
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection


class TicketComplaintDetailsNode(BaseNodePermissionMixin, DjangoObjectType):
    class Meta:
        model = TicketComplaintDetails
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection


class TicketSensitiveDetailsNode(BaseNodePermissionMixin, DjangoObjectType):
    class Meta:
        model = TicketSensitiveDetails
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
