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
    HouseholdFactory,
    PartnerFactory,
    ProgramFactory,
    RegistrationDataImportFactory,
    UserFactory,
)
from hope.apps.account.permissions import Permissions
from hope.models import RegistrationDataImport

pytestmark = pytest.mark.django_db


@pytest.fixture
def registration_data_import_context(api_client: Any) -> Callable[[], dict[str, Any]]:
    def _make() -> dict[str, Any]:
        partner = PartnerFactory(name="TestPartner")
        user = UserFactory(partner=partner)
        client = api_client(user)
        afghanistan = BusinessAreaFactory(slug="afghanistan", name="Afghanistan")
        program1 = ProgramFactory(business_area=afghanistan, name="Program1")
        program2 = ProgramFactory(business_area=afghanistan, name="Program2")

        rdi1 = RegistrationDataImportFactory(
            business_area=afghanistan,
            program=program1,
            status=RegistrationDataImport.IMPORTING,
            name="RDI A 1",
            imported_by=user,
        )
        rdi2 = RegistrationDataImportFactory(
            business_area=afghanistan,
            program=program1,
            status=RegistrationDataImport.IN_REVIEW,
            name="RDI A 2",
            imported_by=user,
        )
        rdi3 = RegistrationDataImportFactory(
            business_area=afghanistan,
            program=program1,
            status=RegistrationDataImport.MERGED,
            name="RDI B 1",
            imported_by=user,
        )
        rdi_program2 = RegistrationDataImportFactory(
            business_area=afghanistan,
            program=program2,
            status=RegistrationDataImport.MERGED,
            name="RDI Program 2",
            imported_by=user,
        )

        url_list = reverse(
            "api:registration-data:registration-data-imports-list",
            kwargs={
                "business_area_slug": afghanistan.slug,
                "program_slug": program1.slug,
            },
        )
        url_detail = reverse(
            "api:registration-data:registration-data-imports-detail",
            kwargs={
                "business_area_slug": afghanistan.slug,
                "program_slug": program1.slug,
                "pk": rdi1.id,
            },
        )

        return {
            "partner": partner,
            "user": user,
            "client": client,
            "afghanistan": afghanistan,
            "program1": program1,
            "program2": program2,
            "rdi1": rdi1,
            "rdi2": rdi2,
            "rdi3": rdi3,
            "rdi_program2": rdi_program2,
            "url_list": url_list,
            "url_detail": url_detail,
        }

    return _make


@pytest.mark.parametrize(
    ("user_permissions", "partner_permissions", "expected_status"),
    [
        ([], [], status.HTTP_403_FORBIDDEN),
        ([Permissions.RDI_VIEW_LIST], [], status.HTTP_200_OK),
        ([], [Permissions.RDI_VIEW_LIST], status.HTTP_200_OK),
        ([Permissions.RDI_VIEW_LIST], [Permissions.RDI_VIEW_LIST], status.HTTP_200_OK),
    ],
)
def test_list_registration_data_imports_permission_in_program(
    user_permissions: list,
    partner_permissions: list,
    expected_status: str,
    registration_data_import_context: Callable[[], dict[str, Any]],
    create_user_role_with_permissions: Any,
    create_partner_role_with_permissions: Any,
) -> None:
    with freezegun.freeze_time("2022-01-01"):
        context = registration_data_import_context()
        create_user_role_with_permissions(
            context["user"],
            user_permissions,
            context["afghanistan"],
            context["program1"],
        )
        create_partner_role_with_permissions(
            context["partner"],
            partner_permissions,
            context["afghanistan"],
            context["program1"],
        )

        response = context["client"].get(context["url_list"])
        assert response.status_code == expected_status


@pytest.mark.parametrize(
    ("user_permissions", "partner_permissions"),
    [
        ([], []),
        ([Permissions.RDI_VIEW_LIST], []),
        ([], [Permissions.RDI_VIEW_LIST]),
        ([Permissions.RDI_VIEW_LIST], [Permissions.RDI_VIEW_LIST]),
    ],
)
def test_list_registration_data_imports_permission_wrong_program(
    user_permissions: list,
    partner_permissions: list,
    registration_data_import_context: Callable[[], dict[str, Any]],
    create_user_role_with_permissions: Any,
    create_partner_role_with_permissions: Any,
) -> None:
    with freezegun.freeze_time("2022-01-01"):
        context = registration_data_import_context()
        create_user_role_with_permissions(
            context["user"],
            user_permissions,
            context["afghanistan"],
            context["program2"],
        )
        create_partner_role_with_permissions(
            context["partner"],
            partner_permissions,
            context["afghanistan"],
            context["program2"],
        )

        response = context["client"].get(context["url_list"])
        assert response.status_code == status.HTTP_403_FORBIDDEN


