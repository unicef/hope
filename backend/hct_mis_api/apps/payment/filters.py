from base64 import b64decode

from django.db.models import Case, CharField, Count, Q, Value, When
from django.db.models.functions import Lower
from django.shortcuts import get_object_or_404

from django_filters import (
    CharFilter,
    DateFilter,
    FilterSet,
    MultipleChoiceFilter,
    NumberFilter,
    OrderingFilter,
    UUIDFilter,
)

from hct_mis_api.apps.activity_log.schema import LogEntryFilter
from hct_mis_api.apps.core.utils import (
    CustomOrderingFilter,
    decode_id_string,
    is_valid_uuid,
)
from hct_mis_api.apps.core.querysets import ExtendedQuerySetSequence
from hct_mis_api.apps.household.models import ROLE_NO_ROLE
from hct_mis_api.apps.payment.models import (
    CashPlan,
    FinancialServiceProvider,
    FinancialServiceProviderXlsxReport,
    FinancialServiceProviderXlsxTemplate,
    GenericPayment,
    Payment,
    PaymentPlan,
    PaymentRecord,
    PaymentVerification,
    PaymentVerificationPlan,
    PaymentVerificationSummary,
)
from hct_mis_api.apps.program.models import Program


class PaymentRecordFilter(FilterSet):
    individual = CharFilter(method="individual_filter")
    business_area = CharFilter(field_name="business_area__slug")

    class Meta:
        fields = (
            "parent",
            "household",
        )
        model = PaymentRecord

    order_by = CustomOrderingFilter(
        fields=(
            "ca_id",
            "status",
            Lower("name"),
            "status_date",
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
    payment_plan_id = CharFilter(method="payment_plan_filter")
    search = CharFilter(method="search_filter")
    business_area = CharFilter(field_name="payment__business_area__slug", required=True)
    verification_channel = CharFilter(field_name="payment_verification_plan__verification_channel")

    class Meta:
        fields = ("payment_verification_plan", "status")
        model = PaymentVerification

    order_by = OrderingFilter(
        fields=(
            "payment__ca_id",
            "payment_verification_plan__verification_channel",
            "payment_verification_plan__unicef_id",
            "status",
            "received_amount",
            "payment__head_of_household__family_name",
            "payment__household__unicef_id",
            "payment__household__status",
            "payment__delivered_quantity",
            "payment__head_of_household__phone_no",
            "payment__head_of_household__phone_no_alternative",
        )
    )

    def search_filter(self, qs, name, value):
        # TODO: fix filter; ''payment_record' and 'payment''
        # payment_plan_id
        values = value.split(" ")
        q_obj = Q()
        for value in values:
            q_obj |= Q(payment__ca_id__istartswith=value)
            q_obj |= Q(payment_verification_plan__unicef_id__istartswith=value)
            q_obj |= Q(received__istartswith=value)
            q_obj |= Q(payment__household__unicef_id__istartswith=value)
            q_obj |= Q(payment__head_of_household__full_name__istartswith=value)
            q_obj |= Q(payment__head_of_household__given_name__istartswith=value)
            q_obj |= Q(payment__head_of_household__middle_name__istartswith=value)
            q_obj |= Q(payment__head_of_household__family_name__istartswith=value)
            q_obj |= Q(payment__head_of_household__phone_no__istartswith=value)
            q_obj |= Q(payment__head_of_household__phone_no_alternative__istartswith=value)
        return qs.filter(q_obj)

    def payment_plan_filter(self, qs, name, value):
        node_name, obj_id = b64decode(value).decode().split(":")
        key =(
            "payment_verification_plan__cash_plan__id" if node_name == "CashPlanNode" else
            "payment_verification_plan__payment_plan__id"
        )
        return qs.filter(**{key: obj_id})


class PaymentVerificationPlanFilter(FilterSet):
    class Meta:
        fields = tuple()
        model = PaymentVerificationPlan


class PaymentVerificationSummaryFilter(FilterSet):
    class Meta:
        fields = tuple()
        model = PaymentVerificationSummary


class PaymentVerificationLogEntryFilter(LogEntryFilter):
    object_id = UUIDFilter(method="object_id_filter")

    def object_id_filter(self, qs, name, value):
        cash_plan = CashPlan.objects.get(pk=value)
        verifications_ids = cash_plan.payment_verification_plan.all().values_list("pk", flat=True)
        return qs.filter(object_id__in=verifications_ids)


class FinancialServiceProviderXlsxTemplateFilter(FilterSet):
    class Meta:
        fields = (
            "name",
            "created_by",
        )
        model = FinancialServiceProviderXlsxTemplate

    order_by = CustomOrderingFilter(
        fields=(
            Lower("name"),
            "created_by",
        )
    )


class FinancialServiceProviderXlsxReportFilter(FilterSet):
    class Meta:
        fields = ("status",)
        model = FinancialServiceProviderXlsxReport

    order_by = CustomOrderingFilter(fields=("status",))


class FinancialServiceProviderFilter(FilterSet):
    delivery_mechanisms = MultipleChoiceFilter(
        field_name="delivery_mechanisms", choices=GenericPayment.DELIVERY_TYPE_CHOICE
    )

    class Meta:
        fields = (
            "created_by",
            "name",
            "vision_vendor_number",
            "delivery_mechanisms",
            "distribution_limit",
            "communication_channel",
            "fsp_xlsx_template",
        )
        model = FinancialServiceProvider

    order_by = CustomOrderingFilter(
        fields=(
            "id",
            Lower("name"),
            "vision_vendor_number",
            "delivery_mechanisms",
            "distribution_limit",
            "communication_channel",
        )
    )


class CashPlanFilter(FilterSet):
    search = CharFilter(method="search_filter")
    delivery_type = MultipleChoiceFilter(field_name="delivery_type", choices=PaymentRecord.DELIVERY_TYPE_CHOICE)
    verification_status = MultipleChoiceFilter(
        field_name="payment_verification_summary__status", choices=PaymentVerificationPlan.STATUS_CHOICES
    )
    business_area = CharFilter(
        field_name="business_area__slug",
    )

    class Meta:
        fields = {
            "program": ["exact"],
            "assistance_through": ["exact", "startswith"],
            "service_provider__full_name": ["exact", "startswith"],
            "start_date": ["exact", "lte", "gte"],
            "end_date": ["exact", "lte", "gte"],
            "business_area": ["exact"],
        }
        model = CashPlan

    order_by = OrderingFilter(
        fields=(
            "ca_id",
            "status",
            "total_number_of_hh",
            "total_entitled_quantity",
            ("payment_verification_summary__status", "verification_status"),
            "total_persons_covered",
            "total_delivered_quantity",
            "total_undelivered_quantity",
            "dispersion_date",
            "assistance_measurement",
            "assistance_through",
            "delivery_type",
            "start_date",
            "end_date",
            "program__name",
            "id",
            "updated_at",
            "service_provider__full_name",
        )
    )

    def filter_queryset(self, queryset):
        queryset = queryset.annotate(total_number_of_hh=Count("payment_items"))
        return super().filter_queryset(queryset)

    def search_filter(self, qs, name, value):
        values = value.split(" ")
        q_obj = Q()
        for value in values:
            q_obj |= Q(ca_id__istartswith=value)
        return qs.filter(q_obj)


class PaymentPlanFilter(FilterSet):
    business_area = CharFilter(field_name="business_area__slug", required=True)
    search = CharFilter(method="search_filter")
    status = MultipleChoiceFilter(field_name="status", choices=PaymentPlan.Status.choices)
    total_entitled_quantity_from = NumberFilter(field_name="total_entitled_quantity", lookup_expr="gte")
    total_entitled_quantity_to = NumberFilter(field_name="total_entitled_quantity", lookup_expr="lte")
    dispersion_start_date = DateFilter(field_name="dispersion_start_date", lookup_expr="gte")
    dispersion_end_date = DateFilter(field_name="dispersion_end_date", lookup_expr="lte")

    class Meta:
        fields = tuple()
        model = PaymentPlan

    def filter_queryset(self, queryset):
        queryset = queryset.annotate(total_number_of_hh=Count("payment_items"))
        if not self.form.cleaned_data.get("order_by"):
            queryset = queryset.order_by("unicef_id")
        return super().filter_queryset(queryset)

    order_by = OrderingFilter(
        fields=(
            "unicef_id",
            "status",
            "total_households_count",
            "currency",
            "total_entitled_quantity",
            "total_delivered_quantity",
            "total_undelivered_quantity",
            "dispersion_start_date",
            "dispersion_end_date",
            "created_at",
        )
    )

    def search_filter(self, qs, name, value):
        return qs.filter(Q(id__icontains=value) | Q(unicef_id__icontains=value))


class PaymentFilter(FilterSet):
    business_area = CharFilter(field_name="parent__business_area__slug", required=True)
    payment_plan_id = CharFilter(required=True, method="payment_plan_id_filter")

    def payment_plan_id_filter(self, qs, name, value):
        payment_plan_id = decode_id_string(value)
        payment_plan = get_object_or_404(PaymentPlan, id=payment_plan_id)
        q = Q(parent=payment_plan)
        if payment_plan.status != PaymentPlan.Status.OPEN:
            q &= ~Q(excluded=True)
        return qs.filter(q)

    class Meta:
        fields = tuple()
        model = Payment

    order_by = OrderingFilter(
        fields=(
            "unicef_id",
            "status",
            "household_id",
            "household__size",
            "admin2",
            "collector_id",
            "assigned_payment_channel",
            "entitlement_quantity_usd",
            "delivered_quantity",
            "financial_service_provider__name",
        )
    )

    def filter_queryset(self, queryset):
        # household__admin2
        queryset = queryset.annotate(
            admin2=Case(
                When(
                    household__admin_area__isnull=True,
                    then=Value(""),
                ),
                When(
                    household__admin_area__isnull=False,
                    household__admin_area__area_type__area_level__in=(0, 1),
                    then=Value(""),
                ),
                When(
                    household__admin_area__isnull=False,
                    household__admin_area__area_type__area_level__lt=2,
                    household__admin_area__area_type__area_level__gt=2,
                    then=Lower("household__admin_area__parent__name"),
                ),
                When(
                    household__admin_area__isnull=False,
                    then=Lower("household__admin_area__name"),
                ),
                default=Value(""),
                output_field=CharField(),
            )
        ).select_related("financial_service_provider")
        if not self.form.cleaned_data.get("order_by"):
            queryset = queryset.order_by("unicef_id")

        return super().filter_queryset(queryset)


def cash_plan_and_payment_plan_filter(queryset: ExtendedQuerySetSequence, **kwargs) -> ExtendedQuerySetSequence:
    business_area = kwargs.get("business_area")
    program = kwargs.get("program")
    service_provider = kwargs.get("service_provider")
    delivery_type = kwargs.get("delivery_type")
    verification_status = kwargs.get("verification_status")
    start_date_gte, end_date_lte = kwargs.get("start_date_gte"), kwargs.get("end_date_lte")
    search = kwargs.get("search")

    if business_area:
        queryset = queryset.filter(business_area__slug=business_area)

    if program:
        program_obj = get_object_or_404(Program, id=decode_id_string(program))
        queryset = queryset.filter(program=program_obj)

    if start_date_gte:
        queryset = queryset.filter(start_date__gte=start_date_gte)
    if end_date_lte:
        queryset = queryset.filter(end_date__lte=end_date_lte)

    if verification_status:
        queryset = queryset.filter(payment_verification_summary__status__in=verification_status)

    # TODO: add filters below
    if service_provider:
        pass
    if delivery_type:
        # ["delivery_type",] PaymentRecord.DELIVERY_TYPE_CHOICE
        pass

    if search:
        pass

    return queryset


def cash_plan_and_payment_plan_ordering(queryset: ExtendedQuerySetSequence, order_by) -> ExtendedQuerySetSequence:
    reverse = "-" if order_by.startswith("-") else ""
    order_by = order_by[1:] if reverse else order_by

    if order_by == "verification_status":
        queryset = queryset.order_by(reverse + "custom_order")

    elif order_by == "unicef_id":
        queryset = sorted(queryset, key=lambda o: o.get_unicef_id, reverse=bool(reverse))
    else:
        queryset = queryset.order_by(reverse + order_by)

    return queryset
