from django.core.cache import cache
from django.test import TestCase
import pytest

from extras.test_utils.factories import (
    BusinessAreaFactory,
    PaymentListFactory,
    PaymentVerificationPlanFactory,
    PaymentVerificationSummaryFactory,
    ProgramCycleFactory,
    ProgramFactory,
)
from hope.api.caches import get_or_create_cache_key
from hope.apps.payment.api.caches import invalidate_payment_list_list_cache
from hope.models import (
    BusinessArea,
    PaymentList,
    PaymentVerificationPlan,
    PaymentVerificationSummary,
    Program,
    ProgramCycle,
)

pytestmark = pytest.mark.django_db


def _version_key(business_area_slug: str, program_code: str, specific_view_cache_key: str) -> str:
    business_area_version = get_or_create_cache_key(f"{business_area_slug}:version", 1)
    return f"{business_area_slug}:{business_area_version}:{program_code}:{specific_view_cache_key}"


def _business_area_version_key(business_area_slug: str, specific_view_cache_key: str) -> str:
    business_area_version = get_or_create_cache_key(f"{business_area_slug}:version", 1)
    return f"{business_area_slug}:{business_area_version}:{specific_view_cache_key}"


@pytest.fixture
def business_area() -> BusinessArea:
    return BusinessAreaFactory(slug="afghanistan", name="Afghanistan")


@pytest.fixture
def program(business_area: BusinessArea) -> Program:
    return ProgramFactory(business_area=business_area)


@pytest.fixture
def other_program(business_area: BusinessArea) -> Program:
    return ProgramFactory(business_area=business_area)


@pytest.fixture
def program_cycle(program: Program) -> ProgramCycle:
    return ProgramCycleFactory(program=program)


@pytest.fixture
def payment_list(program_cycle: ProgramCycle) -> PaymentList:
    return PaymentListFactory(program_cycle=program_cycle)


@pytest.fixture
def payment_verification_summary(payment_list: PaymentList) -> PaymentVerificationSummary:
    return PaymentVerificationSummaryFactory(payment_list=payment_list)


@pytest.fixture
def payment_verification_plan(
    payment_list: PaymentList, payment_verification_summary: PaymentVerificationSummary
) -> PaymentVerificationPlan:
    return PaymentVerificationPlanFactory(payment_list=payment_list)


def test_payment_list_save_increments_payment_list_list_cache(payment_list: PaymentList, program: Program) -> None:
    cache.clear()
    version_key = _version_key(program.business_area.slug, program.code, "payment_lists_list")
    initial_version = get_or_create_cache_key(version_key, 0)

    with TestCase.captureOnCommitCallbacks(execute=True):
        payment_list.name = "Updated Payment Plan"
        payment_list.save()

    assert get_or_create_cache_key(version_key, 0) > initial_version


def test_payment_list_save_increments_target_population_list_cache(payment_list: PaymentList, program: Program) -> None:
    cache.clear()
    version_key = _version_key(program.business_area.slug, program.code, "target_populations_list")
    initial_version = get_or_create_cache_key(version_key, 0)

    with TestCase.captureOnCommitCallbacks(execute=True):
        payment_list.name = "Updated Payment Plan"
        payment_list.save()

    assert get_or_create_cache_key(version_key, 0) > initial_version


def test_payment_list_soft_delete_increments_payment_list_list_cache(
    payment_list: PaymentList, program: Program
) -> None:
    cache.clear()
    version_key = _version_key(program.business_area.slug, program.code, "payment_lists_list")
    initial_version = get_or_create_cache_key(version_key, 0)

    with TestCase.captureOnCommitCallbacks(execute=True):
        payment_list.delete()

    assert get_or_create_cache_key(version_key, 0) > initial_version


def test_payment_list_hard_delete_increments_payment_list_list_cache(
    payment_list: PaymentList, program: Program
) -> None:
    cache.clear()
    version_key = _version_key(program.business_area.slug, program.code, "payment_lists_list")
    initial_version = get_or_create_cache_key(version_key, 0)

    with TestCase.captureOnCommitCallbacks(execute=True):
        payment_list.delete(soft=False)

    assert get_or_create_cache_key(version_key, 0) > initial_version


