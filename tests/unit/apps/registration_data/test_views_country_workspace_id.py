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
def afghanistan() -> BusinessArea:
    return BusinessAreaFactory(name="Afghanistan", slug="afghanistan")


@pytest.fixture
def partner() -> Partner:
    return PartnerFactory(name="TestPartner")


@pytest.fixture
def user(partner: Partner) -> User:
    return UserFactory(partner=partner)


@pytest.fixture
def program(afghanistan: BusinessArea) -> Program:
    return ProgramFactory(business_area=afghanistan, name="ProgramCW")


@pytest.fixture
def rdi_cw(afghanistan: BusinessArea, program: Program) -> RegistrationDataImport:
    return RegistrationDataImportFactory(
        business_area=afghanistan,
        program=program,
        status=RegistrationDataImport.IN_REVIEW,
        name="CW RDI",
        country_workspace_id="cw-corr-detail-1",
    )


@pytest.fixture
def rdi_legacy(afghanistan: BusinessArea, program: Program) -> RegistrationDataImport:
    return RegistrationDataImportFactory(
        business_area=afghanistan,
        program=program,
        status=RegistrationDataImport.IN_REVIEW,
        name="Legacy RDI",
        country_workspace_id=None,
    )


@pytest.fixture
def authenticated_client(
    api_client: Callable,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    create_user_role_with_permissions: Callable,
) -> Any:
    create_user_role_with_permissions(
        user,
        [Permissions.RDI_VIEW_LIST, Permissions.RDI_VIEW_DETAILS],
        afghanistan,
        program,
    )
    return api_client(user)


@pytest.fixture
def url_list(afghanistan: BusinessArea, program: Program) -> str:
    return reverse(
        "api:registration-data:registration-data-imports-list",
        kwargs={"business_area_slug": afghanistan.slug, "program_code": program.code},
    )


@pytest.fixture
def url_detail_cw(afghanistan: BusinessArea, program: Program, rdi_cw: RegistrationDataImport) -> str:
    return reverse(
        "api:registration-data:registration-data-imports-detail",
        kwargs={"business_area_slug": afghanistan.slug, "program_code": program.code, "pk": rdi_cw.id},
    )


@pytest.fixture
def url_detail_legacy(afghanistan: BusinessArea, program: Program, rdi_legacy: RegistrationDataImport) -> str:
    return reverse(
        "api:registration-data:registration-data-imports-detail",
        kwargs={"business_area_slug": afghanistan.slug, "program_code": program.code, "pk": rdi_legacy.id},
    )


def test_detail_response_correlation_id_sourced_from_country_workspace_id(
    authenticated_client: Any,
    rdi_cw: RegistrationDataImport,
    url_detail_cw: str,
) -> None:
    response = authenticated_client.get(url_detail_cw)

    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert "correlation_id" in body
    assert body["correlation_id"] == "cw-corr-detail-1"


def test_detail_response_correlation_id_null_when_no_country_workspace_id(
    authenticated_client: Any,
    rdi_legacy: RegistrationDataImport,
    url_detail_legacy: str,
) -> None:
    response = authenticated_client.get(url_detail_legacy)

    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert "correlation_id" in body
    assert body["correlation_id"] is None


def test_list_response_correlation_id_sourced_from_country_workspace_id(
    authenticated_client: Any,
    rdi_cw: RegistrationDataImport,
    rdi_legacy: RegistrationDataImport,
    url_list: str,
) -> None:
    response = authenticated_client.get(url_list)

    assert response.status_code == status.HTTP_200_OK
    by_id = {row["id"]: row for row in response.json()["results"]}
    assert "correlation_id" in by_id[str(rdi_cw.id)]
    assert by_id[str(rdi_cw.id)]["correlation_id"] == "cw-corr-detail-1"
    assert by_id[str(rdi_legacy.id)]["correlation_id"] is None
