import graphene
from graphene import relay
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from payment.models import PaymentRecord


class PaymentRecordNode(DjangoObjectType):
    class Meta:
        model = PaymentRecord
        filter_fields = ['cash_plan', 'household']
        interfaces = (relay.Node,)


class Query(graphene.ObjectType):
    payment_record = relay.Node.Field(PaymentRecordNode)
    all_payment_records = DjangoFilterConnectionField(PaymentRecordNode)
    payment_delivery_type_choices = graphene.List(graphene.List(
        graphene.String)
    )

    def resolve_payment_delivery_type_choices(self, info, **kwargs):
        return PaymentRecord.DELIVERY_TYPE_CHOICE
