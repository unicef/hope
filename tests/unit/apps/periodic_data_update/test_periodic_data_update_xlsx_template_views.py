"""Tests for PDU xlsx template views."""

import json
from typing import Any, Callable

from django.contrib.admin.options import get_content_type_for_model
from django.core.cache import cache
from django.core.files.base import ContentFile
from django.db import connection
from django.http import FileResponse
from django.test.utils import CaptureQueriesContext
from django.utils import timezone
import freezegun
import pytest
from rest_framework import status
from rest_framework.reverse import reverse

from extras.test_utils.factories import (
    BusinessAreaFactory,
    FlexibleAttributeForPDUFactory,
    PartnerFactory,
    PDUXlsxTemplateFactory,
    PeriodicFieldDataFactory,
    ProgramFactory,
    UserFactory,
)
from hope.apps.account.permissions import Permissions
from hope.models import BusinessArea, FileTemp, Partner, PDUXlsxTemplate, PeriodicFieldData, Program, User

pytestmark = pytest.mark.django_db


@pytest.fixture
def afghanistan(db: Any) -> BusinessArea:
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
def program1(afghanistan: BusinessArea) -> Program:
    return ProgramFactory(business_area=afghanistan, name="Program1")


@pytest.fixture
def program2(afghanistan: BusinessArea) -> Program:
    return ProgramFactory(business_area=afghanistan, name="Program2")


@pytest.fixture
def pdu_template1(program1: Program, user: User) -> PDUXlsxTemplate:
    return PDUXlsxTemplateFactory(program=program1, created_by=user)


@pytest.fixture
def pdu_template2(program1: Program, user: User) -> PDUXlsxTemplate:
    return PDUXlsxTemplateFactory(program=program1, created_by=user)


@pytest.fixture
def pdu_template3(program1: Program, user: User) -> PDUXlsxTemplate:
    return PDUXlsxTemplateFactory(program=program1, created_by=user)


@pytest.fixture
def pdu_template_program2(program2: Program) -> PDUXlsxTemplate:
    return PDUXlsxTemplateFactory(program=program2)


@pytest.fixture
def pdu_field_vaccination(program1: Program) -> Any:
    pdu_data_vaccination = PeriodicFieldDataFactory(
        subtype=PeriodicFieldData.DECIMAL,
        number_of_rounds=5,
        rounds_names=[
            "January vaccination",
            "February vaccination",
            "March vaccination",
            "April vaccination",
            "May vaccination",
        ],
    )
    return FlexibleAttributeForPDUFactory(
        program=program1,
        label="Vaccination Records Update",
        pdu_data=pdu_data_vaccination,
    )


@pytest.fixture
def pdu_field_health(program1: Program) -> Any:
    pdu_data_health = PeriodicFieldDataFactory(
        subtype=PeriodicFieldData.DECIMAL,
        number_of_rounds=5,
        rounds_names=["January", "February", "March", "April", "May"],
    )
    return FlexibleAttributeForPDUFactory(
        program=program1,
        label="Health Records Update",
        pdu_data=pdu_data_health,
    )


@pytest.fixture
def url_list(afghanistan: BusinessArea, program1: Program) -> str:
    return reverse(
        "api:periodic-data-update:periodic-data-update-templates-list",
        kwargs={
            "business_area_slug": afghanistan.slug,
            "program_slug": program1.slug,
        },
    )


@pytest.fixture
def url_count(afghanistan: BusinessArea, program1: Program) -> str:
    return reverse(
        "api:periodic-data-update:periodic-data-update-templates-count",
        kwargs={
            "business_area_slug": afghanistan.slug,
            "program_slug": program1.slug,
        },
    )


@pytest.fixture
def url_detail_pdu_template_program2(
    afghanistan: BusinessArea, program2: Program, pdu_template_program2: PDUXlsxTemplate
) -> str:
    return reverse(
        "api:periodic-data-update:periodic-data-update-templates-detail",
        kwargs={
            "business_area_slug": afghanistan.slug,
            "program_slug": program2.slug,
            "pk": pdu_template_program2.id,
        },
    )


@pytest.fixture
def url_detail_pdu_template1(afghanistan: BusinessArea, program1: Program, pdu_template1: PDUXlsxTemplate) -> str:
    return reverse(
        "api:periodic-data-update:periodic-data-update-templates-detail",
        kwargs={
            "business_area_slug": afghanistan.slug,
            "program_slug": program1.slug,
            "pk": pdu_template1.id,
        },
    )


