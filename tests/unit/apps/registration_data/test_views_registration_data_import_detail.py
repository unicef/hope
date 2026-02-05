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
    return ProgramFactory(business_area=afghanistan, name="Program1")


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
