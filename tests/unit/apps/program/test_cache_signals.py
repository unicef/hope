from django.core.cache import cache
from django.test import TestCase
import pytest

from extras.test_utils.factories import BusinessAreaFactory, ProgramCycleFactory, ProgramFactory
from hope.api.caches import get_or_create_cache_key
from hope.models import BusinessArea, Program, ProgramCycle

pytestmark = pytest.mark.django_db


def _version_key(business_area_slug: str, program_code: str, specific_view_cache_key: str) -> str:
    business_area_version = get_or_create_cache_key(f"{business_area_slug}:version", 1)
    return f"{business_area_slug}:{business_area_version}:{program_code}:{specific_view_cache_key}"


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


def test_program_cycle_save_increments_program_cycle_list_cache(program_cycle: ProgramCycle, program: Program) -> None:
    cache.clear()
    version_key = _version_key(program.business_area.slug, program.code, "program_cycle_list")
    initial_version = get_or_create_cache_key(version_key, 0)

    with TestCase.captureOnCommitCallbacks(execute=True):
        program_cycle.title = "Updated Programme Cycle"
        program_cycle.save()

    assert get_or_create_cache_key(version_key, 0) > initial_version


def test_program_cycle_delete_increments_program_cycle_list_cache(
    program_cycle: ProgramCycle, program: Program
) -> None:
    cache.clear()
    version_key = _version_key(program.business_area.slug, program.code, "program_cycle_list")
    initial_version = get_or_create_cache_key(version_key, 0)

    with TestCase.captureOnCommitCallbacks(execute=True):
        program_cycle.delete()

    assert get_or_create_cache_key(version_key, 0) > initial_version


def test_program_cycle_save_does_not_affect_other_program(
    program_cycle: ProgramCycle, other_program: Program, business_area: BusinessArea
) -> None:
    cache.clear()
    version_key = _version_key(business_area.slug, other_program.code, "program_cycle_list")
    initial_version = get_or_create_cache_key(version_key, 0)

    with TestCase.captureOnCommitCallbacks(execute=True):
        program_cycle.title = "Updated Programme Cycle"
        program_cycle.save()

    assert get_or_create_cache_key(version_key, 0) == initial_version


def test_program_cycle_save_increments_verification_list_cache(program_cycle: ProgramCycle, program: Program) -> None:
    cache.clear()
    version_key = _version_key(program.business_area.slug, program.code, "payment_verifications_list")
    initial_version = get_or_create_cache_key(version_key, 0)

    with TestCase.captureOnCommitCallbacks(execute=True):
        program_cycle.title = "Updated Programme Cycle"
        program_cycle.save()

    assert get_or_create_cache_key(version_key, 0) > initial_version


def test_program_cycle_save_does_not_increment_payment_plan_list_cache(
    program_cycle: ProgramCycle, program: Program
) -> None:
    cache.clear()
    version_key = _version_key(program.business_area.slug, program.code, "payment_plans_list")
    initial_version = get_or_create_cache_key(version_key, 0)

    with TestCase.captureOnCommitCallbacks(execute=True):
        program_cycle.title = "Updated Programme Cycle"
        program_cycle.save()

    assert get_or_create_cache_key(version_key, 0) == initial_version