@pytest.fixture
def url_create_pdu_template_program1(afghanistan: BusinessArea, program1: Program) -> str:
    return reverse(
        "api:periodic-data-update:periodic-data-update-templates-list",
        kwargs={
            "business_area_slug": afghanistan.slug,
            "program_slug": program1.slug,
        },
    )


@pytest.fixture
def url_create_pdu_template_program2(afghanistan: BusinessArea, program2: Program) -> str:
    return reverse(
        "api:periodic-data-update:periodic-data-update-templates-list",
        kwargs={
            "business_area_slug": afghanistan.slug,
            "program_slug": program2.slug,
        },
    )


@pytest.fixture
def url_export_pdu_template_program1(
    afghanistan: BusinessArea, program1: Program, pdu_template1: PDUXlsxTemplate
) -> str:
    return reverse(
        "api:periodic-data-update:periodic-data-update-templates-export",
        kwargs={
            "business_area_slug": afghanistan.slug,
            "program_slug": program1.slug,
            "pk": pdu_template1.id,
        },
    )


@pytest.fixture
def url_export_pdu_template_program2(
    afghanistan: BusinessArea, program2: Program, pdu_template_program2: PDUXlsxTemplate
) -> str:
    return reverse(
        "api:periodic-data-update:periodic-data-update-templates-export",
        kwargs={
            "business_area_slug": afghanistan.slug,
            "program_slug": program2.slug,
            "pk": pdu_template_program2.id,
        },
    )


@pytest.fixture
def url_download_pdu_template_program1(
    afghanistan: BusinessArea, program1: Program, pdu_template1: PDUXlsxTemplate
) -> str:
    return reverse(
        "api:periodic-data-update:periodic-data-update-templates-download",
        kwargs={
            "business_area_slug": afghanistan.slug,
            "program_slug": program1.slug,
            "pk": pdu_template1.id,
        },
    )


@pytest.fixture
def url_download_pdu_template_program2(
    afghanistan: BusinessArea, program2: Program, pdu_template_program2: PDUXlsxTemplate
) -> str:
    return reverse(
        "api:periodic-data-update:periodic-data-update-templates-download",
        kwargs={
            "business_area_slug": afghanistan.slug,
            "program_slug": program2.slug,
            "pk": pdu_template_program2.id,
        },
    )


@freezegun.freeze_time("2022-01-01")
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
        (
            [Permissions.PDU_VIEW_LIST_AND_DETAILS],
            [],
            False,
            status.HTTP_403_FORBIDDEN,
        ),
        (
            [],
            [Permissions.PDU_VIEW_LIST_AND_DETAILS],
            False,
            status.HTTP_403_FORBIDDEN,
        ),
        (
            [Permissions.PDU_VIEW_LIST_AND_DETAILS],
            [Permissions.PDU_VIEW_LIST_AND_DETAILS],
            False,
            status.HTTP_403_FORBIDDEN,
        ),
    ],
)
def test_list_periodic_data_update_templates_permission(
    permissions: list,
    partner_permissions: list,
    access_to_program: bool,
    expected_status: int,
    authenticated_client: Any,
    user: User,
    partner: Partner,
    afghanistan: BusinessArea,
    program1: Program,
    pdu_template1: PDUXlsxTemplate,
    pdu_template2: PDUXlsxTemplate,
    pdu_template3: PDUXlsxTemplate,
    url_list: str,
    create_user_role_with_permissions: Callable,
    create_partner_role_with_permissions: Callable,
) -> None:
    if access_to_program:
        create_user_role_with_permissions(user, permissions, afghanistan, program1)
        create_partner_role_with_permissions(partner, partner_permissions, afghanistan, program1)
    else:
        create_user_role_with_permissions(user, permissions, afghanistan)
        create_partner_role_with_permissions(partner, partner_permissions, afghanistan)

    response = authenticated_client.get(url_list)
    assert response.status_code == expected_status


