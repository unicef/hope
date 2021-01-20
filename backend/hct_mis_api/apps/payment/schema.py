import graphene
from django.db.models import Q, Sum
from django.db.models.functions import Lower
from django.shortcuts import get_object_or_404
from django_filters import CharFilter, FilterSet, OrderingFilter
from graphene import relay
from graphene_django import DjangoObjectType

from hct_mis_api.apps.account.permissions import (
    DjangoPermissionFilterConnectionField,
    Permissions,
    hopePermissionClass,
    BaseNodePermissionMixin,
)
from hct_mis_api.apps.core.extended_connection import ExtendedConnection
from hct_mis_api.apps.core.filters import filter_age
from hct_mis_api.apps.core.schema import ChoiceObject
from hct_mis_api.apps.utils.schema import ChartDatasetNode, ChartDetailedDatasetsNode
from hct_mis_api.apps.core.utils import to_choice_object, decode_id_string, is_valid_uuid, CustomOrderingFilter, chart_map_choices, chart_get_filtered_qs
from hct_mis_api.apps.household.models import ROLE_NO_ROLE
from hct_mis_api.apps.payment.inputs import GetCashplanVerificationSampleSizeInput
from hct_mis_api.apps.payment.models import CashPlanPaymentVerification, PaymentRecord, PaymentVerification, ServiceProvider
from hct_mis_api.apps.payment.rapid_pro.api import RapidProAPI
from hct_mis_api.apps.payment.utils import get_number_of_samples
from hct_mis_api.apps.program.models import CashPlan


class PaymentRecordFilter(FilterSet):
    individual = CharFilter(method="individual_filter")
    business_area = CharFilter(field_name="business_area__slug")

    class Meta:
        fields = (
            "cash_plan",
            "household",
        )
        model = PaymentRecord

    order_by = CustomOrderingFilter(
        fields=(
            "status",
            Lower("name"),
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

    def individual_filter(self, qs, name, value):
        if is_valid_uuid(value):
            return qs.exclude(household__individuals_and_roles__role=ROLE_NO_ROLE)
        return qs


class PaymentVerificationFilter(FilterSet):
    search = CharFilter(method="search_filter")
    business_area = CharFilter(field_name="payment_record__business_area__slug")

    class Meta:
        fields = ("cash_plan_payment_verification", "status")
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
            "received_amount",
        )
    )

    def search_filter(self, qs, name, value):
        values = value.split(" ")
        q_obj = Q()
        for value in values:
            q_obj |= Q(id__icontains=value)
            q_obj |= Q(received_amount__icontains=value)
            q_obj |= Q(payment_record__id__icontains=value)
            q_obj |= Q(payment_record__household__head_of_household__full_name__icontains=value)
        return qs.filter(q_obj)


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
        filter_fields = ["cash_plan", "household"]
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

    class Meta:
        model = CashPlanPaymentVerification
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection


class PaymentVerificationNode(BaseNodePermissionMixin, DjangoObjectType):
    permission_classes = (hopePermissionClass(Permissions.PAYMENT_VERIFICATION_VIEW_PAYMENT_RECORD_DETAILS),)

    class Meta:
        model = PaymentVerification
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection


class GetCashplanVerificationSampleSizeObject(graphene.ObjectType):
    payment_record_count = graphene.Int()
    sample_size = graphene.Int()


class ChartPaymentVerification(ChartDetailedDatasetsNode):
    households = graphene.Int()


