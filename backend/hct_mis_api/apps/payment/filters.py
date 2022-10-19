from django.db.models import Q
from django.db.models.functions import Lower

from django_filters import CharFilter, FilterSet, OrderingFilter, UUIDFilter

from hct_mis_api.apps.activity_log.schema import LogEntryFilter
from hct_mis_api.apps.core.utils import CustomOrderingFilter, is_valid_uuid
from hct_mis_api.apps.household.models import ROLE_NO_ROLE
from hct_mis_api.apps.payment.models import (
    CashPlanPaymentVerification,
    PaymentRecord,
    PaymentVerification,
)
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
    verification_channel = CharFilter(field_name="cash_plan_payment_verification__verification_channel")

    class Meta:
        fields = ("cash_plan_payment_verification", "cash_plan_payment_verification__cash_plan", "status")
        model = PaymentVerification

    order_by = OrderingFilter(
        fields=(
            "payment_record__ca_id",
            "cash_plan_payment_verification__verification_channel",
            "cash_plan_payment_verification__unicef_id",
            "status",
            "payment_record__head_of_household__family_name",
            "payment_record__household__unicef_id",
            "payment_record__household__status",
            "payment_record__delivered_quantity",
            "received_amount",
            "payment_record__head_of_household__phone_no",
            "payment_record__head_of_household__phone_no_alternative",
        )
    )

    def search_filter(self, qs, name, value):
        values = value.split(" ")
        q_obj = Q()
        for value in values:
            q_obj |= Q(payment_record__ca_id__istartswith=value)
            q_obj |= Q(cash_plan_payment_verification__unicef_id__istartswith=value)
            q_obj |= Q(received_amount__istartswith=value)
            q_obj |= Q(payment_record__household__unicef_id__istartswith=value)
            q_obj |= Q(payment_record__head_of_household__full_name__istartswith=value)
            q_obj |= Q(payment_record__head_of_household__given_name__istartswith=value)
            q_obj |= Q(payment_record__head_of_household__middle_name__istartswith=value)
            q_obj |= Q(payment_record__head_of_household__family_name__istartswith=value)
            q_obj |= Q(payment_record__head_of_household__phone_no__istartswith=value)
            q_obj |= Q(payment_record__head_of_household__phone_no_alternative__istartswith=value)
        return qs.filter(q_obj)


class CashPlanPaymentVerificationFilter(FilterSet):
    class Meta:
        fields = tuple()
        model = CashPlanPaymentVerification


class PaymentVerificationLogEntryFilter(LogEntryFilter):
    object_id = UUIDFilter(method="object_id_filter")

    def object_id_filter(self, qs, name, value):
        cash_plan = CashPlan.objects.get(pk=value)
        verifications_ids = cash_plan.verifications.all().values_list("pk", flat=True)
        return qs.filter(object_id__in=verifications_ids)
