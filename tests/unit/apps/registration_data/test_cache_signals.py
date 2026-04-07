from django.core.cache import cache
from django.test import TestCase
import pytest

from extras.test_utils.factories import BusinessAreaFactory, ProgramFactory, RegistrationDataImportFactory
from hope.api.caches import get_or_create_cache_key
from hope.apps.registration_data.signals import invalidate_rdi_cache
from hope.models import BusinessArea, Program

pytestmark = pytest.mark.django_db


def _rdi_version_key(business_area_slug: str, program_code: str) -> str:
    ba_version = get_or_create_cache_key(f"{business_area_slug}:version", 1)
    return f"{business_area_slug}:{ba_version}:{program_code}:registration_data_import_list"


@pytest.fixture
def business_area() -> BusinessArea:
    return BusinessAreaFactory(slug="afghanistan", name="Afghanistan")


@pytest.fixture
def program(business_area: BusinessArea) -> Program:
    return ProgramFactory(business_area=business_area)


def test_rdi_save_increments_cache(program: Program) -> None:
    cache.clear()

    version_key = _rdi_version_key(program.business_area.slug, program.code)
    initial_version = get_or_create_cache_key(version_key, 0)

    with TestCase.captureOnCommitCallbacks(execute=True):
        RegistrationDataImportFactory(business_area=program.business_area, program=program)

    new_version = get_or_create_cache_key(version_key, 0)
    assert new_version > initial_version


def test_rdi_delete_increments_cache(program: Program) -> None:
    rdi = RegistrationDataImportFactory(business_area=program.business_area, program=program)
    cache.clear()

    version_key = _rdi_version_key(program.business_area.slug, program.code)
    initial_version = get_or_create_cache_key(version_key, 0)

    with TestCase.captureOnCommitCallbacks(execute=True):
        rdi.delete()

    new_version = get_or_create_cache_key(version_key, 0)
    assert new_version > initial_version


def test_rdi_save_does_not_affect_other_program(business_area: BusinessArea) -> None:
    program1 = ProgramFactory(business_area=business_area)
    program2 = ProgramFactory(business_area=business_area)
    cache.clear()

    version_key_p2 = _rdi_version_key(business_area.slug, program2.code)
    initial_version_p2 = get_or_create_cache_key(version_key_p2, 0)

    with TestCase.captureOnCommitCallbacks(execute=True):
        RegistrationDataImportFactory(business_area=business_area, program=program1)

    new_version_p2 = get_or_create_cache_key(version_key_p2, 0)
    assert new_version_p2 == initial_version_p2


def test_invalidate_rdi_cache_helper(program: Program) -> None:
    cache.clear()

    version_key = _rdi_version_key(program.business_area.slug, program.code)
    initial_version = get_or_create_cache_key(version_key, 0)

    with TestCase.captureOnCommitCallbacks(execute=True):
        invalidate_rdi_cache(program.business_area.slug, program.code)

    new_version = get_or_create_cache_key(version_key, 0)
    assert new_version > initial_version


def test_rdi_update_field_increments_cache(program: Program) -> None:
    rdi = RegistrationDataImportFactory(business_area=program.business_area, program=program)
    cache.clear()

    version_key = _rdi_version_key(program.business_area.slug, program.code)
    initial_version = get_or_create_cache_key(version_key, 0)

    with TestCase.captureOnCommitCallbacks(execute=True):
        rdi.name = "Updated RDI"
        rdi.save()

    new_version = get_or_create_cache_key(version_key, 0)
    assert new_version > initial_version
