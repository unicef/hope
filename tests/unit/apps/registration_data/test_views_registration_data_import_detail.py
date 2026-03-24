"""Tests for registration data import detail view."""

from typing import Any, Callable

import freezegun
import pytest
from rest_framework import status
from rest_framework.reverse import reverse

from extras.test_utils.factories import (
    BusinessAreaFactory,
    HouseholdFactory,
    IndividualFactory,
    PartnerFactory,
    ProgramFactory,
    RegistrationDataImportFactory,
    UserFactory,
)
from hope.apps.account.permissions import Permissions
from hope.models import BusinessArea, Partner, Program, RegistrationDataImport, User

pytestmark = pytest.mark.django_db


@pytest.fixture
def afghanistan() -> BusinessArea:
    return BusinessAreaFactory(name="Afghanistan", slug="afghanistan")


@pytest.fixture
def partner() -> Partner:
    return PartnerFactory(name="TestPartner")


@pytest.fixture
def user(partner: Partner) -> User:
    return UserFactory(partner=partner)


@pytest.fixture
def program1(afghanistan: BusinessArea) -> Program:
    return ProgramFactory(
        business_area=afghanistan,
        name="Program1",
        biometric_deduplication_enabled=True,
    )


@pytest.fixture
@freezegun.freeze_time("2022-01-01")
def rdi1(afghanistan: BusinessArea, program1: Program) -> RegistrationDataImport:
    return RegistrationDataImportFactory(
        business_area=afghanistan,
        program=program1,
        status=RegistrationDataImport.IMPORTING,
        name="RDI A 1",
    )


@pytest.fixture
def url_detail(afghanistan: BusinessArea, program1: Program, rdi1: RegistrationDataImport) -> str:
    return reverse(
        "api:registration-data:registration-data-imports-detail",
        kwargs={
            "business_area_slug": afghanistan.slug,
            "program_slug": program1.slug,
            "pk": rdi1.id,
        },
    )


@pytest.fixture
def authenticated_client(api_client: Callable, user: User) -> Any:
    return api_client(user)


@freezegun.freeze_time("2022-01-01")
def test_get_registration_data_import_detail_without_permission(
    authenticated_client: Any,
    afghanistan: BusinessArea,
    user: User,
    program1: Program,
    rdi1: RegistrationDataImport,
    url_detail: str,
) -> None:
    response = authenticated_client.get(url_detail)
    assert response.status_code == status.HTTP_403_FORBIDDEN


@freezegun.freeze_time("2022-01-01")
def test_get_registration_data_import_detail_with_permission(
    authenticated_client: Any,
    afghanistan: BusinessArea,
    user: User,
    program1: Program,
    rdi1: RegistrationDataImport,
    url_detail: str,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.RDI_VIEW_DETAILS],
        afghanistan,
        program1,
    )

    individual = IndividualFactory(
        household=None,
        program=program1,
        business_area=afghanistan,
        registration_data_import=rdi1,
        phone_no="+48 123456789",  # valid phone number
    )

    household = HouseholdFactory(
        program=program1,
        business_area=afghanistan,
        registration_data_import=rdi1,
        head_of_household=individual,
    )

    individual.household = household
    individual.save()

    response = authenticated_client.get(url_detail)
    assert response.status_code == status.HTTP_200_OK

    response_json = response.json()
    assert response_json["id"] == str(rdi1.id)
    assert response_json["name"] == rdi1.name
    assert response_json["status"] == rdi1.status
    assert response_json["imported_by"] == rdi1.imported_by.get_full_name()
    assert response_json["data_source"] == rdi1.get_data_source_display()
    assert response_json["created_at"] == "2022-01-01T00:00:00Z"
    assert response_json["erased"] is False
    assert response_json["import_date"] == "2022-01-01T00:00:00Z"
    assert response_json["total_households_count_with_valid_phone_no"] == 1
    assert response_json["number_of_registered_individuals"] == 1


@freezegun.freeze_time("2022-01-01")
def test_get_registration_data_import_detail_with_deduplication_statistics(
    authenticated_client: Any,
    afghanistan: BusinessArea,
    user: User,
    program1: Program,
    create_user_role_with_permissions: Callable,
) -> None:
    """Test RDI detail view returns correct deduplication statistics and percentages."""
    create_user_role_with_permissions(
        user,
        [Permissions.RDI_VIEW_DETAILS],
        afghanistan,
        program1,
    )

    rdi = RegistrationDataImportFactory(
        business_area=afghanistan,
        program=program1,
        status=RegistrationDataImport.IN_REVIEW,
        name="Test RDI",
        data_source=RegistrationDataImport.XLS,
        imported_by=user,
        number_of_households=10,
        number_of_individuals=50,
        batch_duplicates=5,
        batch_unique=45,
        golden_record_duplicates=3,
        golden_record_possible_duplicates=2,
        golden_record_unique=45,
        dedup_engine_batch_duplicates=4,
        dedup_engine_golden_record_duplicates=3,
    )

    url_detail = reverse(
        "api:registration-data:registration-data-imports-detail",
        kwargs={
            "business_area_slug": afghanistan.slug,
            "program_slug": program1.slug,
            "pk": rdi.id,
        },
    )

    response = authenticated_client.get(url_detail)
    assert response.status_code == status.HTTP_200_OK

    response_json = response.json()
    assert response_json["name"] == rdi.name
    assert response_json["id"] == str(rdi.id)
    assert response_json["status_display"] == "In Review"
    assert response_json["data_source"] == "Excel"
    assert response_json["imported_by"] == user.get_full_name()

    batch_duplicates = response_json["batch_duplicates_count_and_percentage"]
    assert len(batch_duplicates) == 2
    assert batch_duplicates[0]["count"] == 5
    assert round(batch_duplicates[0]["percentage"]) == 10
    assert batch_duplicates[1]["count"] == 4
    assert round(batch_duplicates[1]["percentage"]) == 8

    batch_unique = response_json["batch_unique_count_and_percentage"]
    assert len(batch_unique) == 2
    assert batch_unique[0]["count"] == 45
    assert round(batch_unique[0]["percentage"]) == 90
    assert batch_unique[1]["count"] == 46
    assert round(batch_unique[1]["percentage"]) == 92

    gr_duplicates = response_json["golden_record_duplicates_count_and_percentage"]
    assert gr_duplicates[0]["count"] == 3
    assert round(gr_duplicates[0]["percentage"]) == 6

    gr_possible_duplicates = response_json["golden_record_possible_duplicates_count_and_percentage"]
    assert len(gr_possible_duplicates) == 2
    assert gr_possible_duplicates[0]["count"] == 2
    assert round(gr_possible_duplicates[0]["percentage"]) == 4
    assert gr_possible_duplicates[1]["count"] == 3
    assert round(gr_possible_duplicates[1]["percentage"]) == 6

    gr_unique = response_json["golden_record_unique_count_and_percentage"]
    assert len(gr_unique) == 2
    assert gr_unique[0]["count"] == 45
    assert round(gr_unique[0]["percentage"]) == 90
    assert gr_unique[1]["count"] == 47
    assert round(gr_unique[1]["percentage"]) == 94
