from django.core.cache import cache
from django.test import TestCase
from freezegun import freeze_time
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
from hope.apps.payment.api.caches import TodayKeyBit, invalidate_payment_list_list_cache
from hope.models import (
    BusinessArea,
    PaymentList,
    PaymentPlan,
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
def payment_plan(payment_list: PaymentList) -> PaymentPlan:
    return payment_list.payment_plan


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
    version_key = _business_area_version_key(business_area.slug, "management_payment_plans_list")
    initial_version = get_or_create_cache_key(version_key, 0)

    with TestCase.captureOnCommitCallbacks(execute=True):
        payment_list.status = payment_list_status
        payment_list.save()

    assert get_or_create_cache_key(version_key, 0) > initial_version


def test_payment_list_open_does_not_increment_managerial_list_cache(
    payment_list: PaymentList, business_area: BusinessArea
) -> None:
    cache.clear()
    version_key = _business_area_version_key(business_area.slug, "management_payment_plans_list")
    initial_version = get_or_create_cache_key(version_key, 0)

    with TestCase.captureOnCommitCallbacks(execute=True):
        payment_list.status = PaymentList.Status.OPEN
        payment_list.save()

    assert get_or_create_cache_key(version_key, 0) == initial_version


@pytest.mark.parametrize(
    "payment_plan_status",
    [
        PaymentPlan.Status.IN_APPROVAL,
        PaymentPlan.Status.IN_AUTHORIZATION,
        PaymentPlan.Status.IN_REVIEW,
        PaymentPlan.Status.ACCEPTED,
    ],
)
def test_payment_plan_managerial_status_increments_managerial_list_cache(
    payment_plan: PaymentPlan, business_area: BusinessArea, payment_plan_status: PaymentPlan.Status
) -> None:
    cache.clear()
    version_key = _business_area_version_key(business_area.slug, "management_payment_plans_list")
    initial_version = get_or_create_cache_key(version_key, 0)

    with TestCase.captureOnCommitCallbacks(execute=True):
        payment_plan.status = payment_plan_status
        payment_plan.save(update_fields=["status"])

    assert get_or_create_cache_key(version_key, 0) > initial_version


@pytest.mark.parametrize(
    "payment_plan_status",
    [
        PaymentPlan.Status.LOCKED,
        PaymentPlan.Status.FINISHED,
        PaymentPlan.Status.ABORTED,
    ],
)
def test_payment_plan_leaving_managerial_status_increments_managerial_list_cache(
    payment_plan: PaymentPlan, business_area: BusinessArea, payment_plan_status: PaymentPlan.Status
) -> None:
    cache.clear()
    version_key = _business_area_version_key(business_area.slug, "management_payment_plans_list")
    initial_version = get_or_create_cache_key(version_key, 0)

    with TestCase.captureOnCommitCallbacks(execute=True):
        payment_plan.status = payment_plan_status
        payment_plan.save()

    assert get_or_create_cache_key(version_key, 0) > initial_version


@pytest.mark.parametrize(
    "payment_plan_status",
    [
        PaymentPlan.Status.LOCKED,
        PaymentPlan.Status.FINISHED,
        PaymentPlan.Status.ABORTED,
    ],
)
def test_payment_plan_out_of_managerial_list_unrelated_save_does_not_increment_managerial_list_cache(
    payment_plan: PaymentPlan, business_area: BusinessArea, payment_plan_status: PaymentPlan.Status
) -> None:
    PaymentPlan.objects.filter(pk=payment_plan.pk).update(status=payment_plan_status)
    payment_plan.refresh_from_db()
    cache.clear()
    version_key = _business_area_version_key(business_area.slug, "management_payment_plans_list")
    initial_version = get_or_create_cache_key(version_key, 0)

    with TestCase.captureOnCommitCallbacks(execute=True):
        payment_plan.save(update_fields=["background_action_status"])

    assert get_or_create_cache_key(version_key, 0) == initial_version


def test_payment_plan_open_does_not_increment_managerial_list_cache(
    payment_plan: PaymentPlan, business_area: BusinessArea
) -> None:
    cache.clear()
    version_key = _business_area_version_key(business_area.slug, "management_payment_plans_list")
    initial_version = get_or_create_cache_key(version_key, 0)

    with TestCase.captureOnCommitCallbacks(execute=True):
        payment_plan.status = PaymentPlan.Status.OPEN
        payment_plan.save()

    assert get_or_create_cache_key(version_key, 0) == initial_version


def test_program_save_increments_managerial_list_cache(program: Program, business_area: BusinessArea) -> None:
    cache.clear()
    version_key = _business_area_version_key(business_area.slug, "management_payment_plans_list")
    initial_version = get_or_create_cache_key(version_key, 0)

    with TestCase.captureOnCommitCallbacks(execute=True):
        program.reconciliation_window_in_days = 30
        program.save()

    assert get_or_create_cache_key(version_key, 0) > initial_version


def test_program_save_of_managerial_field_increments_managerial_list_cache(
    program: Program, business_area: BusinessArea
) -> None:
    cache.clear()
    version_key = _business_area_version_key(business_area.slug, "management_payment_plans_list")
    initial_version = get_or_create_cache_key(version_key, 0)

    with TestCase.captureOnCommitCallbacks(execute=True):
        program.reconciliation_window_in_days = 30
        program.save(update_fields=["reconciliation_window_in_days"])

    assert get_or_create_cache_key(version_key, 0) > initial_version


def test_program_save_of_unrelated_fields_does_not_increment_managerial_list_cache(
    program: Program, business_area: BusinessArea
) -> None:
    cache.clear()
    version_key = _business_area_version_key(business_area.slug, "management_payment_plans_list")
    initial_version = get_or_create_cache_key(version_key, 0)

    with TestCase.captureOnCommitCallbacks(execute=True):
        program.save(update_fields=["household_count", "individual_count"])

    assert get_or_create_cache_key(version_key, 0) == initial_version


def test_today_key_bit_changes_daily() -> None:
    key_bit = TodayKeyBit()

    with freeze_time("2026-11-02 23:59:00"):
        today = key_bit.get_data(None, None, None, None, (), {})
    with freeze_time("2026-11-03 00:01:00"):
        tomorrow = key_bit.get_data(None, None, None, None, (), {})

    assert today == "2026-11-02"
    assert tomorrow == "2026-11-03"
