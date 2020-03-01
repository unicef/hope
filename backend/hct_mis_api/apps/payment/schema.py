import graphene
from django_filters import FilterSet, OrderingFilter
from graphene import relay
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from core.schema import ChoiceObject
from core.extended_connection import ExtendedConnection
from payment.models import PaymentRecord, PaymentEntitlement


class PaymentEntitlementNode(DjangoObjectType):
    entitlement_quantity = graphene.Decimal()
    delivered_quantity = graphene.Decimal()

    class Meta:
        model = PaymentEntitlement


class PaymentRecordFilter(FilterSet):
    class Meta:
        fields = (
            "cash_plan",
            "household",
        )
        model = PaymentRecord

    order_by = OrderingFilter(
        fields=(
            "status",
            "name",
            "status_date",
            "cash_assist_id",
            "head_of_household",
            "total_person_covered",
            "distribution_modality",
            "household__household_ca_id",
            "entitlement__entitlement_quantity",
            "entitlement__delivered_quantity",
            "entitlement__delivery_date",
        )
    )


class PaymentRecordNode(DjangoObjectType):
    class Meta:
        model = PaymentRecord
        filter_fields = ["cash_plan", "household"]
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection


class Query(graphene.ObjectType):
    payment_record = relay.Node.Field(PaymentRecordNode)
    all_payment_records = DjangoFilterConnectionField(
        PaymentRecordNode, filterset_class=PaymentRecordFilter,
    )
    payment_record_status_choices = graphene.List(ChoiceObject)
    all_payment_entitlements = graphene.List(PaymentEntitlementNode)

    def resolve_payment_record_status_choices(self, info, **kwargs):
        return [
            {"name": name, "value": value}
            for value, name in PaymentRecord.STATUS_CHOICE
        ]
