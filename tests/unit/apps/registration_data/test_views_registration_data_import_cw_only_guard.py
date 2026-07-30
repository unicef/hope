from typing import Any, Callable
from unittest.mock import Mock, patch

from django.urls import reverse
import pytest
from rest_framework import status
from rest_framework.test import APIClient

from extras.test_utils.factories import (
    BusinessAreaFactory,
    HouseholdFactory,
    IndividualFactory,
    PartnerFactory,
    ProgramFactory,
    RegistrationDataImportFactory,
    RoleAssignmentFactory,
    RoleFactory,
    UserFactory,
)
from hope.apps.account.permissions import Permissions
from hope.models import BusinessArea, Partner, Program, RegistrationDataImport, User
from hope.models.business_area import ALL_EXCEPT_CW_INGEST_REJECT_MSG

pytestmark = pytest.mark.django_db


@pytest.fixture
def cw_only_business_area(db: Any) -> BusinessArea:
    return BusinessAreaFactory(
        slug="afghanistan",
        name="Afghanistan",
        ingest_source=BusinessArea.IngestSource.COUNTRY_WORKSPACE_ONLY,
    )


@pytest.fixture
def unicef_partner(db: Any) -> Partner:
    return PartnerFactory(name="UNICEF")


@pytest.fixture
def unicef_hq(unicef_partner: Partner) -> Partner:
    return PartnerFactory(name="UNICEF HQ", parent=unicef_partner)


@pytest.fixture
def user(unicef_hq: Partner, cw_only_business_area: BusinessArea) -> User:
    user = UserFactory(username="Hope_Test_DRF", password="HopePass", partner=unicef_hq, is_superuser=True)
    role = RoleFactory(
        name="TestName",
        permissions=[
            Permissions.RDI_VIEW_LIST.value,
            Permissions.RDI_VIEW_DETAILS.value,
            Permissions.RDI_MERGE_IMPORT.value,
            Permissions.RDI_REFUSE_IMPORT.value,
            Permissions.RDI_RERUN_DEDUPE.value,
            Permissions.RDI_IMPORT_DATA.value,
        ],
    )
    RoleAssignmentFactory(user=user, role=role, business_area=cw_only_business_area)
    return user


@pytest.fixture
def api_client(user: User) -> APIClient:
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def program(cw_only_business_area: BusinessArea) -> Program:
    return ProgramFactory(name="Test Program", status=Program.ACTIVE, business_area=cw_only_business_area)


@pytest.fixture
def rdi(cw_only_business_area: BusinessArea, program: Program) -> RegistrationDataImport:
    return RegistrationDataImportFactory(
        business_area=cw_only_business_area,
        program=program,
        name="Test RDI",
        status=RegistrationDataImport.IN_REVIEW,
    )


# (url_builder, body) — url_builder resolves the route from fixtures so the test body stays
# branch-free. List routes ignore the rdi argument; detail routes use it.
BLOCKED_WRITE_ACTIONS: list[Any] = [
    pytest.param(
        lambda ba, code, rdi_id: reverse("api:registration-data:registration-data-imports-list", args=[ba, code]),
        {},
        id="create",
    ),
    pytest.param(
        lambda ba, code, rdi_id: reverse(
            "api:registration-data:registration-data-imports-registration-xlsx-import", args=[ba, code]
        ),
        {},
        id="registration_xlsx_import",
    ),
    pytest.param(
        lambda ba, code, rdi_id: reverse(
            "api:registration-data:registration-data-imports-registration-kobo-import", args=[ba, code]
        ),
        {},
        id="registration_kobo_import",
    ),
    pytest.param(
        lambda ba, code, rdi_id: reverse(
            "api:registration-data:registration-data-imports-merge", args=[ba, code, rdi_id]
        ),
        {},
        id="merge",
    ),
    pytest.param(
        lambda ba, code, rdi_id: reverse(
            "api:registration-data:registration-data-imports-refuse", args=[ba, code, rdi_id]
        ),
        {},
        id="refuse",
    ),
    pytest.param(
        lambda ba, code, rdi_id: reverse(
            "api:registration-data:registration-data-imports-erase", args=[ba, code, rdi_id]
        ),
        {},
        id="erase",
    ),
    pytest.param(
        lambda ba, code, rdi_id: reverse(
            "api:registration-data:registration-data-imports-deduplicate", args=[ba, code, rdi_id]
        ),
        {},
        id="deduplicate",
    ),
]


@pytest.mark.parametrize(("url_builder", "body"), BLOCKED_WRITE_ACTIONS)
def test_write_action_blocked_for_cw_only_business_area(
    url_builder: Callable[[str, str, Any], str],
    body: dict,
    api_client: APIClient,
    cw_only_business_area: BusinessArea,
    program: Program,
    rdi: RegistrationDataImport,
) -> None:
    url = url_builder(cw_only_business_area.slug, program.code, rdi.id)

    response = api_client.post(url, body, format="json")

    assert response.status_code == status.HTTP_403_FORBIDDEN, str(response.data)
    assert ALL_EXCEPT_CW_INGEST_REJECT_MSG in str(response.data)


