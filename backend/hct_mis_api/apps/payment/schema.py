import graphene
from django.db.models import Q, Sum, Count
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
from hct_mis_api.apps.core.models import AdminArea
from hct_mis_api.apps.core.schema import ChoiceObject
from hct_mis_api.apps.core.utils import (
    to_choice_object,
    decode_id_string,
    is_valid_uuid,
    CustomOrderingFilter,
    chart_map_choices,
    chart_get_filtered_qs,
    chart_permission_decorator,
    chart_filters_decoder,
    chart_create_filter_query,
)
from hct_mis_api.apps.household.models import ROLE_NO_ROLE
from hct_mis_api.apps.payment.inputs import GetCashplanVerificationSampleSizeInput
from hct_mis_api.apps.payment.models import (
    CashPlanPaymentVerification,
    PaymentRecord,
    PaymentVerification,
    ServiceProvider,
)
from hct_mis_api.apps.payment.rapid_pro.api import RapidProAPI
from hct_mis_api.apps.payment.utils import get_number_of_samples, get_payment_records_for_dashboard
from hct_mis_api.apps.program.models import CashPlan
from hct_mis_api.apps.utils.schema import (
    ChartDatasetNode,
    ChartDetailedDatasetsNode,
    SectionTotalNode,
    TableTotalCashTransferred,
)


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
            "ca_id",
            "status",
            Lower("name"),
            "status_date",
            "cash_assist_id",
            Lower("head_of_household__full_name"),
            "total_person_covered",
            "distribution_modality",
            "household__unicef_id",
            "household__size",
            "entitlement_quantity",
            "delivered_quantity_usd",
            "delivery_date",
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
            q_obj |= Q(id__startswith=value)
            q_obj |= Q(received_amount__startswith=value)
            q_obj |= Q(payment_record__id__startswith=value)
            q_obj |= Q(payment_record__household__head_of_household__full_name__startswith=value)
            q_obj |= Q(payment_record__household__head_of_household__given_name__startswith=value)
            q_obj |= Q(payment_record__household__head_of_household__middle_name__startswith=value)
            q_obj |= Q(payment_record__household__head_of_household__family_name__startswith=value)
        return qs.filter(q_obj)


class CashPlanPaymentVerificationFilter(FilterSet):
    class Meta:
        fields = tuple()
        model = CashPlanPaymentVerification


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
    is_manually_editable = graphene.Boolean()

    class Meta:
        model = PaymentVerification
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection


class GetCashplanVerificationSampleSizeObject(graphene.ObjectType):
    payment_record_count = graphene.Int()
    sample_size = graphene.Int()


