import graphene
from django_filters import FilterSet, OrderingFilter
from graphene import relay
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from core.schema import ChoiceObject
from core.extended_connection import ExtendedConnection
from core.utils import to_choice_object
from payment.models import (
    PaymentRecord,
    ServiceProvider,
    CashPlanPaymentVerification,
    PaymentVerification,
)


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
            "household__id",
            "entitlement__entitlement_quantity",
            "entitlement__delivered_quantity",
            "entitlement__delivery_date",
        )
    )


class PaymentVerificationFilter(FilterSet):
    class Meta:
        fields = (
            "cash_plan_payment_verification",
        )
        model = PaymentVerification

    order_by = OrderingFilter(
        fields=(
            "payment_record",
            "status",
            "payment_record__household__head_of_household__full_name",
            "payment_record__household__head_of_household__family_name",
            "payment_record__household",
            "payment_record__household__unicef_id",
            "payment_record__delivered_quantity",
            "received_amount"
        )
    )


class PaymentRecordNode(DjangoObjectType):
    class Meta:
        model = PaymentRecord
        filter_fields = ["cash_plan", "household"]
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection


class ServiceProviderNode(DjangoObjectType):
    class Meta:
        model = ServiceProvider
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection


class CashPlanPaymentVerificationNode(DjangoObjectType):
    class Meta:
        model = CashPlanPaymentVerification
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection


class PaymentVerificationNode(DjangoObjectType):
    class Meta:
        model = PaymentVerification
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection


class Query(graphene.ObjectType):
    payment_record = relay.Node.Field(PaymentRecordNode)
    payment_record_verification = relay.Node.Field(PaymentVerificationNode)
    all_payment_records = DjangoFilterConnectionField(
        PaymentRecordNode, filterset_class=PaymentRecordFilter,
    )
    all_payment_verifications = DjangoFilterConnectionField(
        PaymentVerificationNode, filterset_class=PaymentVerificationFilter,
    )
    payment_record_status_choices = graphene.List(ChoiceObject)
    payment_record_entitlement_card_status_choices = graphene.List(ChoiceObject)
    payment_record_delivery_type_choices = graphene.List(ChoiceObject)
    cash_plan_verification_status_choices = graphene.List(ChoiceObject)
    cash_plan_verification_sampling_choices = graphene.List(ChoiceObject)
    cash_plan_verification_verification_method_choices = graphene.List(
        ChoiceObject
    )
    payment_verification_status_choices = graphene.List(ChoiceObject)

    def resolve_payment_record_status_choices(self, info, **kwargs):
        return to_choice_object(PaymentRecord.STATUS_CHOICE)

    def resolve_payment_record_status_choices(self, info, **kwargs):
        return to_choice_object(PaymentRecord.ENTITLEMENT_CARD_STATUS_CHOICE)

    def resolve_payment_record_delivery_type_choices(self, info, **kwargs):
        return to_choice_object(PaymentRecord.DELIVERY_TYPE_CHOICE)

    def resolve_cash_plan_verification_status_choices(self, info, **kwargs):
        return to_choice_object(CashPlanPaymentVerification.STATUS_CHOICES)

    def resolve_cash_plan_verification_sampling_choices(self, info, **kwargs):
        return to_choice_object(CashPlanPaymentVerification.SAMPLING_CHOICES)

    def resolve_cash_plan_verification_verification_method_choices(
        self, info, **kwargs
    ):
        return to_choice_object(
            CashPlanPaymentVerification.VERIFICATION_METHOD_CHOICES
        )

    def resolve_payment_verification_status_choices(self, info, **kwargs):
        return to_choice_object(PaymentVerification.STATUS_CHOICES)
