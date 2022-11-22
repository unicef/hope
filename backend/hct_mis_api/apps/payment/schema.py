import graphene
from django.db.models import Case, CharField, Q, Value, When
from django.shortcuts import get_object_or_404
from graphene import relay
from graphene_django import DjangoObjectType

from hct_mis_api.apps.account.permissions import (
    BaseNodePermissionMixin,
    DjangoPermissionFilterConnectionField,
    Permissions,
    hopePermissionClass,
)
from hct_mis_api.apps.activity_log.models import LogEntry
from hct_mis_api.apps.activity_log.schema import LogEntryNode
from hct_mis_api.apps.core.extended_connection import ExtendedConnection
from hct_mis_api.apps.core.schema import ChoiceObject
from hct_mis_api.apps.core.utils import (
    decode_id_string,
    to_choice_object,
)
from hct_mis_api.apps.household.models import STATUS_ACTIVE, STATUS_INACTIVE
from hct_mis_api.apps.payment.filters import (
    CashPlanPaymentVerificationFilter,
    PaymentRecordFilter,
    PaymentVerificationFilter,
    PaymentVerificationLogEntryFilter,
)
from hct_mis_api.apps.payment.inputs import GetCashplanVerificationSampleSizeInput
from hct_mis_api.apps.payment.models import (
    CashPlanPaymentVerification,
    CashPlanPaymentVerificationSummary,
    PaymentRecord,
    PaymentVerification,
    ServiceProvider,
)
from hct_mis_api.apps.payment.services.rapid_pro.api import RapidProAPI
from hct_mis_api.apps.payment.services.sampling import Sampling
from hct_mis_api.apps.payment.tasks.CheckRapidProVerificationTask import (
    does_payment_record_have_right_hoh_phone_number,
)
from hct_mis_api.apps.program.models import CashPlan
from hct_mis_api.apps.utils.schema import (
    ChartDetailedDatasetsNode,
)


class RapidProFlowResult(graphene.ObjectType):
    key = graphene.String()
    name = graphene.String()
    categories = graphene.List(graphene.String)
    node_uuids = graphene.List(graphene.String)


class RapidProFlowRun(graphene.ObjectType):
    active = graphene.Int()
    completed = graphene.Int()
    interrupted = graphene.Int()
    expired = graphene.Int()


class RapidProFlow(graphene.ObjectType):
    id = graphene.String()
    name = graphene.String()
    type = graphene.String()
    archived = graphene.Boolean()
    labels = graphene.List(graphene.String)
    expires = graphene.Int()
    runs = graphene.List(RapidProFlowRun)
    results = graphene.List(RapidProFlowResult)
    # parent_refs
    created_on = graphene.DateTime()
    modified_on = graphene.DateTime()

    def resolve_id(parent, info):
        return parent["uuid"]


class PaymentRecordNode(BaseNodePermissionMixin, DjangoObjectType):
    permission_classes = (hopePermissionClass(Permissions.PROGRAMME_VIEW_PAYMENT_RECORD_DETAILS),)

    class Meta:
        model = PaymentRecord
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection


class ServiceProviderNode(DjangoObjectType):
    class Meta:
        model = ServiceProvider
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection


class AgeFilterObject(graphene.ObjectType):
    min = graphene.Int()
    max = graphene.Int()


class CashPlanPaymentVerificationNode(DjangoObjectType):
    excluded_admin_areas_filter = graphene.List(graphene.String)
    age_filter = graphene.Field(AgeFilterObject)
    xlsx_file_was_downloaded = graphene.Boolean()
    has_xlsx_file = graphene.Boolean()

    class Meta:
        model = CashPlanPaymentVerification
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection

    def resolve_xlsx_file_was_downloaded(self, info):
        return self.xlsx_cash_plan_payment_verification_file_was_downloaded

    def resolve_has_xlsx_file(self, info):
        return self.has_xlsx_cash_plan_payment_verification_file


class PaymentVerificationNode(BaseNodePermissionMixin, DjangoObjectType):
    permission_classes = (hopePermissionClass(Permissions.PAYMENT_VERIFICATION_VIEW_PAYMENT_RECORD_DETAILS),)
    is_manually_editable = graphene.Boolean()

    class Meta:
        model = PaymentVerification
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection


class CashPlanPaymentVerificationSummaryNode(DjangoObjectType):
    class Meta:
        model = CashPlanPaymentVerificationSummary
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection


class GetCashplanVerificationSampleSizeObject(graphene.ObjectType):
    payment_record_count = graphene.Int()
    sample_size = graphene.Int()


class PaymentVerificationLogEntryNode(LogEntryNode):
    content_object = graphene.Field(CashPlanPaymentVerificationNode)

    class Meta:
        model = LogEntry
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection


