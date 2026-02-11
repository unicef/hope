"""Tests for program deduplication flags functionality."""

from typing import Any, Callable

import pytest
from rest_framework import status
from rest_framework.reverse import reverse

from extras.test_utils.factories import (
    BusinessAreaFactory,
    PartnerFactory,
    ProgramFactory,
    RegistrationDataImportFactory,
    UserFactory,
)
from hope.apps.account.permissions import Permissions
from hope.models import BusinessArea, Partner, Program, RegistrationDataImport, User

pytestmark = pytest.mark.django_db


@pytest.fixture
def afghanistan(db: Any) -> BusinessArea:
    return BusinessAreaFactory(name="Afghanistan", slug="afghanistan")


@pytest.fixture
def partner(db: Any) -> Partner:
    return PartnerFactory(name="TestPartner")


@pytest.fixture
def user(partner: Partner) -> User:
    return UserFactory(partner=partner)


@pytest.fixture
def program(afghanistan: BusinessArea) -> Program:
    return ProgramFactory(
        business_area=afghanistan,
        status=Program.ACTIVE,
        partner_access=Program.SELECTED_PARTNERS_ACCESS,
    )


@pytest.fixture
def deduplication_flags_url(afghanistan: BusinessArea, program: Program) -> str:
    return reverse(
        "api:programs:programs-deduplication-flags",
        kwargs={
            "business_area_slug": afghanistan.slug,
            "slug": program.slug,
        },
    )


@pytest.fixture
def authenticated_client(api_client: Callable, user: User) -> Any:
    return api_client(user)


def test_deduplication_flags_can_run_deduplication_and_deduplication_enabled(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    deduplication_flags_url: str,
    create_user_role_with_permissions: Callable,
) -> None:
    program.biometric_deduplication_enabled = True
    program.save()
    RegistrationDataImportFactory(
        program=program,
        deduplication_engine_status=RegistrationDataImport.MERGED,
    )
    create_user_role_with_permissions(
        user=user,
        permissions=[Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS],
        business_area=afghanistan,
        whole_business_area_access=True,
    )
    response = authenticated_client.get(deduplication_flags_url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data == {
        "can_run_deduplication": True,
        "is_deduplication_disabled": False,
    }


def test_deduplication_flags_can_run_deduplication_and_deduplication_engine_in_progress(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    deduplication_flags_url: str,
    create_user_role_with_permissions: Callable,
) -> None:
    program.biometric_deduplication_enabled = True
    program.save()
    # deduplication engine in progress - > deduplication disabled
    RegistrationDataImportFactory(
        program=program,
        deduplication_engine_status=RegistrationDataImport.DEDUP_ENGINE_IN_PROGRESS,
    )
    create_user_role_with_permissions(
        user=user,
        permissions=[Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS],
        business_area=afghanistan,
        whole_business_area_access=True,
    )
    response = authenticated_client.get(deduplication_flags_url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data == {
        "can_run_deduplication": True,
        "is_deduplication_disabled": True,
    }


def test_deduplication_flags_can_run_deduplication_and_all_rdis_deduplicated(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    deduplication_flags_url: str,
    create_user_role_with_permissions: Callable,
) -> None:
    program.biometric_deduplication_enabled = True
    program.save()
    # all RDIs are deduplicated - > deduplication disabled
    RegistrationDataImportFactory(
        program=program,
        deduplication_engine_status=RegistrationDataImport.DEDUP_ENGINE_FINISHED,
    )
    assert RegistrationDataImport.objects.filter(program=program).count() == 1
    create_user_role_with_permissions(
        user=user,
        permissions=[Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS],
        business_area=afghanistan,
        whole_business_area_access=True,
    )
    response = authenticated_client.get(deduplication_flags_url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data == {
        "can_run_deduplication": True,
        "is_deduplication_disabled": True,
    }


def test_deduplication_flags_can_run_deduplication_and_not_all_rdis_deduplicated(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    deduplication_flags_url: str,
    create_user_role_with_permissions: Callable,
) -> None:
    program.biometric_deduplication_enabled = True
    program.save()
    RegistrationDataImportFactory(
        program=program,
        deduplication_engine_status=RegistrationDataImport.DEDUP_ENGINE_FINISHED,
    )
    RegistrationDataImportFactory(
        program=program,
        deduplication_engine_status=RegistrationDataImport.MERGED,
    )
    create_user_role_with_permissions(
        user=user,
        permissions=[Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS],
        business_area=afghanistan,
        whole_business_area_access=True,
    )
    response = authenticated_client.get(deduplication_flags_url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data == {
        "can_run_deduplication": True,
        "is_deduplication_disabled": False,
    }


def test_deduplication_flags_cannot_run_deduplication_and_rdi_merge_in_progress(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    deduplication_flags_url: str,
    create_user_role_with_permissions: Callable,
) -> None:
    program.biometric_deduplication_enabled = False
    program.save()
    # RDI merge in progress - > deduplication disabled
    RegistrationDataImportFactory(
        program=program,
        status=RegistrationDataImport.MERGING,
    )
    create_user_role_with_permissions(
        user=user,
        permissions=[Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS],
        business_area=afghanistan,
        whole_business_area_access=True,
    )
    response = authenticated_client.get(deduplication_flags_url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data == {
        "can_run_deduplication": False,
        "is_deduplication_disabled": True,
    }