@freezegun.freeze_time("2022-01-01")
def test_list_periodic_data_update_templates(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program1: Program,
    pdu_template1: PDUXlsxTemplate,
    pdu_template2: PDUXlsxTemplate,
    pdu_template3: PDUXlsxTemplate,
    pdu_template_program2: PDUXlsxTemplate,
    url_list: str,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.PDU_VIEW_LIST_AND_DETAILS],
        afghanistan,
        program1,
    )
    response = authenticated_client.get(url_list)
    assert response.status_code == status.HTTP_200_OK

    response_json = response.json()["results"]
    assert len(response_json) == 3
    assert {
        "id": pdu_template1.id,
        "name": pdu_template1.name,
        "status_display": pdu_template1.combined_status_display,
        "status": pdu_template1.combined_status,
        "number_of_records": pdu_template1.number_of_records,
        "created_at": pdu_template1.created_at.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "created_by": pdu_template1.created_by.get_full_name(),
        "can_export": pdu_template1.can_export,
        "admin_url": None,
    } in response_json
    assert {
        "id": pdu_template2.id,
        "name": pdu_template2.name,
        "status_display": pdu_template2.combined_status_display,
        "status": pdu_template2.combined_status,
        "number_of_records": pdu_template2.number_of_records,
        "created_at": pdu_template2.created_at.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "created_by": pdu_template2.created_by.get_full_name(),
        "can_export": pdu_template2.can_export,
        "admin_url": None,
    } in response_json
    assert {
        "id": pdu_template3.id,
        "name": pdu_template3.name,
        "status_display": pdu_template3.combined_status_display,
        "status": pdu_template3.combined_status,
        "number_of_records": pdu_template3.number_of_records,
        "created_at": pdu_template3.created_at.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "created_by": pdu_template3.created_by.get_full_name(),
        "can_export": pdu_template3.can_export,
        "admin_url": None,
    } in response_json
    assert {
        "id": pdu_template_program2.id,
        "name": pdu_template_program2.name,
        "status_display": pdu_template_program2.combined_status_display,
        "status": pdu_template_program2.combined_status,
        "number_of_records": pdu_template_program2.number_of_records,
        "created_at": pdu_template_program2.created_at.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "created_by": pdu_template_program2.created_by.get_full_name(),
        "can_export": pdu_template_program2.can_export,
        "admin_url": None,
    } not in response_json


@freezegun.freeze_time("2022-01-01")
def test_count_periodic_data_update_templates(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program1: Program,
    pdu_template1: PDUXlsxTemplate,
    pdu_template2: PDUXlsxTemplate,
    pdu_template3: PDUXlsxTemplate,
    url_count: str,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.PDU_VIEW_LIST_AND_DETAILS],
        afghanistan,
        program1,
    )
    response = authenticated_client.get(url_count)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["count"] == 3


@freezegun.freeze_time("2022-01-01")
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
        (
            [Permissions.PDU_VIEW_LIST_AND_DETAILS],
            [],
            False,
            status.HTTP_403_FORBIDDEN,
        ),
        (
            [],
            [Permissions.PDU_VIEW_LIST_AND_DETAILS],
            False,
            status.HTTP_403_FORBIDDEN,
        ),
        (
            [Permissions.PDU_VIEW_LIST_AND_DETAILS],
            [Permissions.PDU_VIEW_LIST_AND_DETAILS],
            False,
            status.HTTP_403_FORBIDDEN,
        ),
    ],
)
def test_detail_periodic_data_update_template_permission(
    permissions: list,
    partner_permissions: list,
    access_to_program: bool,
    expected_status: int,
    authenticated_client: Any,
    user: User,
    partner: Partner,
    afghanistan: BusinessArea,
    program2: Program,
    url_detail_pdu_template_program2: str,
    url_detail_pdu_template1: str,
    create_user_role_with_permissions: Callable,
    create_partner_role_with_permissions: Callable,
) -> None:
    if access_to_program:
        create_user_role_with_permissions(user, permissions, afghanistan, program2)
        create_partner_role_with_permissions(partner, partner_permissions, afghanistan, program2)
    else:
        create_user_role_with_permissions(user, permissions, afghanistan)
        create_partner_role_with_permissions(partner, partner_permissions, afghanistan)

    response = authenticated_client.get(url_detail_pdu_template_program2)
    assert response.status_code == expected_status

    # no access to pdu_template1 for any case as it is in Program1 and user has access to Program2
    response_forbidden = authenticated_client.get(url_detail_pdu_template1)
    assert response_forbidden.status_code == 403


