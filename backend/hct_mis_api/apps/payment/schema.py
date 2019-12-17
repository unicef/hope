import graphene
from graphene import relay
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from payment.models import PaymentRecord


class PaymentRecordNode(DjangoObjectType):
    class Meta:
        model = PaymentRecord
        filter_fields = ['cash_plan',
                         'household']
        interfaces = (relay.Node,)


class Query(graphene.ObjectType):
    payment_record = relay.Node.Field(PaymentRecordNode)
    all_payment_records = DjangoFilterConnectionField(PaymentRecordNode)
