import graphene
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django_filters import CharFilter, FilterSet, OrderingFilter
from graphene import relay
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from core.extended_connection import ExtendedConnection
from core.filters import filter_age
from core.schema import ChoiceObject
from core.utils import decode_id_string, to_choice_object
from payment.inputs import GetCashplanVerificationSampleSizeInput
from payment.models import CashPlanPaymentVerification, PaymentRecord, PaymentVerification, ServiceProvider
from payment.rapid_pro.api import RapidProAPI
from payment.utils import get_number_of_samples
from program.models import CashPlan
from steficon.models import Rule


class SteficonRuleFilter(FilterSet):
    class Meta:
        fields = ("enabled", "deprecated")
        model = Rule


class SteficonRuleNode(DjangoObjectType):
    class Meta:
        model = Rule
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection


class Query(graphene.ObjectType):
    all_steficon_rules = DjangoFilterConnectionField(
        SteficonRuleNode,
        filterset_class=SteficonRuleFilter,
    )

    def resolve_all_steficon_rules(self, info, **kwargs):
        return Rule.objects.all()