@freezegun.freeze_time("2022-01-01")
def test_detail_periodic_data_update_templates(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program2: Program,
    pdu_template_program2: PDUXlsxTemplate,
    url_detail_pdu_template_program2: str,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.PDU_VIEW_LIST_AND_DETAILS],
        afghanistan,
        program2,
    )

    response = authenticated_client.get(url_detail_pdu_template_program2)
    assert response.status_code == status.HTTP_200_OK

    response_json = response.json()
    assert {
        "id": pdu_template_program2.id,
        "name": pdu_template_program2.name,
        "rounds_data": pdu_template_program2.rounds_data,
    } == response_json


@freezegun.freeze_time("2022-01-01")
@pytest.mark.skip("Caching is disabled for now")
def test_list_periodic_data_update_templates_caching(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program1: Program,
    pdu_template1: PDUXlsxTemplate,
    pdu_template2: PDUXlsxTemplate,
    pdu_template3: PDUXlsxTemplate,
    url_list: str,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.PDU_VIEW_LIST_AND_DETAILS],
        afghanistan,
        program1,
    )
    with CaptureQueriesContext(connection) as ctx:
        response = authenticated_client.get(url_list)
        assert response.status_code == status.HTTP_200_OK

        etag = response.headers["etag"]
        assert json.loads(cache.get(etag)[0].decode("utf8")) == response.json()
        assert len(ctx.captured_queries) == 12

    # Test that reoccurring requests use cached data
    with CaptureQueriesContext(connection) as ctx:
        response = authenticated_client.get(url_list)
        assert response.status_code == status.HTTP_200_OK

        etag_second_call = response.headers["etag"]
        assert json.loads(cache.get(response.headers["etag"])[0].decode("utf8")) == response.json()
        assert len(ctx.captured_queries) == 5

        assert etag_second_call == etag


@freezegun.freeze_time("2022-01-01")
@pytest.mark.parametrize(
    ("permissions", "partner_permissions", "access_to_program", "expected_status"),
    [
        ([], [], True, status.HTTP_403_FORBIDDEN),
        ([Permissions.PDU_TEMPLATE_CREATE], [], True, status.HTTP_201_CREATED),
        ([], [Permissions.PDU_TEMPLATE_CREATE], True, status.HTTP_201_CREATED),
        (
            [Permissions.PDU_TEMPLATE_CREATE],
            [Permissions.PDU_TEMPLATE_CREATE],
            True,
            status.HTTP_201_CREATED,
        ),
        ([], [], False, status.HTTP_403_FORBIDDEN),
        ([Permissions.PDU_TEMPLATE_CREATE], [], False, status.HTTP_403_FORBIDDEN),
        ([], [Permissions.PDU_TEMPLATE_CREATE], False, status.HTTP_403_FORBIDDEN),
        (
            [Permissions.PDU_TEMPLATE_CREATE],
            [Permissions.PDU_TEMPLATE_CREATE],
            False,
            status.HTTP_403_FORBIDDEN,
        ),
    ],
)
def test_create_periodic_data_update_template_permission(
    permissions: list,
    partner_permissions: list,
    access_to_program: bool,
    expected_status: int,
    authenticated_client: Any,
    user: User,
    partner: Partner,
    afghanistan: BusinessArea,
    program1: Program,
    pdu_field_vaccination: Any,
    pdu_field_health: Any,
    url_create_pdu_template_program1: str,
    url_create_pdu_template_program2: str,
    create_user_role_with_permissions: Callable,
    create_partner_role_with_permissions: Callable,
) -> None:
    if access_to_program:
        create_user_role_with_permissions(user, permissions, afghanistan, program1)
        create_partner_role_with_permissions(partner, partner_permissions, afghanistan, program1)
    else:
        create_user_role_with_permissions(user, permissions, afghanistan)
        create_partner_role_with_permissions(partner, partner_permissions, afghanistan)

    data = {
        "rounds_data": [
            {
                "field": pdu_field_vaccination.name,
                "round": 2,
            },
            {
                "field": pdu_field_health.name,
                "round": 4,
            },
        ],
        "filters": {
            "received_assistance": True,
        },
    }
    response = authenticated_client.post(url_create_pdu_template_program1, data=data)
    assert response.status_code == expected_status

    # no access to Program2
    response_forbidden = authenticated_client.post(url_create_pdu_template_program2, data=data)
    assert response_forbidden.status_code == 403


