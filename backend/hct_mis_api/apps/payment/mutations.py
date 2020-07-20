from math import ceil

import graphene
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404
from graphene_file_upload.scalars import Upload
from scipy.special import ndtri

from core.filters import filter_age
from core.permissions import is_authenticated
from payment.models import CashPlanPaymentVerification
from program.models import CashPlan
from program.schema import CashPlanNode


class FullListArguments(graphene.InputObjectType):
    excluded_admin_areas = graphene.List(graphene.String)


class AgeInput(graphene.InputObjectType):
    min = graphene.Int()
    max = graphene.Int()


class RandomSamplingArguments(graphene.InputObjectType):
    confidence_interval = graphene.Float(required=True)
    margin_of_error = graphene.Float(required=True)
    excluded_admin_areas = graphene.List(graphene.String)
    age = AgeInput()
    sex = graphene.String()


class RapidProArguments(graphene.InputObjectType):
    flow_id = graphene.String(required=True)


class XlsxArguments(graphene.InputObjectType):
    file = Upload(required=True)


class ManualArguments(graphene.InputObjectType):
    pass


class CreatePaymentVerificationInput(graphene.InputObjectType):
    cash_plan_id = graphene.ID(required=True)
    sampling = graphene.String(required=True)
    verification_channel = graphene.String(required=True)
    full_list_arguments = FullListArguments()
    random_sampling_arguments = RandomSamplingArguments()
    rapid_pro_arguments = RapidProArguments()
    xlsx_arguments = XlsxArguments()
    manual_arguments = ManualArguments


class CreatePaymentVerificationMutation(graphene.Mutation):

    cash_plan = graphene.Field(CashPlanNode)

    class Arguments:
        input = CreatePaymentVerificationInput(required=True)

    @staticmethod
    def verify_required_arguments(input, field_name, options):
        for key, value in options:
            if key != input.get(field_name):
                continue
            for required in value.get("required"):
                if input.get(required) is None:
                    raise ValidationError(
                        f"You have to provide {required} in {key}"
                    )
            for not_allowed in value.get("not_allowed"):
                if input.get(not_allowed) is not None:
                    raise ValidationError(
                        f"You can't provide {not_allowed} in {key}"
                    )

    @classmethod
    @is_authenticated
    @transaction.atomic
    def mutate(cls, root, info, input, **kwargs):
        arg = lambda name: input.get(name)
        cls.verify_required_arguments(
            input,
            "sampling",
            {
                CashPlanPaymentVerification.SAMPLING_FULL_LIST: {
                    "required": ["full_list_arguments"],
                    "not_allowed": ["random_sampling_arguments"],
                },
                CashPlanPaymentVerification.SAMPLING_RANDOM: {
                    "required": ["random_sampling_arguments"],
                    "not_allowed": ["full_list_arguments"],
                },
            },
        )
        cls.verify_required_arguments(
            input,
            "verification_channel",
            {
                CashPlanPaymentVerification.VERIFICATION_METHOD_RAPIDPRO: {
                    "required": ["rapid_pro_arguments"],
                    "not_allowed": ["xlsx_arguments", "manual_arguments"],
                },
                CashPlanPaymentVerification.VERIFICATION_METHOD_XLSX: {
                    "required": ["xlsx_arguments"],
                    "not_allowed": ["rapid_pro_arguments", "manual_arguments"],
                },
                CashPlanPaymentVerification.VERIFICATION_METHOD_MANUAL: {
                    "required": ["manual_arguments"],
                    "not_allowed": ["rapid_pro_arguments", "xlsx_arguments"],
                },
            },
        )

    @classmethod
    def get_records_queryset(cls, input):
        arg = lambda name: input.get(name)
        cash_plan_id = arg("cash_plan_id")
        cash_plan = get_object_or_404(CashPlan, id=cash_plan_id)
        sampling = arg("sampling")
        excluded_admin_areas = []
        sex = None
        age = None
        payment_records = cash_plan.payment_records
        if sampling == CashPlanPaymentVerification.SAMPLING_FULL_LIST:
            excluded_admin_areas = arg("full_list_arguments").get(
                "excluded_admin_areas", []
            )
        elif sampling == CashPlanPaymentVerification.SAMPLING_RANDOM:
            random_sampling_arguments = arg("random_sampling_arguments")
            confidence_interval = random_sampling_arguments.get(
                "confidence_interval"
            )
            margin_of_error = random_sampling_arguments.get("margin_of_error")
            sex = random_sampling_arguments.get("sex")
            age = random_sampling_arguments.get("random_sampling_arguments")

        payment_records = payment_records.filter(
            ~(Q(household__admin_area__title__in=excluded_admin_areas))
        )
        if sex is not None:
            payment_records = payment_records.filter(
                household__head_of_household__sex=sex
            )
        if age is not None:
            payment_records = filter_age(
                "household__head_of_household__birth_date",
                payment_records,
                age.get(min),
                age.get("max"),
            )
        payment_records_sample_count = payment_records.count()
        if sampling == CashPlanPaymentVerification.SAMPLING_RANDOM:
            payment_records_sample_count = CreatePaymentVerificationMutation.get_number_of_samples(
                payment_records_sample_count,
                confidence_interval,
                margin_of_error,
            )
            payment_records = payment_records.order_by("?")[
                :payment_records_sample_count
            ]
        return payment_records

    @classmethod
    def get_number_of_samples(
        cls, payment_records_sample_count, confidence_interval, margin_of_error
    ):
        variable = 0.5
        z_score = ndtri(confidence_interval + (1 - confidence_interval) / 2)
        theoretical_sample = (
            (z_score ** 2) * variable * (1 - variable) / margin_of_error ** 2
        )
        actual_sample = ceil(
            (
                payment_records_sample_count
                * theoretical_sample
                / (theoretical_sample + payment_records_sample_count)
            )
            * 1.5
        )
        return actual_sample


class Mutations(graphene.ObjectType):
    create_cash_plan_payment_verification = CreatePaymentVerificationMutation.Field()
