import graphene
from graphene import relay
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from core.schema import ExtendedConnection, ChoiceObject
from payment.models import PaymentRecord, PaymentEntitlement


class PaymentEntitlementNode(DjangoObjectType):

    class Meta:
        model = PaymentEntitlement

class PaymentRecordNode(DjangoObjectType):
    class Meta:
        model = PaymentRecord
        filter_fields = ["cash_plan", "household"]
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection


class Query(graphene.ObjectType):
    payment_record = relay.Node.Field(PaymentRecordNode)
    all_payment_records = DjangoFilterConnectionField(PaymentRecordNode)
    payment_record_status_choices = graphene.List(ChoiceObject)
    all_payment_entitlements = graphene.List(PaymentEntitlementNode)
    def resolve_payment_record_status_choices(self, info, **kwargs):
        return [
            {"name": name, "value": value}
            for value, name in PaymentRecord.STATUS_CHOICE
        ]