@freezegun.freeze_time("2022-01-01")
def test_create_periodic_data_update_template(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program1: Program,
    pdu_field_vaccination: Any,
    pdu_field_health: Any,
    url_create_pdu_template_program1: str,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.PDU_TEMPLATE_CREATE],
        afghanistan,
        program1,
    )
    data = {
        "name": "Test Template",
        "rounds_data": [
            {
                "field": pdu_field_vaccination.name,
                "round": 2,
            },
            {
                "field": pdu_field_health.name,
                "round": 4,
            },
        ],
        "filters": {
            "received_assistance": True,
        },
    }
    expected_result = [
        {
            "field": pdu_field_vaccination.name,
            "round": 2,
            "round_name": "February vaccination",
            "number_of_records": 0,
        },
        {
            "field": pdu_field_health.name,
            "round": 4,
            "round_name": "April",
            "number_of_records": 0,
        },
    ]
    response = authenticated_client.post(url_create_pdu_template_program1, data=data)
    assert response.status_code == status.HTTP_201_CREATED

    response_json = response.json()
    assert PDUXlsxTemplate.objects.filter(id=response_json["id"]).exists()
    template = PDUXlsxTemplate.objects.get(id=response_json["id"])
    assert template.program == program1
    assert template.name == data["name"]
    assert template.business_area == afghanistan
    assert template.rounds_data == expected_result
    assert template.filters == data["filters"]
    assert template.status == PDUXlsxTemplate.Status.EXPORTED
    assert PDUXlsxTemplate.objects.filter(id=response_json["id"]).first().file is not None


@freezegun.freeze_time("2022-01-01")
def test_create_periodic_data_update_template_duplicate_field(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program1: Program,
    pdu_field_vaccination: Any,
    url_create_pdu_template_program1: str,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.PDU_TEMPLATE_CREATE],
        afghanistan,
        program1,
    )
    data = {
        "rounds_data": [
            {
                "field": pdu_field_vaccination.name,
                "round": 2,
            },
            {
                "field": pdu_field_vaccination.name,
                "round": 4,
            },
        ],
        "filters": {
            "received_assistance": True,
        },
    }
    response = authenticated_client.post(url_create_pdu_template_program1, data=data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST

    response_json = response.json()
    assert response_json == {"rounds_data": ["Each Field can only be used once in the template."]}


@freezegun.freeze_time("2022-01-01")
@pytest.mark.parametrize(
    ("permissions", "partner_permissions", "access_to_program", "expected_status"),
    [
        ([], [], True, status.HTTP_403_FORBIDDEN),
        ([Permissions.PDU_TEMPLATE_CREATE], [], True, status.HTTP_200_OK),
        ([], [Permissions.PDU_TEMPLATE_CREATE], True, status.HTTP_200_OK),
        (
            [Permissions.PDU_TEMPLATE_CREATE],
            [Permissions.PDU_TEMPLATE_CREATE],
            True,
            status.HTTP_200_OK,
        ),
        ([], [], False, status.HTTP_403_FORBIDDEN),
        ([Permissions.PDU_TEMPLATE_CREATE], [], False, status.HTTP_403_FORBIDDEN),
        ([], [Permissions.PDU_TEMPLATE_CREATE], False, status.HTTP_403_FORBIDDEN),
        (
            [Permissions.PDU_TEMPLATE_CREATE],
            [Permissions.PDU_TEMPLATE_CREATE],
            False,
            status.HTTP_403_FORBIDDEN,
        ),
    ],
)
def test_export_periodic_data_update_template_permission(
    permissions: list,
    partner_permissions: list,
    access_to_program: bool,
    expected_status: int,
    authenticated_client: Any,
    user: User,
    partner: Partner,
    afghanistan: BusinessArea,
    program1: Program,
    pdu_template1: PDUXlsxTemplate,
    url_export_pdu_template_program1: str,
    url_export_pdu_template_program2: str,
    create_user_role_with_permissions: Callable,
    create_partner_role_with_permissions: Callable,
) -> None:
    if access_to_program:
        create_user_role_with_permissions(user, permissions, afghanistan, program1)
        create_partner_role_with_permissions(partner, partner_permissions, afghanistan, program1)
    else:
        create_user_role_with_permissions(user, permissions, afghanistan)
        create_partner_role_with_permissions(partner, partner_permissions, afghanistan)

    pdu_template1.status = PDUXlsxTemplate.Status.TO_EXPORT
    pdu_template1.save()

    response = authenticated_client.post(url_export_pdu_template_program1)
    assert response.status_code == expected_status

    # no access to Program2
    response_forbidden = authenticated_client.post(url_export_pdu_template_program2)
    assert response_forbidden.status_code == 403


@freezegun.freeze_time("2022-01-01")
def test_export_periodic_data_update_template(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program1: Program,
    pdu_template1: PDUXlsxTemplate,
    url_export_pdu_template_program1: str,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.PDU_TEMPLATE_CREATE],
        afghanistan,
        program1,
    )

    pdu_template1.status = PDUXlsxTemplate.Status.TO_EXPORT
    pdu_template1.file = None
    pdu_template1.save()

    response = authenticated_client.post(url_export_pdu_template_program1)
    assert response.status_code == status.HTTP_200_OK

    pdu_template1.refresh_from_db()
    assert pdu_template1.status == PDUXlsxTemplate.Status.EXPORTED
    assert pdu_template1.file is not None


