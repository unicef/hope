"""Tests for periodic data update XLSX upload views."""

from io import BytesIO
import json
from typing import Any, Callable

from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import connection
from django.test.utils import CaptureQueriesContext
from flaky import flaky
import freezegun
import openpyxl
import pytest
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from extras.test_utils.factories import (
    BusinessAreaFactory,
    FlexibleAttributeForPDUFactory,
    HouseholdFactory,
    IndividualFactory,
    PartnerFactory,
    PDUXlsxTemplateFactory,
    PDUXlsxUploadFactory,
    PeriodicFieldDataFactory,
    ProgramFactory,
    UserFactory,
)
from hope.apps.account.permissions import Permissions
from hope.apps.periodic_data_update.service.periodic_data_update_export_template_service import (
    PDUXlsxExportTemplateService,
)
from hope.apps.periodic_data_update.utils import populate_pdu_with_null_values
from hope.models import BusinessArea, Partner, PeriodicFieldData, Program, User

pytestmark = pytest.mark.django_db


def add_pdu_data_to_xlsx(periodic_data_update_template: Any, rows: list[list[Any]]) -> BytesIO:
    wb = openpyxl.load_workbook(periodic_data_update_template.file.file)
    ws_pdu = wb[PDUXlsxExportTemplateService.PDU_SHEET]
    for row_index, row in enumerate(rows):
        for col_index, value in enumerate(row):
            ws_pdu.cell(row=row_index + 2, column=col_index + 7, value=value)
    tmp_file = BytesIO()
    wb.save(tmp_file)
    tmp_file.seek(0)
    return tmp_file


@pytest.fixture
def business_area(db: Any) -> BusinessArea:
    return BusinessAreaFactory(slug="afghanistan", name="Afghanistan")


@pytest.fixture
def partner(db: Any) -> Partner:
    return PartnerFactory(name="TestPartner")


@pytest.fixture
def user(partner: Partner) -> User:
    return UserFactory(partner=partner)


@pytest.fixture
def authenticated_client(api_client: Callable, user: User) -> Any:
    return api_client(user)


@pytest.fixture
def program1(business_area: BusinessArea) -> Program:
    return ProgramFactory(business_area=business_area, name="Program1")


@pytest.fixture
def program2(business_area: BusinessArea) -> Program:
    return ProgramFactory(business_area=business_area, name="Program2")


@pytest.fixture
def pdu_upload1_program1(program1: Program, user: User) -> Any:
    pdu_template1_program1 = PDUXlsxTemplateFactory(program=program1)
    return PDUXlsxUploadFactory(template=pdu_template1_program1, created_by=user)


@pytest.fixture
def pdu_upload2_program1(program1: Program, user: User) -> Any:
    pdu_template2_program1 = PDUXlsxTemplateFactory(program=program1)
    return PDUXlsxUploadFactory(template=pdu_template2_program1, created_by=user)


@pytest.fixture
def pdu_upload_program2(program2: Program, user: User) -> Any:
    pdu_template_program2 = PDUXlsxTemplateFactory(program=program2)
    return PDUXlsxUploadFactory(template=pdu_template_program2, created_by=user)


@pytest.fixture
def url_list(business_area: BusinessArea, program1: Program) -> str:
    return reverse(
        "api:periodic-data-update:periodic-data-update-uploads-list",
        kwargs={
            "business_area_slug": business_area.slug,
            "program_slug": program1.slug,
        },
    )


@pytest.fixture
def url_count(business_area: BusinessArea, program1: Program) -> str:
    return reverse(
        "api:periodic-data-update:periodic-data-update-uploads-count",
        kwargs={
            "business_area_slug": business_area.slug,
            "program_slug": program1.slug,
        },
    )


@pytest.fixture
def url_upload(business_area: BusinessArea, program1: Program) -> str:
    return reverse(
        "api:periodic-data-update:periodic-data-update-uploads-upload",
        kwargs={
            "business_area_slug": business_area.slug,
            "program_slug": program1.slug,
        },
    )