def test_create_blocked_for_cw_only_creates_no_rdi(
    api_client: APIClient,
    cw_only_business_area: BusinessArea,
    program: Program,
) -> None:
    url = reverse(
        "api:registration-data:registration-data-imports-list", args=[cw_only_business_area.slug, program.code]
    )

    response = api_client.post(url, {}, format="json")

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert RegistrationDataImport.objects.count() == 0


@patch("hope.apps.registration_data.api.views.registration_xlsx_import_async_task")
def test_xlsx_import_blocked_for_cw_only_enqueues_no_task(
    mock_xlsx_task: Mock,
    api_client: APIClient,
    cw_only_business_area: BusinessArea,
    program: Program,
) -> None:
    url = reverse(
        "api:registration-data:registration-data-imports-registration-xlsx-import",
        args=[cw_only_business_area.slug, program.code],
    )

    response = api_client.post(url, {}, format="json")

    assert response.status_code == status.HTTP_403_FORBIDDEN
    mock_xlsx_task.assert_not_called()


OPEN_READ_ACTIONS: list[Any] = [
    pytest.param("api:registration-data:registration-data-imports-list", id="list"),
    pytest.param("api:registration-data:registration-data-imports-count", id="count"),
    pytest.param("api:registration-data:registration-data-imports-status-choices", id="status_choices"),
]


@pytest.mark.parametrize("url_name", OPEN_READ_ACTIONS)
def test_read_action_allowed_for_cw_only_business_area(
    url_name: str,
    api_client: APIClient,
    cw_only_business_area: BusinessArea,
    program: Program,
) -> None:
    url = reverse(url_name, args=[cw_only_business_area.slug, program.code])

    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK


def test_retrieve_allowed_for_cw_only_business_area(
    api_client: APIClient,
    cw_only_business_area: BusinessArea,
    program: Program,
    rdi: RegistrationDataImport,
) -> None:
    url = reverse(
        "api:registration-data:registration-data-imports-detail",
        args=[cw_only_business_area.slug, program.code, rdi.id],
    )

    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK


@pytest.fixture
def non_cw_business_area(db: Any) -> BusinessArea:
    return BusinessAreaFactory(
        slug="ukraine",
        name="Ukraine",
        ingest_source=BusinessArea.IngestSource.ALL_EXCEPT_COUNTRY_WORKSPACE,
    )


@pytest.fixture
def non_cw_user(unicef_hq: Partner, non_cw_business_area: BusinessArea) -> User:
    user = UserFactory(username="Hope_Test_DRF_NonCW", password="HopePass", partner=unicef_hq, is_superuser=True)
    role = RoleFactory(name="NonCwTestName", permissions=[Permissions.RDI_IMPORT_DATA.value])
    RoleAssignmentFactory(user=user, role=role, business_area=non_cw_business_area)
    return user


@pytest.fixture
def non_cw_api_client(non_cw_user: User) -> APIClient:
    client = APIClient()
    client.force_authenticate(user=non_cw_user)
    return client


@pytest.fixture
def non_cw_target_program(non_cw_business_area: BusinessArea) -> Program:
    return ProgramFactory(name="Target Program", status=Program.ACTIVE, business_area=non_cw_business_area)


@pytest.fixture
def non_cw_source_program(non_cw_business_area: BusinessArea, non_cw_target_program: Program) -> Program:
    # Same beneficiary group + data collecting type as the target so the create compatibility checks pass.
    source = ProgramFactory(
        name="Source Program",
        status=Program.ACTIVE,
        business_area=non_cw_business_area,
        beneficiary_group=non_cw_target_program.beneficiary_group,
        data_collecting_type=non_cw_target_program.data_collecting_type,
    )
    head = IndividualFactory(program=source, business_area=non_cw_business_area, household=None)
    household = HouseholdFactory(program=source, business_area=non_cw_business_area, head_of_household=head)
    head.household = household
    head.save()
    return source


@patch("hope.apps.registration_data.api.views.registration_program_population_import_async_task")
def test_create_succeeds_for_non_cw_business_area(
    mock_population_task: Mock,
    non_cw_api_client: APIClient,
    non_cw_business_area: BusinessArea,
    non_cw_target_program: Program,
    non_cw_source_program: Program,
    django_capture_on_commit_callbacks: Any,
) -> None:
    url = reverse(
        "api:registration-data:registration-data-imports-list",
        args=[non_cw_business_area.slug, non_cw_target_program.code],
    )
    data = {
        "import_from_program_id": str(non_cw_source_program.id),
        "import_from_ids": "",
        "name": "Non-CW Smoke Import",
        "screen_beneficiary": False,
    }

    with django_capture_on_commit_callbacks(execute=True):
        response = non_cw_api_client.post(url, data, format="json")

    assert response.status_code == status.HTTP_201_CREATED, str(response.data)
    assert response.data["name"] == "Non-CW Smoke Import"
    mock_population_task.assert_called_once()