def test_payment_list_save_does_not_affect_other_program(
    payment_list: PaymentList, other_program: Program, business_area: BusinessArea
) -> None:
    cache.clear()
    version_key = _version_key(business_area.slug, other_program.code, "payment_lists_list")
    initial_version = get_or_create_cache_key(version_key, 0)

    with TestCase.captureOnCommitCallbacks(execute=True):
        payment_list.name = "Updated Payment Plan"
        payment_list.save()

    assert get_or_create_cache_key(version_key, 0) == initial_version


def test_payment_verification_plan_save_increments_verification_list_cache(
    payment_verification_plan: PaymentVerificationPlan, program: Program
) -> None:
    cache.clear()
    version_key = _version_key(program.business_area.slug, program.code, "payment_verifications_list")
    initial_version = get_or_create_cache_key(version_key, 0)

    with TestCase.captureOnCommitCallbacks(execute=True):
        payment_verification_plan.sampling = "RANDOM"
        payment_verification_plan.save()

    assert get_or_create_cache_key(version_key, 0) > initial_version


def test_payment_verification_summary_save_increments_verification_list_cache(
    payment_verification_summary: PaymentVerificationSummary, program: Program
) -> None:
    cache.clear()
    version_key = _version_key(program.business_area.slug, program.code, "payment_verifications_list")
    initial_version = get_or_create_cache_key(version_key, 0)

    with TestCase.captureOnCommitCallbacks(execute=True):
        payment_verification_summary.status = PaymentVerificationSummary.STATUS_ACTIVE
        payment_verification_summary.save()

    assert get_or_create_cache_key(version_key, 0) > initial_version


def test_payment_verification_plan_save_does_not_increment_payment_list_list_cache(
    payment_verification_plan: PaymentVerificationPlan, program: Program
) -> None:
    cache.clear()
    version_key = _version_key(program.business_area.slug, program.code, "payment_lists_list")
    initial_version = get_or_create_cache_key(version_key, 0)

    with TestCase.captureOnCommitCallbacks(execute=True):
        payment_verification_plan.sampling = "RANDOM"
        payment_verification_plan.save()

    assert get_or_create_cache_key(version_key, 0) == initial_version


def test_invalidate_payment_list_list_cache_helper(program: Program) -> None:
    cache.clear()
    version_key = _version_key(program.business_area.slug, program.code, "payment_lists_list")
    initial_version = get_or_create_cache_key(version_key, 0)

    with TestCase.captureOnCommitCallbacks(execute=True):
        invalidate_payment_list_list_cache(program.business_area.slug, program.code)

    assert get_or_create_cache_key(version_key, 0) > initial_version


@pytest.mark.parametrize(
    "payment_list_status",
    [
        PaymentList.Status.IN_APPROVAL,
        PaymentList.Status.IN_AUTHORIZATION,
        PaymentList.Status.IN_REVIEW,
        PaymentList.Status.ACCEPTED,
    ],
)
def test_payment_list_managerial_status_increments_managerial_list_cache(
    payment_list: PaymentList, business_area: BusinessArea, payment_list_status: PaymentList.Status
) -> None:
    cache.clear()
    version_key = _business_area_version_key(business_area.slug, "management_payment_lists_list")
    initial_version = get_or_create_cache_key(version_key, 0)

    with TestCase.captureOnCommitCallbacks(execute=True):
        payment_list.status = payment_list_status
        payment_list.save()

    assert get_or_create_cache_key(version_key, 0) > initial_version


def test_payment_list_open_does_not_increment_managerial_list_cache(
    payment_list: PaymentList, business_area: BusinessArea
) -> None:
    cache.clear()
    version_key = _business_area_version_key(business_area.slug, "management_payment_lists_list")
    initial_version = get_or_create_cache_key(version_key, 0)

    with TestCase.captureOnCommitCallbacks(execute=True):
        payment_list.status = PaymentList.Status.OPEN
        payment_list.save()

    assert get_or_create_cache_key(version_key, 0) == initial_version