@freezegun.freeze_time("2022-01-01")
@flaky(max_runs=3, min_passes=1)
@pytest.mark.parametrize(
    ("permissions", "partner_permissions", "access_to_program", "expected_status"),
    [
        ([], [], True, status.HTTP_403_FORBIDDEN),
        ([Permissions.PDU_VIEW_LIST_AND_DETAILS], [], True, status.HTTP_200_OK),
        ([], [Permissions.PDU_VIEW_LIST_AND_DETAILS], True, status.HTTP_200_OK),
        (
            [Permissions.PDU_VIEW_LIST_AND_DETAILS],
            [Permissions.PDU_VIEW_LIST_AND_DETAILS],
            True,
            status.HTTP_200_OK,
        ),
        ([], [], False, status.HTTP_403_FORBIDDEN),
        ([Permissions.PDU_VIEW_LIST_AND_DETAILS], [], False, status.HTTP_403_FORBIDDEN),
        ([], [Permissions.PDU_VIEW_LIST_AND_DETAILS], False, status.HTTP_403_FORBIDDEN),
        (
            [Permissions.PDU_VIEW_LIST_AND_DETAILS],
            [Permissions.PDU_VIEW_LIST_AND_DETAILS],
            False,
            status.HTTP_403_FORBIDDEN,
        ),
    ],
)
def test_list_periodic_data_update_uploads_permission(
    permissions: list,
    partner_permissions: list,
    access_to_program: bool,
    expected_status: int,
    authenticated_client: APIClient,
    user: User,
    partner: Partner,
    business_area: BusinessArea,
    program1: Program,
    pdu_upload1_program1: Any,
    pdu_upload2_program1: Any,
    url_list: str,
    create_user_role_with_permissions: Callable,
    create_partner_role_with_permissions: Callable,
) -> None:
    if access_to_program:
        create_user_role_with_permissions(user, permissions, business_area, program1)
        create_partner_role_with_permissions(partner, partner_permissions, business_area, program1)
    else:
        create_user_role_with_permissions(user, permissions, business_area)
        create_partner_role_with_permissions(partner, partner_permissions, business_area)

    response = authenticated_client.get(url_list)
    assert response.status_code == expected_status


@freezegun.freeze_time("2022-01-01")
def test_list_periodic_data_update_uploads(
    authenticated_client: APIClient,
    user: User,
    business_area: BusinessArea,
    program1: Program,
    pdu_upload1_program1: Any,
    pdu_upload2_program1: Any,
    pdu_upload_program2: Any,
    url_list: str,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.PDU_VIEW_LIST_AND_DETAILS],
        business_area,
        program1,
    )

    response = authenticated_client.get(url_list)
    assert response.status_code == status.HTTP_200_OK

    response_json = response.json()["results"]
    assert len(response_json) == 2
    assert {
        "id": pdu_upload1_program1.id,
        "status_display": pdu_upload1_program1.combined_status_display,
        "status": pdu_upload1_program1.combined_status,
        "template": pdu_upload1_program1.template.id,
        "created_at": pdu_upload1_program1.created_at.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "created_by": pdu_upload1_program1.created_by.get_full_name(),
    } in response_json
    assert {
        "id": pdu_upload2_program1.id,
        "status_display": pdu_upload2_program1.combined_status_display,
        "status": pdu_upload2_program1.combined_status,
        "template": pdu_upload2_program1.template.id,
        "created_at": pdu_upload2_program1.created_at.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "created_by": pdu_upload2_program1.created_by.get_full_name(),
    } in response_json

    assert {
        "id": pdu_upload_program2.id,
        "status_display": pdu_upload_program2.combined_status_display,
        "status": pdu_upload_program2.combined_status,
        "template": pdu_upload_program2.template.id,
        "created_at": pdu_upload_program2.created_at.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "created_by": pdu_upload_program2.created_by.get_full_name(),
    } not in response_json


@freezegun.freeze_time("2022-01-01")
@pytest.mark.skip(reason="Caching is disabled for now")
def test_list_periodic_data_update_uploads_caching(
    authenticated_client: APIClient,
    user: User,
    business_area: BusinessArea,
    program1: Program,
    pdu_upload1_program1: Any,
    pdu_upload2_program1: Any,
    pdu_upload_program2: Any,
    url_list: str,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.PDU_VIEW_LIST_AND_DETAILS],
        business_area,
        program1,
    )

    with CaptureQueriesContext(connection) as ctx:
        response = authenticated_client.get(url_list)
        assert response.status_code == status.HTTP_200_OK

        etag = response.headers["etag"]
        assert json.loads(cache.get(etag)[0].decode("utf8")) == response.json()
        assert len(ctx.captured_queries) == 11

    # Test that reoccurring requests use cached data
    with CaptureQueriesContext(connection) as ctx:
        response = authenticated_client.get(url_list)
        assert response.status_code == status.HTTP_200_OK

        etag_second_call = response.headers["etag"]
        assert json.loads(cache.get(response.headers["etag"])[0].decode("utf8")) == response.json()
        assert len(ctx.captured_queries) == 5

        assert etag_second_call == etag


@freezegun.freeze_time("2022-01-01")
def test_count_periodic_data_update_uploads(
    authenticated_client: APIClient,
    user: User,
    business_area: BusinessArea,
    program1: Program,
    pdu_upload1_program1: Any,
    pdu_upload2_program1: Any,
    url_count: str,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.PDU_VIEW_LIST_AND_DETAILS],
        business_area,
        program1,
    )

    response = authenticated_client.get(url_count)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["count"] == 2