def test_list_registration_data_imports(
    registration_data_import_context: Callable[[], dict[str, Any]],
    create_user_role_with_permissions: Any,
) -> None:
    with freezegun.freeze_time("2022-01-01"):
        context = registration_data_import_context()
        create_user_role_with_permissions(
            context["user"],
            [Permissions.RDI_VIEW_LIST],
            context["afghanistan"],
            context["program1"],
        )
        response = context["client"].get(context["url_list"])
        assert response.status_code == status.HTTP_200_OK

        response_json = response.json()["results"]
        assert len(response_json) == 3

        rdi1 = context["rdi1"]
        rdi2 = context["rdi2"]
        rdi3 = context["rdi3"]
        rdi_program2 = context["rdi_program2"]

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


def test_list_registration_data_imports_filter(
    registration_data_import_context: Callable[[], dict[str, Any]],
    create_user_role_with_permissions: Any,
) -> None:
    with freezegun.freeze_time("2022-01-01"):
        context = registration_data_import_context()
        create_user_role_with_permissions(
            context["user"],
            [Permissions.RDI_VIEW_LIST],
            context["afghanistan"],
            context["program1"],
        )
        response = context["client"].get(
            context["url_list"],
            {"status": RegistrationDataImport.MERGED},
        )
        assert response.status_code == status.HTTP_200_OK

        response_json = response.json()["results"]
        assert len(response_json) == 1


def test_list_registration_data_imports_search_by_name(
    registration_data_import_context: Callable[[], dict[str, Any]],
    create_user_role_with_permissions: Any,
) -> None:
    with freezegun.freeze_time("2022-01-01"):
        context = registration_data_import_context()
        create_user_role_with_permissions(
            context["user"],
            [Permissions.RDI_VIEW_LIST],
            context["afghanistan"],
            context["program1"],
        )
        response = context["client"].get(
            context["url_list"],
            {"search": "RDI A"},
        )
        assert response.status_code == status.HTTP_200_OK

        response_json = response.json()["results"]
        assert len(response_json) == 2


def test_list_registration_data_imports_caching(
    registration_data_import_context: Callable[[], dict[str, Any]],
    create_user_role_with_permissions: Any,
) -> None:
    with freezegun.freeze_time("2022-01-01"):
        context = registration_data_import_context()
        create_user_role_with_permissions(
            context["user"],
            [Permissions.RDI_VIEW_LIST],
            context["afghanistan"],
            context["program1"],
        )
        with CaptureQueriesContext(connection) as ctx:
            response = context["client"].get(context["url_list"])
            assert response.status_code == status.HTTP_200_OK

            etag = response.headers["etag"]
            assert json.loads(cache.get(etag)[0].decode("utf8")) == response.json()
            assert len(ctx.captured_queries) == 16

        with CaptureQueriesContext(connection) as ctx:
            response = context["client"].get(context["url_list"])
            assert response.status_code == status.HTTP_200_OK

            etag_second_call = response.headers["etag"]
            assert json.loads(cache.get(response.headers["etag"])[0].decode("utf8")) == response.json()
            assert len(ctx.captured_queries) == 4
            assert etag_second_call == etag

        context["rdi1"].status = RegistrationDataImport.MERGE_ERROR
        context["rdi1"].save(update_fields=["status"])
        with CaptureQueriesContext(connection) as ctx:
            response = context["client"].get(context["url_list"])
            assert response.status_code == status.HTTP_200_OK

            etag_call_after_update = response.headers["etag"]
            assert json.loads(cache.get(response.headers["etag"])[0].decode("utf8")) == response.json()
            assert len(ctx.captured_queries) == 10
            assert etag_call_after_update != etag

        with CaptureQueriesContext(connection) as ctx:
            response = context["client"].get(context["url_list"])
            assert response.status_code == status.HTTP_200_OK

            etag_call_after_update_second_call = response.headers["etag"]
            assert json.loads(cache.get(response.headers["etag"])[0].decode("utf8")) == response.json()
            assert len(ctx.captured_queries) == 4
            assert etag_call_after_update_second_call == etag_call_after_update


def test_get_registration_data_import_detail(
    registration_data_import_context: Callable[[], dict[str, Any]],
    create_user_role_with_permissions: Any,
) -> None:
    with freezegun.freeze_time("2022-01-01"):
        context = registration_data_import_context()
        create_user_role_with_permissions(
            context["user"],
            [Permissions.RDI_VIEW_DETAILS],
            context["afghanistan"],
            context["program1"],
        )
        household = HouseholdFactory(
            program=context["program1"],
            business_area=context["afghanistan"],
            registration_data_import=context["rdi1"],
            create_role=False,
        )
        individual = household.head_of_household
        individual.phone_no_valid = True
        individual.save(update_fields=["phone_no_valid"])
        response = context["client"].get(context["url_detail"])
        assert response.status_code == status.HTTP_200_OK

        response_json = response.json()
        rdi1 = context["rdi1"]
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