class Query(graphene.ObjectType):
    payment_record = relay.Node.Field(PaymentRecordNode)
    payment_record_verification = relay.Node.Field(PaymentVerificationNode)
    cash_plan_payment_verification = relay.Node.Field(CashPlanPaymentVerificationNode)
    all_payment_records = DjangoPermissionFilterConnectionField(
        PaymentRecordNode,
        filterset_class=PaymentRecordFilter,
        permission_classes=(hopePermissionClass(Permissions.PRORGRAMME_VIEW_LIST_AND_DETAILS),),
    )
    all_payment_verifications = DjangoPermissionFilterConnectionField(
        PaymentVerificationNode,
        filterset_class=PaymentVerificationFilter,
        permission_classes=(hopePermissionClass(Permissions.PAYMENT_VERIFICATION_VIEW_DETAILS),),
    )
    all_cash_plan_payment_verification = DjangoPermissionFilterConnectionField(
        CashPlanPaymentVerificationNode,
        filterset_class=CashPlanPaymentVerificationFilter,
        permission_classes=(hopePermissionClass(Permissions.PAYMENT_VERIFICATION_VIEW_DETAILS),),
    )

    payment_record_status_choices = graphene.List(ChoiceObject)
    payment_record_entitlement_card_status_choices = graphene.List(ChoiceObject)
    payment_record_delivery_type_choices = graphene.List(ChoiceObject)
    cash_plan_verification_status_choices = graphene.List(ChoiceObject)
    cash_plan_verification_sampling_choices = graphene.List(ChoiceObject)
    cash_plan_verification_verification_channel_choices = graphene.List(ChoiceObject)
    payment_verification_status_choices = graphene.List(ChoiceObject)

    all_rapid_pro_flows = graphene.List(
        RapidProFlow,
        business_area_slug=graphene.String(required=True),
    )
    sample_size = graphene.Field(
        GetCashplanVerificationSampleSizeObject,
        input=GetCashplanVerificationSampleSizeInput(),
    )

    all_payment_verification_log_entries = DjangoPermissionFilterConnectionField(
        PaymentVerificationLogEntryNode,
        filterset_class=PaymentVerificationLogEntryFilter,
        permission_classes=(hopePermissionClass(Permissions.ACTIVITY_LOG_VIEW),),
    )

    def resolve_all_payment_verifications(self, info, **kwargs):
        return (
            PaymentVerification.objects.filter(
                Q(cash_plan_payment_verification__status=CashPlanPaymentVerification.STATUS_ACTIVE)
                | Q(cash_plan_payment_verification__status=CashPlanPaymentVerification.STATUS_FINISHED)
            )
            .annotate(
                payment_record__household__status=Case(
                    When(payment_record__household__withdrawn=True, then=Value(STATUS_INACTIVE)),
                    default=Value(STATUS_ACTIVE),
                    output_field=CharField(),
                ),
            )
            .distinct()
        )

    def resolve_sample_size(self, info, input, **kwargs):
        def get_payment_records(cash_plan, payment_verification_plan, verification_channel):
            if verification_channel == CashPlanPaymentVerification.VERIFICATION_CHANNEL_RAPIDPRO:
                return cash_plan.available_payment_records(
                    payment_verification_plan=payment_verification_plan,
                    extra_validation=does_payment_record_have_right_hoh_phone_number,
                )
            return cash_plan.available_payment_records(payment_verification_plan=payment_verification_plan)

        cash_plan_id = decode_id_string(input.get("cash_plan_id"))
        cash_plan = get_object_or_404(CashPlan, id=cash_plan_id)

        payment_verification_plan = None
        if payment_verification_plan_id := decode_id_string(input.get("cash_plan_payment_verification_id")):
            payment_verification_plan = get_object_or_404(CashPlanPaymentVerification, id=payment_verification_plan_id)

        payment_records = get_payment_records(cash_plan, payment_verification_plan, input.get("verification_channel"))
        if not payment_records:
            return {
                "sample_size": 0,
                "payment_record_count": 0,
            }

        sampling = Sampling(input, cash_plan, payment_records)
        payment_record_count, payment_records_sample_count = sampling.generate_sampling()

        return {
            "payment_record_count": payment_record_count,
            "sample_size": payment_records_sample_count,
        }

    def resolve_all_rapid_pro_flows(self, info, business_area_slug, **kwargs):
        api = RapidProAPI(business_area_slug)
        return api.get_flows()

    def resolve_payment_record_status_choices(self, info, **kwargs):
        return to_choice_object(PaymentRecord.STATUS_CHOICE)

    def resolve_payment_record_entitlement_card_status_choices(self, info, **kwargs):
        return to_choice_object(PaymentRecord.ENTITLEMENT_CARD_STATUS_CHOICE)

    def resolve_payment_record_delivery_type_choices(self, info, **kwargs):
        return to_choice_object(PaymentRecord.DELIVERY_TYPE_CHOICE)

    def resolve_cash_plan_verification_status_choices(self, info, **kwargs):
        return to_choice_object(CashPlanPaymentVerification.STATUS_CHOICES)

    def resolve_cash_plan_verification_sampling_choices(self, info, **kwargs):
        return to_choice_object(CashPlanPaymentVerification.SAMPLING_CHOICES)

    def resolve_cash_plan_verification_verification_channel_choices(self, info, **kwargs):
        return to_choice_object(CashPlanPaymentVerification.VERIFICATION_CHANNEL_CHOICES)

    def resolve_payment_verification_status_choices(self, info, **kwargs):
        return to_choice_object(PaymentVerification.STATUS_CHOICES)
