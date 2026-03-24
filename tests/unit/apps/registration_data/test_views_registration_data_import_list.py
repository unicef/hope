"""Tests for registration data import views."""

import json
from typing import Any, Callable

from django.core.cache import cache
from django.db import connection
from django.test.utils import CaptureQueriesContext
import freezegun
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
def program1(afghanistan: BusinessArea) -> Program:
    return ProgramFactory(business_area=afghanistan, name="Program1")


@pytest.fixture
def program2(afghanistan: BusinessArea) -> Program:
    return ProgramFactory(business_area=afghanistan, name="Program2")


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
@freezegun.freeze_time("2022-01-01")
def rdi2(afghanistan: BusinessArea, program1: Program) -> RegistrationDataImport:
    return RegistrationDataImportFactory(
        business_area=afghanistan,
        program=program1,
        status=RegistrationDataImport.IN_REVIEW,
        name="RDI A 2",
    )


@pytest.fixture
@freezegun.freeze_time("2022-01-01")
def rdi3(afghanistan: BusinessArea, program1: Program) -> RegistrationDataImport:
    return RegistrationDataImportFactory(
        business_area=afghanistan,
        program=program1,
        status=RegistrationDataImport.MERGED,
        name="RDI B 1",
    )


@pytest.fixture
@freezegun.freeze_time("2022-01-01")
def rdi_program2(afghanistan: BusinessArea, program2: Program) -> RegistrationDataImport:
    return RegistrationDataImportFactory(
        business_area=afghanistan,
        program=program2,
        status=RegistrationDataImport.MERGED,
        name="RDI Program 2",
    )


@pytest.fixture
def url_list(afghanistan: BusinessArea, program1: Program) -> str:
    return reverse(
        "api:registration-data:registration-data-imports-list",
        kwargs={
            "business_area_slug": afghanistan.slug,
            "program_slug": program1.slug,
        },
    )


@pytest.fixture
def authenticated_client(api_client: Callable, user: User) -> Any:
    return api_client(user)


@freezegun.freeze_time("2022-01-01")
@pytest.mark.parametrize(
    (
        "user_permissions",
        "partner_permissions",
        "is_permission_in_correct_program",
        "expected_status",
    ),
    [
        ([], [], True, status.HTTP_403_FORBIDDEN),
        ([Permissions.RDI_VIEW_LIST], [], True, status.HTTP_200_OK),
        ([], [Permissions.RDI_VIEW_LIST], True, status.HTTP_200_OK),
        (
            [Permissions.RDI_VIEW_LIST],
            [Permissions.RDI_VIEW_LIST],
            True,
            status.HTTP_200_OK,
        ),
        ([], [], False, status.HTTP_403_FORBIDDEN),
        ([Permissions.RDI_VIEW_LIST], [], False, status.HTTP_403_FORBIDDEN),
        ([], [Permissions.RDI_VIEW_LIST], False, status.HTTP_403_FORBIDDEN),
        (
            [Permissions.RDI_VIEW_LIST],
            [Permissions.RDI_VIEW_LIST],
            False,
            status.HTTP_403_FORBIDDEN,
        ),
    ],
)
def test_list_registration_data_imports_permission(
    user_permissions: list,
    partner_permissions: list,
    is_permission_in_correct_program: bool,
    expected_status: int,
    authenticated_client: Any,
    afghanistan: BusinessArea,
    partner: Partner,
    user: User,
    program1: Program,
    rdi1: RegistrationDataImport,
    rdi2: RegistrationDataImport,
    rdi3: RegistrationDataImport,
    rdi_program2: RegistrationDataImport,
    url_list: str,
    create_user_role_with_permissions: Callable,
    create_partner_role_with_permissions: Callable,
) -> None:
    if is_permission_in_correct_program:
        create_user_role_with_permissions(user, user_permissions, afghanistan, program1)
        create_partner_role_with_permissions(partner, partner_permissions, afghanistan, program1)
    else:
        # role will be created for different program
        create_user_role_with_permissions(user, user_permissions, afghanistan)
        create_partner_role_with_permissions(partner, partner_permissions, afghanistan)

    response = authenticated_client.get(url_list)
    assert response.status_code == expected_status