class Query(graphene.ObjectType):
    payment_record = relay.Node.Field(PaymentRecordNode)
    payment_record_verification = relay.Node.Field(PaymentVerificationNode)
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

    chart_payment_verifications_status = graphene.Field(
        ChartPaymentVerification,
        business_area_slug=graphene.String(required=True),
        year=graphene.Int(required=True)
    )
    chart_payment_record_delivery_type = graphene.Field(
        ChartDatasetNode,
        business_area_slug=graphene.String(required=True),
        year=graphene.Int(required=True)
    )
    chart_payment_record_status = graphene.Field(
        ChartDatasetNode,
        business_area_slug=graphene.String(required=True),
        year=graphene.Int(required=True)
    )

    payment_record_status_choices = graphene.List(ChoiceObject)
    payment_record_entitlement_card_status_choices = graphene.List(ChoiceObject)
    payment_record_delivery_type_choices = graphene.List(ChoiceObject)
    cash_plan_verification_status_choices = graphene.List(ChoiceObject)
    cash_plan_verification_sampling_choices = graphene.List(ChoiceObject)
    cash_plan_verification_verification_method_choices = graphene.List(ChoiceObject)
    payment_verification_status_choices = graphene.List(ChoiceObject)

    all_rapid_pro_flows = graphene.List(
        RapidProFlow,
        business_area_slug=graphene.String(required=True),
    )
    sample_size = graphene.Field(
        GetCashplanVerificationSampleSizeObject,
        input=GetCashplanVerificationSampleSizeInput(),
    )

    def resolve_sample_size(self, info, input, **kwargs):
        arg = lambda name: input.get(name)
        cash_plan_id = decode_id_string(arg("cash_plan_id"))
        cash_plan = get_object_or_404(CashPlan, id=cash_plan_id)
        sampling = arg("sampling")
        excluded_admin_areas = []
        sex = None
        age = None
        confidence_interval = None
        margin_of_error = None
        payment_records = cash_plan.payment_records.filter(
            status=PaymentRecord.STATUS_SUCCESS, delivered_quantity__gt=0
        )
        payment_record_count = payment_records.count()
        if sampling == CashPlanPaymentVerification.SAMPLING_FULL_LIST:
            excluded_admin_areas = arg("full_list_arguments").get("excluded_admin_areas", [])
        elif sampling == CashPlanPaymentVerification.SAMPLING_RANDOM:
            random_sampling_arguments = arg("random_sampling_arguments")
            confidence_interval = random_sampling_arguments.get("confidence_interval")
            margin_of_error = random_sampling_arguments.get("margin_of_error")
            sex = random_sampling_arguments.get("sex")
            age = random_sampling_arguments.get("random_sampling_arguments")
        if excluded_admin_areas is not None:
            payment_records = payment_records.filter(~(Q(household__admin_area__title__in=excluded_admin_areas)))
        if sex is not None:
            payment_records = payment_records.filter(household__head_of_household__sex=sex)
        if age is not None:
            payment_records = filter_age(
                "household__head_of_household__birth_date",
                payment_records,
                age.get(min),
                age.get("max"),
            )
        payment_records_sample_count = payment_records.count()
        if sampling == CashPlanPaymentVerification.SAMPLING_RANDOM:
            payment_records_sample_count = get_number_of_samples(
                payment_records_sample_count,
                confidence_interval,
                margin_of_error,
            )
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

    def resolve_cash_plan_verification_verification_method_choices(self, info, **kwargs):
        return to_choice_object(CashPlanPaymentVerification.VERIFICATION_METHOD_CHOICES)

    def resolve_payment_verification_status_choices(self, info, **kwargs):
        return to_choice_object(PaymentVerification.STATUS_CHOICES)

    def resolve_chart_payment_verifications_status(self, info, business_area_slug, year, **kwargs):
        status_choices = PaymentVerification.STATUS_CHOICES
        status_choices_mapping = dict(status_choices)
        payment_verifications = PaymentVerification.objects.filter(
            payment_record__business_area__slug=business_area_slug,
            created_at__year=year
        )

        dataset = [payment_verifications.filter(status=status).count() for status in status_choices_mapping.keys()]
        dataset_percentage = [data / sum(dataset) for data in dataset]
        dataset_percentage_done = [
            {
                "label": status,
                "data": [dataset_percentage_value]
            }
            for (dataset_percentage_value, status) in zip(dataset_percentage, status_choices_mapping.values())
        ]
        return {
            "labels": ["Payment Verification"],
            "datasets": dataset_percentage_done,
            "households": payment_verifications.values('payment_record__household').count()
        }

    def resolve_chart_payment_record_delivery_type(self, info, business_area_slug, year, **kwargs):
        delivery_type_choices = PaymentRecord.DELIVERY_TYPE_CHOICE
        delivery_type_choices_mapping = dict(delivery_type_choices)
        payment_records = PaymentRecord.objects.filter(
            business_area__slug=business_area_slug,
            created_at__year=year
        )
        dataset = [
            {
                "data": [
                    payment_records.filter(
                        delivery_type=delivery_type
                    ).aggregate(Sum('delivered_quantity'))['delivered_quantity__sum']
                    for delivery_type in delivery_type_choices_mapping.keys()
                ]
            }
        ]
        return {"labels": delivery_type_choices_mapping.values(), "datasets": dataset}

    def resolve_chart_payment_record_status(self, info, business_area_slug, year, **kwargs):
        status_choices_mapping = chart_map_choices(PaymentRecord.STATUS_CHOICE)
        payment_records = chart_get_filtered_qs(PaymentRecord, business_area_slug, year)
        dataset = [
            {
                "data": [
                    payment_records.filter(status=status).count()
                    for status in status_choices_mapping.keys()]
            }
        ]
        return {"labels": status_choices_mapping.values(), "datasets": dataset}