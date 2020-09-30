import graphene
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django_filters import FilterSet, OrderingFilter, CharFilter
from graphene import relay
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from account.permissions import BaseNodePermissionMixin, DjangoPermissionFilterConnectionField
from core.extended_connection import ExtendedConnection
from core.filters import filter_age
from core.schema import ChoiceObject
from core.utils import to_choice_object, decode_id_string
from grievance.models import GrievanceTicket, TicketNotes, TicketDeduplicationDetails, TicketPaymentVerificationDetails
from payment.inputs import GetCashplanVerificationSampleSizeInput
from payment.models import (
    PaymentRecord,
    ServiceProvider,
    CashPlanPaymentVerification,
    PaymentVerification,
)
from payment.rapid_pro.api import RapidProAPI
from payment.utils import get_number_of_samples
from program.models import CashPlan


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


class TicketDeduplicationDetailsNode(BaseNodePermissionMixin, DjangoObjectType):
    class Meta:
        model = TicketDeduplicationDetails
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection


class TicketPaymentVerificationDetailsNode(BaseNodePermissionMixin, DjangoObjectType):
    class Meta:
        model = TicketPaymentVerificationDetails
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
