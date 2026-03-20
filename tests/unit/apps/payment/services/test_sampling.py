from datetime import date
import random

import pytest
from rest_framework.exceptions import ValidationError

from extras.test_utils.factories import (
    AreaFactory,
    HouseholdFactory,
    IndividualFactory,
    PaymentFactory,
    PaymentVerificationPlanFactory,
)
from hope.apps.payment.services.sampling import Sampling
from hope.models import Area, Payment, PaymentVerificationPlan

pytestmark = pytest.mark.django_db


@pytest.fixture
def seed_random() -> None:
    random.seed(2137)


@pytest.fixture
def verification_plan() -> PaymentVerificationPlan:
    return PaymentVerificationPlanFactory()


@pytest.fixture
def areas() -> dict[str, Area]:
    return {
        "area_a": AreaFactory(),
        "area_b": AreaFactory(),
    }


@pytest.fixture
def payments(verification_plan: PaymentVerificationPlan, areas: dict) -> list[Payment]:
    plan = verification_plan.payment_plan
    ba = plan.business_area
    program = plan.program_cycle.program

    def _make_payment(sex: str, birth_date: date, area: Area) -> Payment:
        hoh = IndividualFactory(household=None, sex=sex, birth_date=birth_date, business_area=ba, program=program)
        household = HouseholdFactory(
            head_of_household=hoh,
            admin1=area,
            business_area=ba,
            program=program,
            registration_data_import=hoh.registration_data_import,
        )
        return PaymentFactory(parent=plan, business_area=ba, household=household)

    return [
        _make_payment("MALE", date(1996, 1, 1), areas["area_a"]),
        _make_payment("FEMALE", date(1996, 6, 1), areas["area_a"]),
        _make_payment("MALE", date(1976, 1, 1), areas["area_b"]),
        _make_payment("FEMALE", date(1976, 6, 1), areas["area_b"]),
    ]


def test_random_sampling_filters_by_sex(
    seed_random: None, verification_plan: PaymentVerificationPlan, payments: list[Payment]
) -> None:
    plan = verification_plan.payment_plan
    input_data = {
        "sampling": PaymentVerificationPlan.SAMPLING_RANDOM,
        "random_sampling_arguments": {
            "confidence_interval": 0.95,
            "margin_of_error": 0.05,
            "sex": "FEMALE",
            "age": None,
            "excluded_admin_areas": [],
        },
    }
    sampling_service = Sampling(input_data, plan, plan.payment_items.all())
    updated_plan, sampled_records = sampling_service.process_sampling(verification_plan)

    assert updated_plan is verification_plan
    sampled_ids = set(sampled_records.values_list("id", flat=True))
    assert sampled_ids == {payments[1].id, payments[3].id}


def test_random_sampling_filters_by_age(
    seed_random: None, verification_plan: PaymentVerificationPlan, payments: list[Payment]
) -> None:
    plan = verification_plan.payment_plan
    input_data = {
        "sampling": PaymentVerificationPlan.SAMPLING_RANDOM,
        "random_sampling_arguments": {
            "confidence_interval": 0.95,
            "margin_of_error": 0.05,
            "sex": None,
            "age": {"min": 40, "max": 60},
            "excluded_admin_areas": [],
        },
    }
    sampling_service = Sampling(input_data, plan, plan.payment_items.all())
    updated_plan, sampled_records = sampling_service.process_sampling(verification_plan)

    assert updated_plan is verification_plan
    sampled_ids = set(sampled_records.values_list("id", flat=True))
    assert sampled_ids == {payments[2].id, payments[3].id}


def test_random_sampling_caps_sample_size_to_population(
    seed_random: None, verification_plan: PaymentVerificationPlan, payments: list[Payment]
) -> None:
    plan = verification_plan.payment_plan
    input_data = {
        "sampling": PaymentVerificationPlan.SAMPLING_RANDOM,
        "random_sampling_arguments": {
            "confidence_interval": 0.95,
            "margin_of_error": 0.01,
            "sex": None,
            "age": None,
            "excluded_admin_areas": [],
        },
    }
    sampling_service = Sampling(input_data, plan, plan.payment_items.all())
    updated_plan, sampled_records = sampling_service.process_sampling(verification_plan)

    assert updated_plan is verification_plan
    assert sampled_records.count() == len(payments)


def test_random_sampling_zero_sample_size_returns_empty(
    verification_plan: PaymentVerificationPlan, payments: list[Payment]
) -> None:
    plan = verification_plan.payment_plan
    input_data = {
        "sampling": PaymentVerificationPlan.SAMPLING_RANDOM,
        "random_sampling_arguments": {
            "confidence_interval": 0.95,
            "margin_of_error": 0.05,
            "sex": None,
            "age": {"min": 90, "max": 100},
            "excluded_admin_areas": [],
        },
    }
    sampling_service = Sampling(input_data, plan, plan.payment_items.all())
    updated_plan, sampled_records = sampling_service.process_sampling(verification_plan)

    assert updated_plan is verification_plan
    assert sampled_records.count() == 0


def test_full_list_sampling_returns_all_records(
    verification_plan: PaymentVerificationPlan, payments: list[Payment]
) -> None:
    plan = verification_plan.payment_plan
    input_data = {
        "sampling": PaymentVerificationPlan.SAMPLING_FULL_LIST,
        "full_list_arguments": {
            "excluded_admin_areas": [],
        },
    }
    sampling_service = Sampling(input_data, plan, plan.payment_items.all())
    updated_plan, sampled_records = sampling_service.process_sampling(verification_plan)

    assert updated_plan is verification_plan
    assert updated_plan.sample_size == len(payments)
    assert sampled_records.count() == len(payments)


def test_full_list_sampling_excludes_admin_areas(
    verification_plan: PaymentVerificationPlan, payments: list[Payment], areas: dict
) -> None:
    plan = verification_plan.payment_plan
    input_data = {
        "sampling": PaymentVerificationPlan.SAMPLING_FULL_LIST,
        "full_list_arguments": {
            "excluded_admin_areas": [areas["area_a"].id],
        },
    }
    sampling_service = Sampling(input_data, plan, plan.payment_items.all())
    updated_plan, sampled_records = sampling_service.process_sampling(verification_plan)

    assert updated_plan is verification_plan
    sampled_ids = set(sampled_records.values_list("id", flat=True))
    assert sampled_ids == {payments[2].id, payments[3].id}


def test_generate_sampling_returns_count_and_sample_size(
    verification_plan: PaymentVerificationPlan, payments: list[Payment]
) -> None:
    plan = verification_plan.payment_plan
    input_data = {
        "sampling": PaymentVerificationPlan.SAMPLING_FULL_LIST,
        "full_list_arguments": {
            "excluded_admin_areas": [],
        },
    }
    sampling_service = Sampling(input_data, plan, plan.payment_items.all())
    payment_record_count, sample_size = sampling_service.generate_sampling()

    assert payment_record_count == len(payments)
    assert sample_size == len(payments)


def test_process_sampling_raises_when_no_payment_records(
    verification_plan: PaymentVerificationPlan,
) -> None:
    plan = verification_plan.payment_plan
    input_data = {
        "sampling": PaymentVerificationPlan.SAMPLING_RANDOM,
        "random_sampling_arguments": {
            "confidence_interval": 0.95,
            "margin_of_error": 0.05,
            "sex": None,
            "age": None,
            "excluded_admin_areas": [],
        },
    }
    sampling_service = Sampling(input_data, plan, Payment.objects.none())

    with pytest.raises(
        ValidationError, match="There are no payment records that could be assigned to a new verification plan."
    ):
        sampling_service.process_sampling(verification_plan)