@freezegun.freeze_time("2022-01-01")
def test_export_periodic_data_update_template_already_exporting(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program1: Program,
    pdu_template1: PDUXlsxTemplate,
    url_export_pdu_template_program1: str,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.PDU_TEMPLATE_CREATE],
        afghanistan,
        program1,
    )

    pdu_template1.status = PDUXlsxTemplate.Status.EXPORTING
    pdu_template1.file = None
    pdu_template1.save()

    response = authenticated_client.post(url_export_pdu_template_program1)
    assert response.status_code == status.HTTP_400_BAD_REQUEST

    response_json = response.json()
    assert response_json == ["Template is already being exported"]


@freezegun.freeze_time("2022-01-01")
def test_export_periodic_data_update_template_already_exported(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program1: Program,
    pdu_template1: PDUXlsxTemplate,
    url_export_pdu_template_program1: str,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.PDU_TEMPLATE_CREATE],
        afghanistan,
        program1,
    )

    file = FileTemp.objects.create(
        object_id=pdu_template1.pk,
        content_type=get_content_type_for_model(pdu_template1),
        created=timezone.now(),
        file=ContentFile(b"Test content", f"Test File {pdu_template1.pk}.xlsx"),
    )
    pdu_template1.file = file
    pdu_template1.status = PDUXlsxTemplate.Status.EXPORTED
    pdu_template1.save()

    response = authenticated_client.post(url_export_pdu_template_program1)
    assert response.status_code == status.HTTP_400_BAD_REQUEST

    response_json = response.json()
    assert response_json == ["Template is already exported"]


@freezegun.freeze_time("2022-01-01")
@pytest.mark.parametrize(
    ("permissions", "partner_permissions", "access_to_program", "expected_status"),
    [
        ([], [], True, status.HTTP_403_FORBIDDEN),
        ([Permissions.PDU_TEMPLATE_DOWNLOAD], [], True, status.HTTP_200_OK),
        ([], [Permissions.PDU_TEMPLATE_DOWNLOAD], True, status.HTTP_200_OK),
        (
            [Permissions.PDU_TEMPLATE_DOWNLOAD],
            [Permissions.PDU_TEMPLATE_DOWNLOAD],
            True,
            status.HTTP_200_OK,
        ),
        ([], [], False, status.HTTP_403_FORBIDDEN),
        ([Permissions.PDU_TEMPLATE_DOWNLOAD], [], False, status.HTTP_403_FORBIDDEN),
        ([], [Permissions.PDU_TEMPLATE_DOWNLOAD], False, status.HTTP_403_FORBIDDEN),
        (
            [Permissions.PDU_TEMPLATE_DOWNLOAD],
            [Permissions.PDU_TEMPLATE_DOWNLOAD],
            False,
            status.HTTP_403_FORBIDDEN,
        ),
    ],
)
def test_download_periodic_data_update_template_permission(
    permissions: list,
    partner_permissions: list,
    access_to_program: bool,
    expected_status: int,
    authenticated_client: Any,
    user: User,
    partner: Partner,
    afghanistan: BusinessArea,
    program1: Program,
    pdu_template1: PDUXlsxTemplate,
    url_download_pdu_template_program1: str,
    url_download_pdu_template_program2: str,
    create_user_role_with_permissions: Callable,
    create_partner_role_with_permissions: Callable,
) -> None:
    if access_to_program:
        create_user_role_with_permissions(user, permissions, afghanistan, program1)
        create_partner_role_with_permissions(partner, partner_permissions, afghanistan, program1)
    else:
        create_user_role_with_permissions(user, permissions, afghanistan)
        create_partner_role_with_permissions(partner, partner_permissions, afghanistan)

    pdu_template1.status = PDUXlsxTemplate.Status.EXPORTED

    file = FileTemp.objects.create(
        object_id=pdu_template1.pk,
        content_type=get_content_type_for_model(pdu_template1),
        created=timezone.now(),
        file=ContentFile(b"Test content", f"Test File {pdu_template1.pk}.xlsx"),
    )
    pdu_template1.file = file
    pdu_template1.status = PDUXlsxTemplate.Status.EXPORTED
    pdu_template1.save()

    response = authenticated_client.get(url_download_pdu_template_program1)
    assert response.status_code == expected_status

    # no access to Program2
    response_forbidden = authenticated_client.get(url_download_pdu_template_program2)
    assert response_forbidden.status_code == 403