@freezegun.freeze_time("2022-01-01")
@pytest.mark.parametrize(
    ("permissions", "partner_permissions", "access_to_program", "expected_status"),
    [
        ([], [], True, status.HTTP_403_FORBIDDEN),
        ([Permissions.PDU_UPLOAD], [], True, status.HTTP_202_ACCEPTED),
        ([], [Permissions.PDU_UPLOAD], True, status.HTTP_202_ACCEPTED),
        ([Permissions.PDU_UPLOAD], [Permissions.PDU_UPLOAD], True, status.HTTP_202_ACCEPTED),
        ([], [], False, status.HTTP_403_FORBIDDEN),
        ([Permissions.PDU_UPLOAD], [], False, status.HTTP_403_FORBIDDEN),
        ([], [Permissions.PDU_UPLOAD], False, status.HTTP_403_FORBIDDEN),
        ([Permissions.PDU_UPLOAD], [Permissions.PDU_VIEW_LIST_AND_DETAILS], False, status.HTTP_403_FORBIDDEN),
    ],
)
def test_upload_periodic_data_update_upload_permission(
    permissions: list,
    partner_permissions: list,
    access_to_program: bool,
    expected_status: int,
    authenticated_client: APIClient,
    user: User,
    partner: Partner,
    business_area: BusinessArea,
    program1: Program,
    url_upload: str,
    create_user_role_with_permissions: Callable,
    create_partner_role_with_permissions: Callable,
) -> None:
    if access_to_program:
        create_user_role_with_permissions(user, permissions, business_area, program1)
        create_partner_role_with_permissions(partner, partner_permissions, business_area, program1)
    else:
        create_user_role_with_permissions(user, permissions, business_area)
        create_partner_role_with_permissions(partner, partner_permissions, business_area)

    individual = IndividualFactory(
        household=None,
        business_area=business_area,
        program=program1,
    )
    household = HouseholdFactory(
        business_area=business_area,
        program=program1,
        head_of_household=individual,
    )
    individual.household = household
    individual.save()

    pdu_data = PeriodicFieldDataFactory(
        subtype=PeriodicFieldData.STRING,
        number_of_rounds=1,
        rounds_names=["January"],
    )
    pdu_field = FlexibleAttributeForPDUFactory(
        program=program1,
        label="PDU Field",
        pdu_data=pdu_data,
    )
    pdu_template = PDUXlsxTemplateFactory(
        program=program1,
        rounds_data=[
            {
                "field": pdu_field.name,
                "round": 1,
                "round_name": pdu_field.pdu_data.rounds_names[0],
                "number_of_records": 1,
            }
        ],
    )
    rows = [["Positive", "2024-07-20"]]

    service = PDUXlsxExportTemplateService(pdu_template)
    service.generate_workbook()
    service.save_xlsx_file()
    tmp_file = add_pdu_data_to_xlsx(pdu_template, rows)

    simple_file = SimpleUploadedFile(
        "file.xlsx",
        tmp_file.getvalue(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response = authenticated_client.post(url_upload, {"file": simple_file}, format="multipart")

    assert response.status_code == expected_status


@freezegun.freeze_time("2022-01-01")
def test_upload_periodic_data_update_upload(
    authenticated_client: APIClient,
    user: User,
    business_area: BusinessArea,
    program1: Program,
    url_upload: str,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.PDU_UPLOAD],
        business_area,
        program1,
    )

    individual = IndividualFactory(
        household=None,
        business_area=business_area,
        program=program1,
    )
    household = HouseholdFactory(
        business_area=business_area,
        program=program1,
        head_of_household=individual,
    )
    individual.household = household
    individual.save()

    pdu_data = PeriodicFieldDataFactory(
        subtype=PeriodicFieldData.STRING,
        number_of_rounds=1,
        rounds_names=["January"],
    )
    pdu_field = FlexibleAttributeForPDUFactory(
        program=program1,
        label="PDU Field",
        pdu_data=pdu_data,
    )
    populate_pdu_with_null_values(program1, individual.flex_fields)
    individual.save()

    pdu_template = PDUXlsxTemplateFactory(
        program=program1,
        rounds_data=[
            {
                "field": pdu_field.name,
                "round": 1,
                "round_name": pdu_field.pdu_data.rounds_names[0],
                "number_of_records": 1,
            }
        ],
    )
    rows = [["Positive", "2024-07-20"]]

    service = PDUXlsxExportTemplateService(pdu_template)
    service.generate_workbook()
    service.save_xlsx_file()
    tmp_file = add_pdu_data_to_xlsx(pdu_template, rows)

    simple_file = SimpleUploadedFile(
        "file.xlsx",
        tmp_file.getvalue(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response = authenticated_client.post(url_upload, {"file": simple_file}, format="multipart")

    assert response.status_code == status.HTTP_202_ACCEPTED

    individual.refresh_from_db()
    assert individual.flex_fields[pdu_field.name]["1"]["value"] == "Positive"
    assert individual.flex_fields[pdu_field.name]["1"]["collection_date"] == "2024-07-20"
