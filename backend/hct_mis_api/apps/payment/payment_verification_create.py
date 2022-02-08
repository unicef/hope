from django.db.models import Q
from django.utils import timezone

from hct_mis_api.apps.core.filters import filter_age
from hct_mis_api.apps.core.utils import decode_id_string
from hct_mis_api.apps.payment.models import (
    CashPlanPaymentVerification,
    PaymentRecord,
    PaymentVerification,
)
from hct_mis_api.apps.payment.utils import get_number_of_samples


class PaymentVerificationVerifyArgument:
    ARGUMENTS = {
        "sampling": {
            CashPlanPaymentVerification.SAMPLING_FULL_LIST: {
                "required": ["full_list_arguments"],
                "not_allowed": ["random_sampling_arguments"],
            },
            CashPlanPaymentVerification.SAMPLING_RANDOM: {
                "required": ["random_sampling_arguments"],
                "not_allowed": ["full_list_arguments"],
            },
        },
        "verification_channel": {
            CashPlanPaymentVerification.VERIFICATION_METHOD_RAPIDPRO: {
                "required": ["rapid_pro_arguments"],
                "not_allowed": ["xlsx_arguments", "manual_arguments"],
            },
            CashPlanPaymentVerification.VERIFICATION_METHOD_XLSX: {
                "required": [],
                "not_allowed": ["rapid_pro_arguments", "manual_arguments"],
            },
            CashPlanPaymentVerification.VERIFICATION_METHOD_MANUAL: {
                "required": [],
                "not_allowed": ["rapid_pro_arguments", "xlsx_arguments"],
            },
        },
    }

    def __init__(self, input):
        self.input = input

    def verify(self, field_name):
        options = self.ARGUMENTS.get(field_name)

        for key, value in options.items():
            if key != self.input.get(field_name):
                continue
            for required in value.get("required"):
                if self.input.get(required) is None:
                    raise ValueError(f"You have to provide {required} in {key}")
            for not_allowed in value.get("not_allowed"):
                if self.input.get(not_allowed) is not None:
                    raise ValueError(f"You can't provide {not_allowed} in {key}")


class PaymentVerificationCreate:
    def __init__(self, input, cash_plan):
        self.input = input
        self.cash_plan = cash_plan

    def execute(self) -> CashPlanPaymentVerification:
        verifier = PaymentVerificationVerifyArgument(self.input)
        verifier.verify("sampling")
        verifier.verify("verification_channel")

        (
            payment_records,
            confidence_interval,
            margin_of_error,
            payment_records_sample_count,
            sampling,
            excluded_admin_areas,
            sex,
            age,
        ) = self.process_sampling()

        verification_channel = self.input.get("verification_channel")

        cash_plan_verification = CashPlanPaymentVerification(
            cash_plan=self.cash_plan,
            confidence_interval=confidence_interval,
            margin_of_error=margin_of_error,
            sample_size=payment_records_sample_count,
            sampling=sampling,
            verification_method=verification_channel,
        )
        cash_plan_verification.sex_filter = sex
        cash_plan_verification.age_filter = age
        cash_plan_verification.excluded_admin_areas_filter = excluded_admin_areas
        cash_plan_verification.save()

        payment_record_verifications_to_create = []
        for payment_record in payment_records:
            payment_record_verification = PaymentVerification(
                status_date=timezone.now(),
                cash_plan_payment_verification=cash_plan_verification,
                payment_record=payment_record,
            )
            payment_record_verifications_to_create.append(payment_record_verification)
        PaymentVerification.objects.bulk_create(payment_record_verifications_to_create)
        self.process_verification_method(cash_plan_verification)
        return cash_plan_verification

    def process_sampling(self):
        sampling = self.input.get("sampling")
        excluded_admin_areas = []
        sex = None
        age = None
        confidence_interval = None
        margin_of_error = None
        payment_records = self.cash_plan.payment_records.filter(
            status__in=PaymentRecord.ALLOW_CREATE_VERIFICATION, delivered_quantity__gt=0
        )
        if sampling == CashPlanPaymentVerification.SAMPLING_FULL_LIST:
            excluded_admin_areas = self.input.get("full_list_arguments").get("excluded_admin_areas", [])
        elif sampling == CashPlanPaymentVerification.SAMPLING_RANDOM:
            random_sampling_arguments = self.input.get("random_sampling_arguments")
            confidence_interval = random_sampling_arguments.get("confidence_interval")
            margin_of_error = random_sampling_arguments.get("margin_of_error")
            sex = random_sampling_arguments.get("sex")
            age = random_sampling_arguments.get("age")
            excluded_admin_areas = random_sampling_arguments.get("excluded_admin_areas", [])
        excluded_admin_areas_decoded = [decode_id_string(x) for x in excluded_admin_areas]

        payment_records = payment_records.filter(~(Q(household__admin_area__id__in=excluded_admin_areas_decoded)))
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
            payment_records = payment_records.order_by("?")[:payment_records_sample_count]
        return (
            payment_records,
            confidence_interval,
            margin_of_error,
            payment_records_sample_count,
            sampling,
            excluded_admin_areas,
            sex,
            age,
        )

    def process_verification_method(self, cash_plan_payment_verification: CashPlanPaymentVerification):
        verification_method = cash_plan_payment_verification.verification_method
        if verification_method == CashPlanPaymentVerification.VERIFICATION_METHOD_RAPIDPRO:
            flow_id = self.input["rapid_pro_arguments"]["flow_id"]
            cash_plan_payment_verification.rapid_pro_flow_id = flow_id
            cash_plan_payment_verification.save()
