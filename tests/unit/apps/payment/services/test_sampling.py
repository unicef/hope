from unittest.mock import patch

from django.test import TestCase
import pytest
from rest_framework.exceptions import ValidationError

from extras.test_utils.factories.core import create_afghanistan
from extras.test_utils.factories.geo import AreaFactory
from extras.test_utils.factories.household import HouseholdFactory, IndividualFactory
from extras.test_utils.factories.payment import (
    PaymentFactory,
    PaymentPlanFactory,
    PaymentVerificationPlanFactory,
    PaymentVerificationSummaryFactory,
)
from hope.apps.payment.services.sampling import Sampling
from hope.models import Payment, PaymentVerificationPlan


class TestSampling(TestCase):
    def setUp(self) -> None:
        create_afghanistan()

    def test_process_sampling_random_limits_to_sample_size(self) -> None:
        payment_plan = PaymentPlanFactory()
        PaymentVerificationSummaryFactory(payment_plan=payment_plan)
        payments = PaymentFactory.create_batch(
            3,
            parent=payment_plan,
            business_area=payment_plan.business_area,
        )
        verification_plan = PaymentVerificationPlanFactory(payment_plan=payment_plan)
        input_data = {
            "sampling": PaymentVerificationPlan.SAMPLING_RANDOM,
            "random_sampling_arguments": {
                "confidence_interval": 95,
                "margin_of_error": 5,
                "sex": None,
                "age": None,
                "excluded_admin_areas": [],
            },
        }
        sampling_service = Sampling(input_data, payment_plan, payment_plan.payment_items.all())

        with (
            patch("hope.apps.payment.services.sampling.get_number_of_samples", return_value=2),
            patch(
                "hope.apps.payment.services.sampling.random.sample",
                side_effect=lambda seq, k: seq[:k],
            ),
        ):
            updated_plan, sampled_records = sampling_service.process_sampling(verification_plan)

        assert updated_plan.sample_size == 2
        assert updated_plan.sampling == PaymentVerificationPlan.SAMPLING_RANDOM
        sampled_ids = set(sampled_records.values_list("id", flat=True))
        assert len(sampled_ids) == 2
        assert sampled_ids.issubset({p.id for p in payments})

    def test_process_sampling_random_with_zero_sample_size_returns_empty(self) -> None:
        payment_plan = PaymentPlanFactory()
        PaymentVerificationSummaryFactory(payment_plan=payment_plan)
        PaymentFactory.create_batch(
            2,
            parent=payment_plan,
            business_area=payment_plan.business_area,
        )
        verification_plan = PaymentVerificationPlanFactory(payment_plan=payment_plan)
        input_data = {
            "sampling": PaymentVerificationPlan.SAMPLING_RANDOM,
            "random_sampling_arguments": {
                "confidence_interval": 95,
                "margin_of_error": 5,
                "sex": None,
                "age": None,
                "excluded_admin_areas": [],
            },
        }
        sampling_service = Sampling(input_data, payment_plan, payment_plan.payment_items.all())

        with patch("hope.apps.payment.services.sampling.get_number_of_samples", return_value=0):
            _, sampled_records = sampling_service.process_sampling(verification_plan)

        assert sampled_records.count() == 0

    def test_process_sampling_full_list_excludes_admin_areas(self) -> None:
        payment_plan = PaymentPlanFactory()
        PaymentVerificationSummaryFactory(payment_plan=payment_plan)
        excluded_area = AreaFactory()
        included_area = AreaFactory()
        hoh1 = IndividualFactory(household=None)
        PaymentFactory(
            parent=payment_plan,
            business_area=payment_plan.business_area,
            household=HouseholdFactory(
                admin1=excluded_area, program=payment_plan.program_cycle.program, head_of_household=hoh1
            ),
        )
        hoh2 = IndividualFactory(household=None)
        included_payment = PaymentFactory(
            parent=payment_plan,
            business_area=payment_plan.business_area,
            household=HouseholdFactory(
                admin1=included_area,
                program=payment_plan.program_cycle.program,
                head_of_household=hoh2,
            ),
        )
        verification_plan = PaymentVerificationPlanFactory(payment_plan=payment_plan)
        input_data = {
            "sampling": PaymentVerificationPlan.SAMPLING_FULL_LIST,
            "full_list_arguments": {
                "confidence_interval": 95,
                "margin_of_error": 5,
                "excluded_admin_areas": [excluded_area.id],
            },
        }
        sampling_service = Sampling(input_data, payment_plan, payment_plan.payment_items.all())

        updated_plan, sampled_records = sampling_service.process_sampling(verification_plan)

        assert updated_plan.sample_size == payment_plan.payment_items.count()
        sampled_ids = list(sampled_records.values_list("id", flat=True))
        assert sampled_ids == [included_payment.id]

    def test_process_sampling_raises_when_no_payment_records(self) -> None:
        payment_plan = PaymentPlanFactory()
        PaymentVerificationSummaryFactory(payment_plan=payment_plan)
        verification_plan = PaymentVerificationPlanFactory(payment_plan=payment_plan)
        input_data = {
            "sampling": PaymentVerificationPlan.SAMPLING_RANDOM,
            "random_sampling_arguments": {
                "confidence_interval": 95,
                "margin_of_error": 5,
                "sex": None,
                "age": None,
                "excluded_admin_areas": [],
            },
        }
        sampling_service = Sampling(input_data, payment_plan, Payment.objects.none())

        with pytest.raises(ValidationError):
            sampling_service.process_sampling(verification_plan)
