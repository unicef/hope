import math
from decimal import Decimal

import graphene
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from graphene_file_upload.scalars import Upload
from graphql import GraphQLError

from core.filters import filter_age
from core.permissions import is_authenticated
from core.utils import decode_id_string
from household.models import Individual
from payment.inputs import (
    CreatePaymentVerificationInput,
    EditCashPlanPaymentVerificationInput,
)
from payment.models import CashPlanPaymentVerification, PaymentVerification
from payment.rapid_pro.api import RapidProAPI
from payment.schema import PaymentVerificationNode
from payment.utils import get_number_of_samples, from_received_to_status, calculate_counts
from payment.xlsx.XlsxVerificationImportService import XlsxVerificationImportService
from program.models import CashPlan
from program.schema import CashPlanNode


class CreatePaymentVerificationMutation(graphene.Mutation):

    cash_plan = graphene.Field(CashPlanNode)

    class Arguments:
        input = CreatePaymentVerificationInput(required=True)

    @staticmethod
    def verify_required_arguments(input, field_name, options):
        for key, value in options.items():
            if key != input.get(field_name):
                continue
            for required in value.get("required"):
                if input.get(required) is None:
                    raise GraphQLError(f"You have to provide {required} in {key}")
            for not_allowed in value.get("not_allowed"):
                if input.get(not_allowed) is not None:
                    raise GraphQLError(f"You can't provide {not_allowed} in {key}")

    @classmethod
    @is_authenticated
    @transaction.atomic
    def mutate(cls, root, info, input, **kwargs):
        arg = lambda name: input.get(name)
        cls.verify_required_arguments(
            input,
            "status",
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



class Mutations(graphene.ObjectType):
    create_cash_plan_payment_verification = CreatePaymentVerificationMutation.Field()