class ChartPaymentVerification(ChartDetailedDatasetsNode):
    households = graphene.Int()
    average_sample_size = graphene.Float()


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

    chart_payment_verification = graphene.Field(
        ChartPaymentVerification,
        business_area_slug=graphene.String(required=True),
        year=graphene.Int(required=True),
        program=graphene.String(required=False),
        administrative_area=graphene.String(required=False),
    )
    chart_volume_by_delivery_mechanism = graphene.Field(
        ChartDatasetNode,
        business_area_slug=graphene.String(required=True),
        year=graphene.Int(required=True),
        program=graphene.String(required=False),
        administrative_area=graphene.String(required=False),
    )
    chart_payment = graphene.Field(
        ChartDatasetNode,
        business_area_slug=graphene.String(required=True),
        year=graphene.Int(required=True),
        program=graphene.String(required=False),
        administrative_area=graphene.String(required=False),
    )
    section_total_transferred = graphene.Field(
        SectionTotalNode,
        business_area_slug=graphene.String(required=True),
        year=graphene.Int(required=True),
        program=graphene.String(required=False),
        administrative_area=graphene.String(required=False),
    )
    table_total_cash_transferred_by_administrative_area = graphene.Field(
        TableTotalCashTransferred,
        business_area_slug=graphene.String(required=True),
        year=graphene.Int(required=True),
        program=graphene.String(required=False),
        administrative_area=graphene.String(required=False),
        order=graphene.String(required=False),
        order_by=graphene.String(required=False),
    )
    chart_total_transferred_cash_by_country = graphene.Field(
        ChartDetailedDatasetsNode, year=graphene.Int(required=True)
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
            age = random_sampling_arguments.get("age")
        if excluded_admin_areas is not None:
            payment_records = payment_records.filter(~(Q(household__admin_area__title__in=excluded_admin_areas)))
        if sex is not None:
            payment_records = payment_records.filter(household__head_of_household__sex=sex)
        if age is not None:
            payment_records = filter_age(
                "household__head_of_household__birth_date",
                payment_records,
                age.get("min"),
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

    @chart_permission_decorator(permissions=[Permissions.DASHBOARD_VIEW_COUNTRY])
    def resolve_chart_payment_verification(self, info, business_area_slug, year, **kwargs):
        filters = chart_filters_decoder(kwargs)
        status_choices_mapping = chart_map_choices(PaymentVerification.STATUS_CHOICES)
        payment_verifications = chart_get_filtered_qs(
            PaymentVerification,
            year,
            business_area_slug_filter={"payment_record__business_area__slug": business_area_slug},
            additional_filters={
                **chart_create_filter_query(
                    filters,
                    program_id_path="payment_record__cash_plan__program__id",
                    administrative_area_path="payment_record__household__admin_area",
                )
            },
            year_filter_path="payment_record__delivery_date",
        )

        verifications_by_status = payment_verifications.values("status").annotate(count=Count("status"))
        verifications_by_status_dict = {x.get("status"): x.get("count") for x in verifications_by_status}
        dataset = [verifications_by_status_dict.get(status, 0) for status in status_choices_mapping.keys()]
        try:
            all_verifications = sum(dataset)
            dataset_percentage = [data / all_verifications for data in dataset]
        except ZeroDivisionError:
            dataset_percentage = [0] * len(status_choices_mapping.values())
        dataset_percentage_done = [
            {"label": status, "data": [dataset_percentage_value]}
            for (dataset_percentage_value, status) in zip(dataset_percentage, status_choices_mapping.values())
        ]

        samples_count = payment_verifications.distinct("payment_record").count()
        all_payment_records_for_created_verifications = (
            PaymentRecord.objects.filter(
                cash_plan__in=payment_verifications.distinct("cash_plan_payment_verification__cash_plan").values_list(
                    "cash_plan_payment_verification__cash_plan", flat=True
                )
            )
            .filter(status=PaymentRecord.STATUS_SUCCESS, delivered_quantity__gt=0)
            .count()
        )
        if samples_count == 0 or all_payment_records_for_created_verifications == 0:
            average_sample_size = 0
        else:
            average_sample_size = samples_count / all_payment_records_for_created_verifications
        return {
            "labels": ["Payment Verification"],
            "datasets": dataset_percentage_done,
            "households": payment_verifications.distinct("payment_record__household").count(),
            "average_sample_size": average_sample_size,
        }

    @chart_permission_decorator(permissions=[Permissions.DASHBOARD_VIEW_COUNTRY])
    def resolve_chart_volume_by_delivery_mechanism(self, info, business_area_slug, year, **kwargs):
        payment_records = get_payment_records_for_dashboard(
            year, business_area_slug, chart_filters_decoder(kwargs), True
        )
        volume_by_delivery_type = payment_records.values("delivery_type").annotate(volume=Sum("delivered_quantity_usd"))
        labels = []
        data = []
        for volume_dict in volume_by_delivery_type:
            if volume_dict.get("volume"):
                labels.append(volume_dict.get("delivery_type"))
                data.append(volume_dict.get("volume"))

        return {"labels": labels, "datasets": [{"data": data}]}

    @chart_permission_decorator(permissions=[Permissions.DASHBOARD_VIEW_COUNTRY])
    def resolve_chart_payment(self, info, business_area_slug, year, **kwargs):
        payment_records = get_payment_records_for_dashboard(
            year, business_area_slug, chart_filters_decoder(kwargs)
        ).aggregate(
            successful=Count("id", filter=~Q(status=PaymentRecord.STATUS_ERROR)),
            unsuccessful=Count("id", filter=Q(status=PaymentRecord.STATUS_ERROR)),
        )

        dataset = [
            {
                "data": [
                    payment_records.get("successful", 0),
                    payment_records.get("unsuccessful", 0),
                ]
            }
        ]
        return {"labels": ["Successful Payments", "Unsuccessful Payments"], "datasets": dataset}

    @chart_permission_decorator(permissions=[Permissions.DASHBOARD_VIEW_COUNTRY])
    def resolve_section_total_transferred(self, info, business_area_slug, year, **kwargs):
        payment_records = get_payment_records_for_dashboard(year, business_area_slug, chart_filters_decoder(kwargs))
        return {"total": payment_records.aggregate(Sum("delivered_quantity_usd"))["delivered_quantity_usd__sum"]}

    @chart_permission_decorator(permissions=[Permissions.DASHBOARD_VIEW_COUNTRY])
    def resolve_table_total_cash_transferred_by_administrative_area(self, info, business_area_slug, year, **kwargs):
        if business_area_slug == "global":
            return None
        order = kwargs.pop("order", None)
        order_by = kwargs.pop("order_by", None)
        payment_records = get_payment_records_for_dashboard(
            year, business_area_slug, chart_filters_decoder(kwargs), True
        )

        admin_areas = (
            AdminArea.objects.filter(
                level=2,
                household__payment_records__in=payment_records,
            )
            .distinct()
            .annotate(total_transferred=Sum("household__payment_records__delivered_quantity_usd"))
            .annotate(num_households=Count("household", distinct=True))
        )

        if order_by:
            order_by_arg = None
            if order_by == "admin2":
                order_by_arg = "title"
            elif order_by == "totalCashTransferred":
                order_by_arg = "total_transferred"
            elif order_by == "totalHouseholds":
                order_by_arg = "num_households"
            if order_by_arg:
                admin_areas = admin_areas.order_by(f"{'-' if order == 'desc' else ''}{order_by_arg}")

        data = [
            {
                "id": item.id,
                "admin2": item.title,
                "total_cash_transferred": item.total_transferred,
                "total_households": item.num_households,
            }
            for item in admin_areas
        ]
        return {"data": data}

    @chart_permission_decorator(permissions=[Permissions.DASHBOARD_VIEW_COUNTRY])
    def resolve_chart_total_transferred_cash_by_country(self, info, year, **kwargs):
        payment_records = get_payment_records_for_dashboard(year, "global", {}, True)

        countries_and_amounts = (
            payment_records.values("business_area__name")
            .order_by("business_area__name")
            .annotate(
                total_delivered_cash=Sum(
                    "delivered_quantity_usd", filter=Q(delivery_type__in=PaymentRecord.DELIVERY_TYPES_IN_CASH)
                )
            )
            .annotate(
                total_delivered_voucher=Sum(
                    "delivered_quantity_usd", filter=Q(delivery_type__in=PaymentRecord.DELIVERY_TYPES_IN_VOUCHER)
                )
            )
        )

        labels = []
        cash_transferred = []
        voucher_transferred = []
        total_transferred = []
        for data_dict in countries_and_amounts:
            labels.append(data_dict.get("business_area__name"))
            cash_transferred.append(data_dict.get("total_delivered_cash") or 0)
            voucher_transferred.append(data_dict.get("total_delivered_voucher") or 0)
            total_transferred.append(cash_transferred[-1] + voucher_transferred[-1])

        datasets = [
            {"label": "Actual cash transferred", "data": cash_transferred},
            {"label": "Actual voucher transferred", "data": voucher_transferred},
            {"label": "Total transferred", "data": total_transferred},
        ]

        return {"labels": labels, "datasets": datasets}