@freezegun.freeze_time("2022-01-01")
def test_download_periodic_data_update_template(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program1: Program,
    pdu_template1: PDUXlsxTemplate,
    url_download_pdu_template_program1: str,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.PDU_TEMPLATE_DOWNLOAD],
        afghanistan,
        program1,
    )

    file = FileTemp.objects.create(
        object_id=pdu_template1.pk,
        content_type=get_content_type_for_model(pdu_template1),
        created=timezone.now(),
        file=ContentFile(b"Test content", f"Test File {pdu_template1.pk}.xlsx"),
    )
    pdu_template1.file = file
    pdu_template1.status = PDUXlsxTemplate.Status.EXPORTED
    pdu_template1.save()

    response = authenticated_client.get(url_download_pdu_template_program1)
    assert response.status_code == status.HTTP_200_OK

    pdu_template1.refresh_from_db()
    assert pdu_template1.status == PDUXlsxTemplate.Status.EXPORTED
    assert isinstance(response, FileResponse) is True
    assert f'filename="{file.file.name}"' in response["Content-Disposition"]
    assert response["Content-Type"] == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    assert response.getvalue() == b"Test content"


@freezegun.freeze_time("2022-01-01")
def test_download_periodic_data_update_template_not_exported(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program1: Program,
    pdu_template1: PDUXlsxTemplate,
    url_download_pdu_template_program1: str,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.PDU_TEMPLATE_DOWNLOAD],
        afghanistan,
        program1,
    )

    pdu_template1.status = PDUXlsxTemplate.Status.TO_EXPORT
    pdu_template1.save()

    response = authenticated_client.get(url_download_pdu_template_program1)
    assert response.status_code == status.HTTP_400_BAD_REQUEST

    response_json = response.json()
    assert response_json == ["Template is not exported yet"]


@freezegun.freeze_time("2022-01-01")
def test_download_periodic_data_update_template_no_records(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program1: Program,
    pdu_template1: PDUXlsxTemplate,
    url_download_pdu_template_program1: str,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.PDU_TEMPLATE_DOWNLOAD],
        afghanistan,
        program1,
    )

    pdu_template1.status = PDUXlsxTemplate.Status.EXPORTED
    pdu_template1.number_of_records = 0
    pdu_template1.save()

    response = authenticated_client.get(url_download_pdu_template_program1)
    assert response.status_code == status.HTTP_400_BAD_REQUEST

    response_json = response.json()
    assert response_json == ["Template has no records"]


@freezegun.freeze_time("2022-01-01")
def test_download_periodic_data_update_template_no_file(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program1: Program,
    pdu_template1: PDUXlsxTemplate,
    url_download_pdu_template_program1: str,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.PDU_TEMPLATE_DOWNLOAD],
        afghanistan,
        program1,
    )

    pdu_template1.status = PDUXlsxTemplate.Status.EXPORTED
    pdu_template1.number_of_records = 1
    pdu_template1.file = None
    pdu_template1.save()

    response = authenticated_client.get(url_download_pdu_template_program1)
    assert response.status_code == status.HTTP_400_BAD_REQUEST

    response_json = response.json()
    assert response_json == ["Template file is missing"]