@freezegun.freeze_time("2022-01-01")
def test_list_registration_data_imports(
    authenticated_client: Any,
    afghanistan: BusinessArea,
    user: User,
    program1: Program,
    rdi1: RegistrationDataImport,
    rdi2: RegistrationDataImport,
    rdi3: RegistrationDataImport,
    rdi_program2: RegistrationDataImport,
    url_list: str,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.RDI_VIEW_LIST],
        afghanistan,
        program1,
    )
    response = authenticated_client.get(url_list)
    assert response.status_code == status.HTTP_200_OK

    response_json = response.json()["results"]
    assert len(response_json) == 3

    assert {
        "id": str(rdi1.id),
        "name": rdi1.name,
        "status": rdi1.get_status_display(),
        "imported_by": rdi1.imported_by.get_full_name(),
        "data_source": rdi1.get_data_source_display(),
        "created_at": "2022-01-01T00:00:00Z",
        "erased": rdi1.erased,
        "import_date": "2022-01-01T00:00:00Z",
        "number_of_households": rdi1.number_of_households,
        "number_of_individuals": rdi1.number_of_individuals,
        "biometric_deduplicated": rdi1.biometric_deduplicated,
    } in response_json
    assert {
        "id": str(rdi2.id),
        "name": rdi2.name,
        "status": rdi2.get_status_display(),
        "imported_by": rdi2.imported_by.get_full_name(),
        "data_source": rdi2.get_data_source_display(),
        "created_at": "2022-01-01T00:00:00Z",
        "erased": rdi2.erased,
        "import_date": "2022-01-01T00:00:00Z",
        "number_of_households": rdi2.number_of_households,
        "number_of_individuals": rdi2.number_of_individuals,
        "biometric_deduplicated": rdi2.biometric_deduplicated,
    } in response_json
    assert {
        "id": str(rdi3.id),
        "name": rdi3.name,
        "status": rdi3.get_status_display(),
        "imported_by": rdi3.imported_by.get_full_name(),
        "data_source": rdi3.get_data_source_display(),
        "created_at": "2022-01-01T00:00:00Z",
        "erased": rdi3.erased,
        "import_date": "2022-01-01T00:00:00Z",
        "number_of_households": rdi3.number_of_households,
        "number_of_individuals": rdi3.number_of_individuals,
        "biometric_deduplicated": rdi3.biometric_deduplicated,
    } in response_json
    assert {
        "id": str(rdi_program2.id),
        "name": rdi_program2.name,
        "status": rdi1.get_status_display(),
        "imported_by": rdi1.imported_by.get_full_name(),
        "data_source": rdi1.get_data_source_display(),
        "created_at": "2022-01-01T00:00:00Z",
        "erased": rdi1.erased,
        "import_date": "2022-01-01T00:00:00Z",
        "number_of_households": rdi1.number_of_households,
        "number_of_individuals": rdi1.number_of_individuals,
        "biometric_deduplicated": rdi1.biometric_deduplicated,
    } not in response_json


@freezegun.freeze_time("2022-01-01")
def test_list_registration_data_imports_filter(
    authenticated_client: Any,
    afghanistan: BusinessArea,
    user: User,
    program1: Program,
    rdi1: RegistrationDataImport,
    rdi2: RegistrationDataImport,
    rdi3: RegistrationDataImport,
    rdi_program2: RegistrationDataImport,
    url_list: str,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.RDI_VIEW_LIST],
        afghanistan,
        program1,
    )
    response = authenticated_client.get(url_list, {"status": RegistrationDataImport.MERGED})
    assert response.status_code == status.HTTP_200_OK

    response_json = response.json()["results"]
    assert len(response_json) == 1


@freezegun.freeze_time("2022-01-01")
def test_list_registration_data_imports_search_by_name(
    authenticated_client: Any,
    afghanistan: BusinessArea,
    user: User,
    program1: Program,
    rdi1: RegistrationDataImport,
    rdi2: RegistrationDataImport,
    rdi3: RegistrationDataImport,
    rdi_program2: RegistrationDataImport,
    url_list: str,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.RDI_VIEW_LIST],
        afghanistan,
        program1,
    )
    response = authenticated_client.get(url_list, {"search": "RDI A"})
    assert response.status_code == status.HTTP_200_OK

    response_json = response.json()["results"]
    assert len(response_json) == 2


@freezegun.freeze_time("2022-01-01")
def test_list_registration_data_imports_caching(
    authenticated_client: Any,
    afghanistan: BusinessArea,
    user: User,
    program1: Program,
    rdi1: RegistrationDataImport,
    rdi2: RegistrationDataImport,
    rdi3: RegistrationDataImport,
    rdi_program2: RegistrationDataImport,
    url_list: str,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.RDI_VIEW_LIST],
        afghanistan,
        program1,
    )
    with CaptureQueriesContext(connection) as ctx:
        response = authenticated_client.get(url_list)
        assert response.status_code == status.HTTP_200_OK

        etag = response.headers["etag"]
        assert json.loads(cache.get(etag)[0].decode("utf8")) == response.json()
        assert len(ctx.captured_queries) == 16

    # Test that reoccurring requests use cached data
    with CaptureQueriesContext(connection) as ctx:
        response = authenticated_client.get(url_list)
        assert response.status_code == status.HTTP_200_OK

        etag_second_call = response.headers["etag"]
        assert json.loads(cache.get(response.headers["etag"])[0].decode("utf8")) == response.json()
        assert len(ctx.captured_queries) == 4

        assert etag_second_call == etag

    # After update, it does not use the cached data
    rdi1.status = RegistrationDataImport.MERGE_ERROR
    rdi1.save()
    with CaptureQueriesContext(connection) as ctx:
        response = authenticated_client.get(url_list)
        assert response.status_code == status.HTTP_200_OK

        etag_call_after_update = response.headers["etag"]
        assert json.loads(cache.get(response.headers["etag"])[0].decode("utf8")) == response.json()
        assert len(ctx.captured_queries) == 10  # less than the first call because of cached permissions

        assert etag_call_after_update != etag

    # Cached data again
    with CaptureQueriesContext(connection) as ctx:
        response = authenticated_client.get(url_list)
        assert response.status_code == status.HTTP_200_OK

        etag_call_after_update_second_call = response.headers["etag"]
        assert json.loads(cache.get(response.headers["etag"])[0].decode("utf8")) == response.json()
        assert len(ctx.captured_queries) == 4

        assert etag_call_after_update_second_call == etag_call_after_update
