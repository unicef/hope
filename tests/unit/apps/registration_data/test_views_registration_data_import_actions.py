"""Tests for registration data import (RDI) views - main RDI operations."""

from contextlib import contextmanager
from typing import Any, Callable, Generator
from unittest.mock import ANY, Mock, patch

from django.db import DEFAULT_DB_ALIAS, connections
from django.test import override_settings
from django.urls import reverse
from flags.models import FlagState
import pytest
from rest_framework import status
from rest_framework.test import APIClient

from extras.test_utils.factories import (
    BeneficiaryGroupFactory,
    BusinessAreaFactory,
    DataCollectingTypeFactory,
    HouseholdFactory,
    ImportDataFactory,
    IndividualFactory,
    KoboImportDataFactory,
    PartnerFactory,
    ProgramFactory,
    RegistrationDataImportFactory,
    RoleAssignmentFactory,
    RoleFactory,
    SanctionListFactory,
    UserFactory,
)
from hope.apps.account.permissions import Permissions
from hope.apps.registration_data.services.biometric_deduplication import BiometricDeduplicationService
from hope.models import (
    BusinessArea,
    DataCollectingType,
    Household,
    ImportData,
    Individual,
    Partner,
    Program,
    RegistrationDataImport,
    Role,
    RoleAssignment,
    User,
)

pytestmark = pytest.mark.django_db


def create_household_and_individuals(
    household_data: dict, individuals_data: list[dict]
) -> tuple[Household, list[Individual]]:
    first_individual_data = individuals_data[0].copy()
    first_individual_data["household"] = None

    head_individual = IndividualFactory(**{**household_data, **first_individual_data})

    household = HouseholdFactory(**household_data, head_of_household=head_individual)

    head_individual.household = household
    head_individual.save()

    individuals = [head_individual]
    for individual_data in individuals_data[1:]:
        ind_data = individual_data.copy()
        individuals.append(IndividualFactory(**{**household_data, **ind_data, "household": household}))

    return household, individuals


@pytest.fixture
def business_area(db: Any) -> BusinessArea:
    return BusinessAreaFactory(slug="afghanistan", name="Afghanistan")


@pytest.fixture
def unicef_partner(db: Any) -> Partner:
    return PartnerFactory(name="UNICEF")


@pytest.fixture
def unicef_hq(unicef_partner: Partner) -> Partner:
    return PartnerFactory(name="UNICEF HQ", parent=unicef_partner)


@pytest.fixture
def user(unicef_hq: Partner, business_area: BusinessArea) -> User:
    user_permissions = [
        Permissions.RDI_VIEW_LIST,
        Permissions.RDI_VIEW_DETAILS,
        Permissions.RDI_MERGE_IMPORT,
        Permissions.RDI_REFUSE_IMPORT,
        Permissions.RDI_RERUN_DEDUPE,
        Permissions.RDI_IMPORT_DATA,
        Permissions.RDI_WEBHOOK_DEDUPLICATION,
    ]
    user = UserFactory(
        username="Hope_Test_DRF",
        password="HopePass",
        partner=unicef_hq,
        is_superuser=True,
    )
    permission_list = [perm.value for perm in user_permissions]
    role = RoleFactory(name="TestName", permissions=permission_list)
    RoleAssignmentFactory(user=user, role=role, business_area=business_area)
    return user


@pytest.fixture
def partner(db: Any) -> Partner:
    return PartnerFactory(name="Test Partner")


@pytest.fixture
def user_no_permissions(partner: Partner) -> User:
    return UserFactory(
        username="Hope_Test_DRF",
        password="HopePass",
        partner=partner,
        is_superuser=False,
    )


@pytest.fixture
def program(business_area: BusinessArea) -> Program:
    return ProgramFactory(
        name="Test Program",
        status=Program.ACTIVE,
        biometric_deduplication_enabled=True,
        business_area=business_area,
    )


@pytest.fixture
def api_client(user: User) -> APIClient:
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def api_client_no_permissions(user_no_permissions: User) -> APIClient:
    client = APIClient()
    client.force_authenticate(user=user_no_permissions)
    return client


@pytest.fixture
def program_with_sanction_list(business_area: BusinessArea) -> Program:
    program = ProgramFactory(
        name="Test Program",
        status=Program.ACTIVE,
        business_area=business_area,
    )
    program.sanction_lists.add(SanctionListFactory(name="Test Sanction List"))
    return program


def test_run_deduplication_without_permission(
    api_client_no_permissions: APIClient,
    program: Program,
) -> None:
    url = reverse(
        "api:registration-data:registration-data-imports-run-deduplication",
        args=["afghanistan", program.slug],
    )
    response = api_client_no_permissions.post(url, {}, format="json")
    assert response.status_code == status.HTTP_403_FORBIDDEN


@patch("hope.apps.registration_data.celery_tasks.deduplication_engine_process.delay")
def test_run_deduplication(
    mock_deduplication_engine_process: Mock,
    api_client: APIClient,
    program: Program,
) -> None:
    url = reverse(
        "api:registration-data:registration-data-imports-run-deduplication",
        args=["afghanistan", program.slug],
    )
    resp = api_client.post(url, {}, format="json")

    assert resp.status_code == status.HTTP_200_OK
    assert resp.data == {"message": "Deduplication process started"}
    mock_deduplication_engine_process.assert_called_once_with(str(program.id))

    RegistrationDataImportFactory(
        program=program, deduplication_engine_status=RegistrationDataImport.DEDUP_ENGINE_IN_PROGRESS
    )
    resp = api_client.post(url, {}, format="json")
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert resp.json() == ["Deduplication is already in progress for some RDIs"]

    program.biometric_deduplication_enabled = False
    program.save()
    resp = api_client.post(url, {}, format="json")
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert resp.json() == ["Biometric deduplication is not enabled for this program"]


@patch("hope.apps.registration_data.celery_tasks.fetch_biometric_deduplication_results_and_process.delay")
def test_webhook_deduplication(mock_fetch_dedup_results: Mock, api_client: APIClient, program: Program) -> None:
    url = reverse(
        "api:registration-data:registration-data-imports-webhook-deduplication",
        args=["afghanistan", program.slug],
    )
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    mock_fetch_dedup_results.assert_called_once_with(str(program.id))


def test_merge_rdi_without_permission(
    api_client_no_permissions: APIClient,
    business_area: BusinessArea,
    program: Program,
) -> None:
    rdi = RegistrationDataImportFactory(
        business_area=business_area,
        program=program,
        name="Test RDI",
        status=RegistrationDataImport.IN_REVIEW,
    )

    url = reverse(
        "api:registration-data:registration-data-imports-merge",
        args=["afghanistan", program.slug, rdi.id],
    )
    response = api_client_no_permissions.post(url, {}, format="json")
    assert response.status_code == status.HTTP_403_FORBIDDEN


@patch("hope.apps.registration_data.celery_tasks.merge_registration_data_import_task.delay")
def test_merge_rdi(mock_merge_task: Mock, api_client: APIClient, program: Program, business_area: BusinessArea) -> None:
    rdi = RegistrationDataImportFactory(
        business_area=business_area,
        program=program,
        name="Test RDI",
        status=RegistrationDataImport.IN_REVIEW,
    )

    url = reverse(
        "api:registration-data:registration-data-imports-merge",
        args=["afghanistan", program.slug, rdi.id],
    )

    response = api_client.post(url, {}, format="json")
    assert response.status_code == status.HTTP_200_OK
    assert response.data == {"message": "Registration Data Import Merge Scheduled"}

    rdi.refresh_from_db()
    assert rdi.status == RegistrationDataImport.MERGE_SCHEDULED
    mock_merge_task.assert_called_once_with(registration_data_import_id=rdi.id)


def test_merge_rdi_with_invalid_status(api_client: APIClient, program: Program, business_area: BusinessArea) -> None:
    rdi = RegistrationDataImportFactory(
        business_area=business_area,
        program=program,
        name="Test RDI",
        status=RegistrationDataImport.DEDUPLICATION,
    )

    url = reverse(
        "api:registration-data:registration-data-imports-merge",
        args=["afghanistan", program.slug, rdi.id],
    )

    response = api_client.post(url, {}, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST

    rdi.refresh_from_db()
    assert rdi.status == RegistrationDataImport.DEDUPLICATION


def test_erase_rdi_without_permission(
    api_client_no_permissions: APIClient,
    business_area: BusinessArea,
    program: Program,
) -> None:
    rdi = RegistrationDataImportFactory(
        business_area=business_area,
        program=program,
        name="Test RDI",
        status=RegistrationDataImport.IMPORT_ERROR,
    )

    url = reverse(
        "api:registration-data:registration-data-imports-erase",
        args=["afghanistan", program.slug, rdi.id],
    )
    response = api_client_no_permissions.post(url, {}, format="json")
    assert response.status_code == status.HTTP_403_FORBIDDEN


@patch("hope.apps.registration_data.api.views.BiometricDeduplicationService")
@patch("hope.apps.registration_data.api.views.remove_elasticsearch_documents_by_matching_ids")
def test_erase_rdi(
    mock_remove_es: Mock,
    mock_biometric_service: Mock,
    api_client: APIClient,
    program: Program,
    business_area: BusinessArea,
) -> None:
    mock_biometric_service.INDIVIDUALS_REFUSED = BiometricDeduplicationService.INDIVIDUALS_REFUSED
    mock_service = mock_biometric_service.return_value

    rdi = RegistrationDataImportFactory(
        business_area=business_area,
        program=program,
        name="Test RDI",
        status=RegistrationDataImport.IMPORT_ERROR,
    )

    household, individuals = create_household_and_individuals(
        household_data={
            "registration_data_import": rdi,
            "program": program,
            "business_area": business_area,
        },
        individuals_data=[
            {"program": program, "registration_data_import": rdi},
            {"program": program, "registration_data_import": rdi},
        ],
    )

    individual_ids = [ind.id for ind in individuals]

    assert Household.all_objects.filter(registration_data_import=rdi).count() == 1
    assert Individual.all_objects.filter(registration_data_import=rdi).count() == 2

    url = reverse(
        "api:registration-data:registration-data-imports-erase",
        args=["afghanistan", program.slug, rdi.id],
    )

    response = api_client.post(url, {}, format="json")
    assert response.status_code == status.HTTP_200_OK
    assert response.data == {"message": "Registration Data Import Erased"}

    assert Household.all_objects.filter(registration_data_import=rdi).count() == 0

    rdi.refresh_from_db()
    assert rdi.erased

    assert mock_remove_es.call_count == 2
    es_call_args = mock_remove_es.call_args_list[0][0]
    assert set(es_call_args[0]) == set(individual_ids)
    assert es_call_args[1].__name__ == f"IndividualDocument_{program.slug}"
    es_call_args_2 = mock_remove_es.call_args_list[1][0]
    assert set(es_call_args_2[0]) == {household.id}
    assert es_call_args_2[1].__name__ == f"HouseholdDocument_{program.slug}"

    mock_service.report_individuals_status.assert_called_once()
    report_call_args = mock_service.report_individuals_status.call_args[0]
    assert report_call_args[0] == program
    assert set(report_call_args[1]) == {str(_id) for _id in individual_ids}  # Order doesn't matter
    assert report_call_args[2] == mock_biometric_service.INDIVIDUALS_REFUSED


def test_erase_rdi_with_invalid_status(api_client: APIClient, program: Program, business_area: BusinessArea) -> None:
    rdi = RegistrationDataImportFactory(
        business_area=business_area,
        program=program,
        name="Test RDI",
        status=RegistrationDataImport.IN_REVIEW,
    )

    household, individuals = create_household_and_individuals(
        household_data={
            "registration_data_import": rdi,
            "program": program,
            "business_area": business_area,
        },
        individuals_data=[
            {"program": program, "registration_data_import": rdi},
        ],
    )

    url = reverse(
        "api:registration-data:registration-data-imports-erase",
        args=["afghanistan", program.slug, rdi.id],
    )

    response = api_client.post(url, {}, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST

    assert Household.all_objects.filter(registration_data_import=rdi).count() == 1

    rdi.refresh_from_db()
    assert not rdi.erased


@patch.dict(
    "os.environ",
    {
        "DEDUPLICATION_ENGINE_API_KEY": "dedup_api_key",
        "DEDUPLICATION_ENGINE_API_URL": "http://dedup-fake-url.com",
    },
)
def test_refuse_rdi_without_permission(
    api_client_no_permissions: APIClient,
    business_area: BusinessArea,
    program: Program,
) -> None:
    rdi = RegistrationDataImportFactory(
        business_area=business_area,
        program=program,
        name="Test RDI",
        status=RegistrationDataImport.IN_REVIEW,
    )

    url = reverse(
        "api:registration-data:registration-data-imports-refuse",
        args=["afghanistan", program.slug, rdi.id],
    )
    response = api_client_no_permissions.post(url, {"reason": "Test reason"}, format="json")
    assert response.status_code == status.HTTP_403_FORBIDDEN


@override_settings(
    CELERY_TASK_ALWAYS_EAGER=True,
    FLAGS={
        "BIOMETRIC_DEDUPLICATION_REPORT_INDIVIDUALS_STATUS": [
            {"condition": "boolean", "value": True, "required": True},
        ],
        "DEDUPLICATION_ENGINE_API_KEY": "dedup_api_key",
        "DEDUPLICATION_ENGINE_API_URL": "http://dedup-fake-url.com",
    },
)
@patch("hope.apps.registration_data.api.views.BiometricDeduplicationService")
@patch("hope.apps.registration_data.api.views.remove_elasticsearch_documents_by_matching_ids")
def test_refuse_rdi(
    remove_elasticsearch_documents_by_matching_ids_moc: Any,
    mock_biometric_service: Any,
    api_client: APIClient,
    program: Program,
    business_area: BusinessArea,
) -> None:
    mock_biometric_service.INDIVIDUALS_REFUSED = "rejected"

    FlagState.objects.get_or_create(
        name="BIOMETRIC_DEDUPLICATION_REPORT_INDIVIDUALS_STATUS",
        condition="boolean",
        value="True",
        required=False,
    )

    rdi = RegistrationDataImportFactory(
        business_area=business_area,
        program=program,
        name="Test RDI",
        status=RegistrationDataImport.IN_REVIEW,
    )

    create_household_and_individuals(
        household_data={
            "registration_data_import": rdi,
            "program": program,
            "business_area": business_area,
        },
        individuals_data=[
            {"program": program, "registration_data_import": rdi},
            {"program": program, "registration_data_import": rdi},
        ],
    )
    individuals_ids_to_remove = list(
        Individual.all_objects.filter(registration_data_import=rdi).values_list("id", flat=True)
    )

    assert Household.all_objects.filter(registration_data_import=rdi).count() == 1
    assert Individual.all_objects.filter(registration_data_import=rdi).count() == 2

    url = reverse(
        "api:registration-data:registration-data-imports-refuse",
        args=["afghanistan", program.slug, rdi.id],
    )

    response = api_client.post(url, {"reason": "Testing refuse endpoint"}, format="json")
    assert response.status_code == status.HTTP_200_OK
    assert response.data == {"message": "Registration Data Import Refused"}

    assert Household.all_objects.filter(registration_data_import=rdi).count() == 0

    rdi.refresh_from_db()
    assert rdi.status == RegistrationDataImport.REFUSED_IMPORT
    assert rdi.refuse_reason == "Testing refuse endpoint"

    mock_biometric_service.assert_called_once()
    mock_service_instance = mock_biometric_service.return_value
    mock_service_instance.report_individuals_status.assert_called_once_with(
        rdi.program, [str(_id) for _id in individuals_ids_to_remove], "rejected"
    )
    assert remove_elasticsearch_documents_by_matching_ids_moc.call_count == 2
    remove_elasticsearch_documents_by_matching_ids_moc.assert_any_call(individuals_ids_to_remove, ANY)
    assert (
        remove_elasticsearch_documents_by_matching_ids_moc.call_args_list[0][0][1].__name__
        == f"IndividualDocument_{program.slug}"
    )
    assert (
        remove_elasticsearch_documents_by_matching_ids_moc.call_args_list[1][0][1].__name__
        == f"HouseholdDocument_{program.slug}"
    )


def test_refuse_rdi_with_invalid_status(api_client: APIClient, program: Program, business_area: BusinessArea) -> None:
    rdi = RegistrationDataImportFactory(
        business_area=business_area,
        program=program,
        name="Test RDI",
        status=RegistrationDataImport.DEDUPLICATION,
    )

    create_household_and_individuals(
        household_data={
            "registration_data_import": rdi,
            "program": program,
            "business_area": business_area,
        },
        individuals_data=[
            {"program": program, "registration_data_import": rdi},
        ],
    )

    url = reverse(
        "api:registration-data:registration-data-imports-refuse",
        args=["afghanistan", program.slug, rdi.id],
    )

    response = api_client.post(url, {"reason": "Testing refuse endpoint"}, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST

    assert Household.all_objects.filter(registration_data_import=rdi).count() == 1

    rdi.refresh_from_db()
    assert rdi.status == RegistrationDataImport.DEDUPLICATION


def test_deduplicate_rdi_without_permission(
    api_client_no_permissions: APIClient,
    business_area: BusinessArea,
    program: Program,
) -> None:
    rdi = RegistrationDataImportFactory(
        business_area=business_area,
        program=program,
        name="Test RDI",
        status=RegistrationDataImport.DEDUPLICATION_FAILED,
    )

    url = reverse(
        "api:registration-data:registration-data-imports-deduplicate",
        args=["afghanistan", program.slug, rdi.id],
    )
    response = api_client_no_permissions.post(url, {}, format="json")
    assert response.status_code == status.HTTP_403_FORBIDDEN


@patch("hope.apps.registration_data.celery_tasks.rdi_deduplication_task.delay")
def test_deduplicate_rdi(
    mock_deduplicate_task: Mock, api_client: APIClient, program: Program, business_area: BusinessArea
) -> None:
    rdi = RegistrationDataImportFactory(
        business_area=business_area,
        program=program,
        name="Test RDI",
        status=RegistrationDataImport.DEDUPLICATION_FAILED,
    )

    url = reverse(
        "api:registration-data:registration-data-imports-deduplicate",
        args=["afghanistan", program.slug, rdi.id],
    )

    response = api_client.post(url, {}, format="json")
    assert response.status_code == status.HTTP_200_OK

    rdi.refresh_from_db()
    assert rdi.status == RegistrationDataImport.DEDUPLICATION

    mock_deduplicate_task.assert_called_once_with(registration_data_import_id=str(rdi.id))


def test_deduplicate_rdi_with_invalid_status(
    api_client: APIClient, program: Program, business_area: BusinessArea
) -> None:
    rdi = RegistrationDataImportFactory(
        business_area=business_area,
        program=program,
        name="Test RDI",
        status=RegistrationDataImport.IN_REVIEW,
    )

    url = reverse(
        "api:registration-data:registration-data-imports-deduplicate",
        args=["afghanistan", program.slug, rdi.id],
    )

    response = api_client.post(url, {}, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST

    rdi.refresh_from_db()
    assert rdi.status == RegistrationDataImport.IN_REVIEW


def test_status_choices_without_permission(
    api_client_no_permissions: APIClient,
    program: Program,
) -> None:
    url = reverse(
        "api:registration-data:registration-data-imports-status-choices",
        args=["afghanistan", program.slug],
    )
    response = api_client_no_permissions.get(url)
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_status_choices(api_client: APIClient, program: Program) -> None:
    url = reverse(
        "api:registration-data:registration-data-imports-status-choices",
        args=["afghanistan", program.slug],
    )
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.data, list)
    assert all("name" in c and "value" in c for c in response.data)


def test_registration_xlsx_import_without_permission(
    api_client_no_permissions: APIClient,
    business_area: BusinessArea,
    program: Program,
) -> None:
    import_data = ImportDataFactory(
        status=ImportData.STATUS_FINISHED,
        business_area_slug=business_area.slug,
    )

    url = reverse(
        "api:registration-data:registration-data-imports-registration-xlsx-import",
        args=["afghanistan", program.slug],
    )

    data = {
        "import_data_id": str(import_data.id),
        "name": "Test XLSX Import",
        "screen_beneficiary": True,
    }
    response = api_client_no_permissions.post(url, data, format="json")
    assert response.status_code == status.HTTP_403_FORBIDDEN


@patch("hope.apps.registration_data.celery_tasks.registration_xlsx_import_task.delay")
def test_registration_xlsx_import(
    mock_import_task: Mock, api_client: APIClient, user: User, program: Program, business_area: BusinessArea
) -> None:
    api_client.force_authenticate(user=user)

    # Create ImportData that's ready for import
    import_data = ImportDataFactory(
        status=ImportData.STATUS_FINISHED,
        business_area_slug=business_area.slug,
        data_type=ImportData.XLSX,
        number_of_households=5,
        number_of_individuals=15,
    )

    url = reverse(
        "api:registration-data:registration-data-imports-registration-xlsx-import",
        args=["afghanistan", program.slug],
    )

    data = {
        "import_data_id": str(import_data.id),
        "name": "Test XLSX Import",
        "screen_beneficiary": True,
    }

    with capture_on_commit_callbacks(execute=True):
        response = api_client.post(url, data, format="json")

    assert response.status_code == status.HTTP_201_CREATED

    # Check response contains required fields
    assert "id" in response.data
    assert response.data["name"] == "Test XLSX Import"
    assert "status" in response.data

    # Check RegistrationDataImport was created
    rdi = RegistrationDataImport.objects.get(id=response.data["id"])
    assert rdi.name == "Test XLSX Import"
    assert rdi.status == RegistrationDataImport.IMPORT_SCHEDULED
    assert rdi.data_source == RegistrationDataImport.XLS
    assert rdi.number_of_households == 5
    assert rdi.number_of_individuals == 15
    assert rdi.screen_beneficiary
    assert rdi.program == program
    assert rdi.imported_by == user

    # Check celery task was called
    mock_import_task.assert_called_once()


def test_registration_xlsx_import_import_data_not_found(api_client: APIClient, user: User, program: Program) -> None:
    api_client.force_authenticate(user=user)

    url = reverse(
        "api:registration-data:registration-data-imports-registration-xlsx-import",
        args=["afghanistan", program.slug],
    )

    data = {
        "import_data_id": "00000000-0000-0000-0000-000000000000",
        "name": "Test XLSX Import",
        "screen_beneficiary": True,
    }

    response = api_client.post(url, data, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Import data not found" in response.data


def test_registration_xlsx_import_import_data_not_ready(
    api_client: APIClient, user: User, program: Program, business_area: BusinessArea
) -> None:
    api_client.force_authenticate(user=user)

    # Create ImportData that's not ready
    import_data = ImportDataFactory(
        status=ImportData.STATUS_PENDING,
        business_area_slug=business_area.slug,
    )

    url = reverse(
        "api:registration-data:registration-data-imports-registration-xlsx-import",
        args=["afghanistan", program.slug],
    )

    data = {
        "import_data_id": str(import_data.id),
        "name": "Test XLSX Import",
        "screen_beneficiary": True,
    }

    response = api_client.post(url, data, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Import data is not ready for import" in response.data


def test_registration_xlsx_import_program_finished(
    api_client: APIClient, user: User, program: Program, business_area: BusinessArea
) -> None:
    api_client.force_authenticate(user=user)

    # Create ImportData that's ready for import
    import_data = ImportDataFactory(
        status=ImportData.STATUS_FINISHED,
        business_area_slug=business_area.slug,
    )

    # Set program to finished
    program.status = Program.FINISHED
    program.save()

    url = reverse(
        "api:registration-data:registration-data-imports-registration-xlsx-import",
        args=["afghanistan", program.slug],
    )

    data = {
        "import_data_id": str(import_data.id),
        "name": "Test XLSX Import",
        "screen_beneficiary": True,
    }

    response = api_client.post(url, data, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "In order to perform this action, program status must not be finished." in response.data


def test_registration_kobo_import_without_permission(
    api_client_no_permissions: APIClient,
    business_area: BusinessArea,
    program: Program,
) -> None:
    kobo_import_data = KoboImportDataFactory(
        status=ImportData.STATUS_FINISHED,
        business_area_slug=business_area.slug,
    )

    url = reverse(
        "api:registration-data:registration-data-imports-registration-kobo-import",
        args=["afghanistan", program.slug],
    )

    data = {
        "import_data_id": str(kobo_import_data.id),
        "name": "Test Kobo Import",
        "pull_pictures": True,
        "screen_beneficiary": False,
    }
    response = api_client_no_permissions.post(url, data, format="json")
    assert response.status_code == status.HTTP_403_FORBIDDEN


@patch("hope.apps.registration_data.celery_tasks.registration_kobo_import_task.delay")
def test_registration_kobo_import(
    mock_import_task: Mock, api_client: APIClient, user: User, program: Program, business_area: BusinessArea
) -> None:
    api_client.force_authenticate(user=user)

    # Create KoboImportData that's ready for import
    kobo_import_data = KoboImportDataFactory(
        status=ImportData.STATUS_FINISHED,
        business_area_slug=business_area.slug,
        kobo_asset_id="test_kobo_asset_456",
        number_of_households=8,
        number_of_individuals=25,
    )

    url = reverse(
        "api:registration-data:registration-data-imports-registration-kobo-import",
        args=["afghanistan", program.slug],
    )

    data = {
        "import_data_id": str(kobo_import_data.id),
        "name": "Test Kobo Import",
        "pull_pictures": True,
        "screen_beneficiary": False,
    }

    with capture_on_commit_callbacks(execute=True):
        response = api_client.post(url, data, format="json")

    assert response.status_code == status.HTTP_201_CREATED

    # Check response contains required fields
    assert "id" in response.data
    assert response.data["name"] == "Test Kobo Import"
    assert "status" in response.data

    # Check RegistrationDataImport was created
    rdi = RegistrationDataImport.objects.get(id=response.data["id"])
    assert rdi.name == "Test Kobo Import"
    assert rdi.status == RegistrationDataImport.IMPORT_SCHEDULED
    assert rdi.data_source == RegistrationDataImport.KOBO
    assert rdi.number_of_households == 8
    assert rdi.number_of_individuals == 25
    assert rdi.pull_pictures
    assert not rdi.screen_beneficiary
    assert rdi.program == program
    assert rdi.imported_by == user

    # Check celery task was called
    mock_import_task.assert_called_once()


def test_registration_kobo_import_kobo_data_not_found(api_client: APIClient, user: User, program: Program) -> None:
    api_client.force_authenticate(user=user)

    url = reverse(
        "api:registration-data:registration-data-imports-registration-kobo-import",
        args=["afghanistan", program.slug],
    )

    data = {
        "import_data_id": "00000000-0000-0000-0000-000000000000",
        "name": "Test Kobo Import",
        "pull_pictures": True,
        "screen_beneficiary": False,
    }

    response = api_client.post(url, data, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Kobo import data not found" in response.data


def test_registration_kobo_import_kobo_data_not_ready(
    api_client: APIClient, user: User, program: Program, business_area: BusinessArea
) -> None:
    api_client.force_authenticate(user=user)

    # Create KoboImportData that's not ready
    kobo_import_data = KoboImportDataFactory(
        status=ImportData.STATUS_PENDING,
        business_area_slug=business_area.slug,
    )

    url = reverse(
        "api:registration-data:registration-data-imports-registration-kobo-import",
        args=["afghanistan", program.slug],
    )

    data = {
        "import_data_id": str(kobo_import_data.id),
        "name": "Test Kobo Import",
        "pull_pictures": True,
        "screen_beneficiary": False,
    }

    response = api_client.post(url, data, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Kobo import data is not ready for import" in response.data


def test_registration_kobo_import_program_finished(
    api_client: APIClient, user: User, program: Program, business_area: BusinessArea
) -> None:
    api_client.force_authenticate(user=user)

    # Create KoboImportData that's ready for import
    kobo_import_data = KoboImportDataFactory(
        status=ImportData.STATUS_FINISHED,
        business_area_slug=business_area.slug,
    )

    # Set program to finished
    program.status = Program.FINISHED
    program.save()

    url = reverse(
        "api:registration-data:registration-data-imports-registration-kobo-import",
        args=["afghanistan", program.slug],
    )

    data = {
        "import_data_id": str(kobo_import_data.id),
        "name": "Test Kobo Import",
        "pull_pictures": True,
        "screen_beneficiary": False,
    }

    response = api_client.post(url, data, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "In order to perform this action, program status must not be finished." in response.data


@patch("hope.apps.registration_data.celery_tasks.registration_program_population_import_task.delay")
def test_create_rdi_social_worker_program_with_household_ids(
    mock_registration_task: Mock, api_client: APIClient, user: User, business_area: BusinessArea
) -> None:
    api_client.force_authenticate(user=user)
    role, _ = Role.objects.update_or_create(
        name="TestPermissionCreateRole",
        defaults={"permissions": [Permissions.RDI_IMPORT_DATA.value]},
    )
    RoleAssignment.objects.get_or_create(user=user, role=role, business_area=business_area)

    # Create social worker DCT
    social_dct = DataCollectingTypeFactory(
        label="Social",
        code="social",
        type=DataCollectingType.Type.SOCIAL,
    )
    beneficiary_group = BeneficiaryGroupFactory(name="Social", master_detail=False)

    # Create source and target programs with social worker DCT
    import_from_program = ProgramFactory(
        name="Source Social Worker Program",
        status=Program.ACTIVE,
        biometric_deduplication_enabled=True,
        beneficiary_group=beneficiary_group,
        data_collecting_type=social_dct,
    )

    target_program = ProgramFactory(
        name="Target Social Worker Program",
        status=Program.ACTIVE,
        business_area=business_area,
        beneficiary_group=beneficiary_group,
        data_collecting_type=social_dct,
    )

    social_dct.compatible_types.add(social_dct)

    # Create households with individuals in source program
    household1, individuals1 = create_household_and_individuals(
        household_data={
            "program": import_from_program,
            "business_area": business_area,
        },
        individuals_data=[
            {"program": import_from_program, "business_area": business_area},
        ],
    )

    household2, individuals2 = create_household_and_individuals(
        household_data={
            "program": import_from_program,
            "business_area": business_area,
        },
        individuals_data=[
            {"program": import_from_program, "business_area": business_area},
        ],
    )

    url = reverse(
        "api:registration-data:registration-data-imports-list",
        args=["afghanistan", target_program.slug],
    )

    # Import using household IDs
    data = {
        "import_from_program_id": str(import_from_program.id),
        "import_from_ids": f"{household1.unicef_id}, {household2.unicef_id}",
        "name": "Test Social Worker Import - Households",
        "screen_beneficiary": False,
    }

    with capture_on_commit_callbacks(execute=True):
        response = api_client.post(url, data, format="json")

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["name"] == "Test Social Worker Import - Households"
    # Should import both households
    assert response.data["number_of_households"] == 2
    assert response.data["number_of_individuals"] == 2
    mock_registration_task.assert_called_once()


@patch("hope.apps.registration_data.celery_tasks.registration_program_population_import_task.delay")
def test_create_rdi_social_worker_program_with_individual_ids(
    mock_registration_task: Mock, api_client: APIClient, user: User, business_area: BusinessArea
) -> None:
    api_client.force_authenticate(user=user)
    role, _ = Role.objects.update_or_create(
        name="TestPermissionCreateRole",
        defaults={"permissions": [Permissions.RDI_IMPORT_DATA.value]},
    )
    RoleAssignment.objects.get_or_create(user=user, role=role, business_area=business_area)

    # Create social worker DCT
    social_dct = DataCollectingTypeFactory(
        label="Social",
        code="social",
        type=DataCollectingType.Type.SOCIAL,
    )
    beneficiary_group = BeneficiaryGroupFactory(name="Social", master_detail=False)

    # Create source and target programs with social worker DCT
    import_from_program = ProgramFactory(
        name="Source Social Worker Program",
        status=Program.ACTIVE,
        biometric_deduplication_enabled=True,
        beneficiary_group=beneficiary_group,
        data_collecting_type=social_dct,
    )

    target_program = ProgramFactory(
        name="Target Social Worker Program",
        status=Program.ACTIVE,
        business_area=business_area,
        beneficiary_group=beneficiary_group,
        data_collecting_type=social_dct,
    )

    social_dct.compatible_types.add(social_dct)

    # Create households with individuals in source program
    household1, individuals1 = create_household_and_individuals(
        household_data={
            "program": import_from_program,
            "business_area": business_area,
        },
        individuals_data=[
            {"program": import_from_program, "business_area": business_area},
            {"program": import_from_program, "business_area": business_area},
        ],
    )

    household2, individuals2 = create_household_and_individuals(
        household_data={
            "program": import_from_program,
            "business_area": business_area,
        },
        individuals_data=[
            {"program": import_from_program, "business_area": business_area},
        ],
    )

    url = reverse(
        "api:registration-data:registration-data-imports-list",
        args=["afghanistan", target_program.slug],
    )

    # Import using individual IDs
    data = {
        "import_from_program_id": str(import_from_program.id),
        "import_from_ids": f"{individuals1[0].unicef_id}, {individuals2[0].unicef_id}",
        "name": "Test Social Worker Import - Individuals",
        "screen_beneficiary": False,
    }

    with capture_on_commit_callbacks(execute=True):
        response = api_client.post(url, data, format="json")

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["name"] == "Test Social Worker Import - Individuals"
    assert response.data["number_of_households"] == 2
    assert response.data["number_of_individuals"] == 2
    mock_registration_task.assert_called_once()


@patch("hope.apps.registration_data.celery_tasks.registration_program_population_import_task.delay")
def test_create_registration_data_import_without_permission(
    mock_registration_task: Mock,
    api_client_no_permissions: APIClient,
    business_area: BusinessArea,
    program_with_sanction_list: Program,
) -> None:
    # Create a source program to import from
    import_from_program = ProgramFactory(
        name="Source Program",
        status=Program.ACTIVE,
        biometric_deduplication_enabled=True,
        beneficiary_group=program_with_sanction_list.beneficiary_group,
        data_collecting_type=program_with_sanction_list.data_collecting_type,
        business_area=business_area,
    )

    create_household_and_individuals(
        household_data={
            "program": import_from_program,
            "business_area": business_area,
        },
        individuals_data=[
            {"program": import_from_program, "business_area": business_area},
        ],
    )

    url = reverse(
        "api:registration-data:registration-data-imports-list",
        args=["afghanistan", program_with_sanction_list.slug],
    )

    data = {
        "import_from_program_id": str(import_from_program.id),
        "import_from_ids": "",
        "name": "Test Import",
        "screen_beneficiary": True,
    }

    with capture_on_commit_callbacks(execute=True):
        response = api_client_no_permissions.post(url, data, format="json")

    assert response.status_code == status.HTTP_403_FORBIDDEN
    mock_registration_task.assert_not_called()


@patch("hope.apps.registration_data.celery_tasks.registration_program_population_import_task.delay")
def test_create_registration_data_import(
    mock_registration_task: Mock,
    api_client_no_permissions: APIClient,
    user_no_permissions: User,
    business_area: BusinessArea,
    program_with_sanction_list: Program,
) -> None:
    # Grant permission for create
    role = RoleFactory(name="TestPermissionCreateRole", permissions=[Permissions.RDI_IMPORT_DATA.value])
    RoleAssignmentFactory(user=user_no_permissions, role=role, business_area=business_area)

    # Create a source program to import from, matching beneficiary group and data collecting type
    compatible_dct = DataCollectingTypeFactory(code="compatible_dct")
    import_from_program = ProgramFactory(
        name="Source Program",
        status=Program.ACTIVE,
        biometric_deduplication_enabled=True,
        beneficiary_group=program_with_sanction_list.beneficiary_group,
        data_collecting_type=compatible_dct,
        business_area=business_area,
    )
    import_from_program.data_collecting_type.compatible_types.add(program_with_sanction_list.data_collecting_type)

    # Create at least one household and individual in the source program
    create_household_and_individuals(
        household_data={
            "program": import_from_program,
            "business_area": business_area,
        },
        individuals_data=[
            {"program": import_from_program, "business_area": business_area},
        ],
    )
    create_household_and_individuals(
        household_data={
            "program": import_from_program,
            "business_area": business_area,
        },
        individuals_data=[
            {"program": import_from_program, "business_area": business_area},
            {"program": import_from_program, "business_area": business_area},
        ],
    )

    url = reverse(
        "api:registration-data:registration-data-imports-list",
        args=["afghanistan", program_with_sanction_list.slug],
    )

    data = {
        "import_from_program_id": str(import_from_program.id),
        "import_from_ids": "",  # No specific IDs, import all
        "name": "Test Import",
        "screen_beneficiary": True,
    }

    with capture_on_commit_callbacks(execute=True):
        response = api_client_no_permissions.post(url, data, format="json")

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["name"] == "Test Import"
    assert response.data["number_of_households"] == 2
    assert response.data["number_of_individuals"] == 3
    assert "id" in response.data
    mock_registration_task.assert_called_once()


@patch("hope.apps.registration_data.celery_tasks.registration_program_population_import_task.delay")
def test_create_registration_data_import_with_ids_filter(
    mock_registration_task: Mock,
    api_client_no_permissions: APIClient,
    user_no_permissions: User,
    business_area: BusinessArea,
    program_with_sanction_list: Program,
) -> None:
    # Grant permission for create
    role = RoleFactory(name="TestPermissionCreateRole", permissions=[Permissions.RDI_IMPORT_DATA.value])
    RoleAssignmentFactory(user=user_no_permissions, role=role, business_area=business_area)

    # Create a source program to import from
    compatible_dct = DataCollectingTypeFactory(code="compatible_dct")
    import_from_program = ProgramFactory(
        name="Source Program",
        status=Program.ACTIVE,
        biometric_deduplication_enabled=True,
        beneficiary_group=program_with_sanction_list.beneficiary_group,
        data_collecting_type=compatible_dct,
        business_area=business_area,
    )
    import_from_program.data_collecting_type.compatible_types.add(program_with_sanction_list.data_collecting_type)

    # Create households
    create_household_and_individuals(
        household_data={
            "program": import_from_program,
            "business_area": business_area,
        },
        individuals_data=[
            {"program": import_from_program, "business_area": business_area},
        ],
    )
    household, individuals = create_household_and_individuals(
        household_data={
            "program": import_from_program,
            "business_area": business_area,
        },
        individuals_data=[
            {"program": import_from_program, "business_area": business_area},
            {"program": import_from_program, "business_area": business_area},
        ],
    )

    url = reverse(
        "api:registration-data:registration-data-imports-list",
        args=["afghanistan", program_with_sanction_list.slug],
    )

    data = {
        "import_from_program_id": str(import_from_program.id),
        "import_from_ids": f"{household.unicef_id}",  # Only 1 household
        "name": "Test Import",
        "screen_beneficiary": True,
    }

    with capture_on_commit_callbacks(execute=True):
        response = api_client_no_permissions.post(url, data, format="json")

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["name"] == "Test Import"
    assert response.data["number_of_households"] == 1
    assert response.data["number_of_individuals"] == 2
    mock_registration_task.assert_called_once()


@patch("hope.apps.registration_data.celery_tasks.registration_program_population_import_task.delay")
def test_create_registration_data_import_invalid_bg(
    mock_registration_task: Mock,
    api_client_no_permissions: APIClient,
    user_no_permissions: User,
    business_area: BusinessArea,
    program_with_sanction_list: Program,
) -> None:
    role = RoleFactory(name="TestPermissionCreateRole", permissions=[Permissions.RDI_IMPORT_DATA.value])
    RoleAssignmentFactory(user=user_no_permissions, role=role, business_area=business_area)

    import_from_program = ProgramFactory(
        name="Source Program",
        status=Program.ACTIVE,
        biometric_deduplication_enabled=True,
        beneficiary_group=BeneficiaryGroupFactory(name="Different Beneficiary Group"),
        data_collecting_type=program_with_sanction_list.data_collecting_type,
        business_area=business_area,
    )

    create_household_and_individuals(
        household_data={
            "program": import_from_program,
            "business_area": business_area,
        },
        individuals_data=[
            {"program": import_from_program, "business_area": business_area},
        ],
    )

    url = reverse(
        "api:registration-data:registration-data-imports-list",
        args=["afghanistan", program_with_sanction_list.slug],
    )

    data = {
        "import_from_program_id": str(import_from_program.id),
        "import_from_ids": "",
        "name": "Test Import",
        "screen_beneficiary": True,
    }

    with capture_on_commit_callbacks(execute=True):
        response = api_client_no_permissions.post(url, data, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Cannot import data from a program with a different Beneficiary Group." in str(response.data)


@patch("hope.apps.registration_data.celery_tasks.registration_program_population_import_task.delay")
def test_create_registration_data_import_invalid_dct(
    mock_registration_task: Mock,
    api_client_no_permissions: APIClient,
    user_no_permissions: User,
    business_area: BusinessArea,
    program_with_sanction_list: Program,
) -> None:
    role = RoleFactory(name="TestPermissionCreateRole", permissions=[Permissions.RDI_IMPORT_DATA.value])
    RoleAssignmentFactory(user=user_no_permissions, role=role, business_area=business_area)

    import_from_program = ProgramFactory(
        name="Source Program",
        status=Program.ACTIVE,
        biometric_deduplication_enabled=True,
        beneficiary_group=program_with_sanction_list.beneficiary_group,
        data_collecting_type=DataCollectingTypeFactory(code="incompatible_dct"),
        business_area=business_area,
    )

    create_household_and_individuals(
        household_data={
            "program": import_from_program,
            "business_area": business_area,
        },
        individuals_data=[
            {"program": import_from_program, "business_area": business_area},
        ],
    )

    url = reverse(
        "api:registration-data:registration-data-imports-list",
        args=["afghanistan", program_with_sanction_list.slug],
    )

    data = {
        "import_from_program_id": str(import_from_program.id),
        "import_from_ids": "",
        "name": "Test Import",
        "screen_beneficiary": True,
    }

    with capture_on_commit_callbacks(execute=True):
        response = api_client_no_permissions.post(url, data, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Cannot import data from a program with not compatible data collecting type." in str(response.data)


@patch("hope.apps.registration_data.celery_tasks.registration_program_population_import_task.delay")
def test_create_registration_data_import_program_finished(
    mock_registration_task: Mock,
    api_client_no_permissions: APIClient,
    user_no_permissions: User,
    business_area: BusinessArea,
    program_with_sanction_list: Program,
) -> None:
    role = RoleFactory(name="TestPermissionCreateRole", permissions=[Permissions.RDI_IMPORT_DATA.value])
    RoleAssignmentFactory(user=user_no_permissions, role=role, business_area=business_area)

    import_from_program = ProgramFactory(
        name="Source Program",
        status=Program.ACTIVE,
        biometric_deduplication_enabled=True,
        beneficiary_group=program_with_sanction_list.beneficiary_group,
        data_collecting_type=program_with_sanction_list.data_collecting_type,
        business_area=business_area,
    )

    create_household_and_individuals(
        household_data={
            "program": import_from_program,
            "business_area": business_area,
        },
        individuals_data=[
            {"program": import_from_program, "business_area": business_area},
        ],
    )

    program_with_sanction_list.status = Program.FINISHED
    program_with_sanction_list.save()

    url = reverse(
        "api:registration-data:registration-data-imports-list",
        args=["afghanistan", program_with_sanction_list.slug],
    )

    data = {
        "import_from_program_id": str(import_from_program.id),
        "import_from_ids": "",
        "name": "Test Import",
        "screen_beneficiary": True,
    }

    with capture_on_commit_callbacks(execute=True):
        response = api_client_no_permissions.post(url, data, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "In order to perform this action, program status must not be finished." in str(response.data)


@patch("hope.apps.registration_data.celery_tasks.registration_program_population_import_task.delay")
def test_create_registration_data_import_cannot_check_against_sanction_list(
    mock_registration_task: Mock,
    api_client_no_permissions: APIClient,
    user_no_permissions: User,
    business_area: BusinessArea,
) -> None:
    role = RoleFactory(name="TestPermissionCreateRole", permissions=[Permissions.RDI_IMPORT_DATA.value])
    RoleAssignmentFactory(user=user_no_permissions, role=role, business_area=business_area)

    # Create program without sanction list
    program_no_sanction = ProgramFactory(
        name="Test Program No Sanction",
        status=Program.ACTIVE,
        business_area=business_area,
    )

    import_from_program = ProgramFactory(
        name="Source Program",
        status=Program.ACTIVE,
        biometric_deduplication_enabled=True,
        beneficiary_group=program_no_sanction.beneficiary_group,
        data_collecting_type=program_no_sanction.data_collecting_type,
        business_area=business_area,
    )

    create_household_and_individuals(
        household_data={
            "program": import_from_program,
            "business_area": business_area,
        },
        individuals_data=[
            {"program": import_from_program, "business_area": business_area},
        ],
    )

    url = reverse(
        "api:registration-data:registration-data-imports-list",
        args=["afghanistan", program_no_sanction.slug],
    )

    data = {
        "import_from_program_id": str(import_from_program.id),
        "import_from_ids": "",
        "name": "Test Import",
        "screen_beneficiary": True,
    }

    with capture_on_commit_callbacks(execute=True):
        response = api_client_no_permissions.post(url, data, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Cannot check against sanction list." in str(response.data)


@patch("hope.apps.registration_data.celery_tasks.registration_program_population_import_task.delay")
def test_create_registration_data_import_0_objects(
    mock_registration_task: Mock,
    api_client_no_permissions: APIClient,
    user_no_permissions: User,
    business_area: BusinessArea,
    program_with_sanction_list: Program,
) -> None:
    role = RoleFactory(name="TestPermissionCreateRole", permissions=[Permissions.RDI_IMPORT_DATA.value])
    RoleAssignmentFactory(user=user_no_permissions, role=role, business_area=business_area)

    import_from_program = ProgramFactory(
        name="Source Program",
        status=Program.ACTIVE,
        biometric_deduplication_enabled=True,
        beneficiary_group=program_with_sanction_list.beneficiary_group,
        data_collecting_type=program_with_sanction_list.data_collecting_type,
        business_area=business_area,
    )

    url = reverse(
        "api:registration-data:registration-data-imports-list",
        args=["afghanistan", program_with_sanction_list.slug],
    )

    data = {
        "import_from_program_id": str(import_from_program.id),
        "import_from_ids": "",
        "name": "Test Import",
        "screen_beneficiary": True,
    }

    with capture_on_commit_callbacks(execute=True):
        response = api_client_no_permissions.post(url, data, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "This action would result in importing 0 households and 0 individuals." in str(response.data)


def test_registration_xlsx_import_name_not_unique(
    api_client_no_permissions: APIClient,
    user_no_permissions: User,
    business_area: BusinessArea,
    program_with_sanction_list: Program,
) -> None:
    role = RoleFactory(name="TestPermissionCreateRole", permissions=[Permissions.RDI_IMPORT_DATA.value])
    RoleAssignmentFactory(user=user_no_permissions, role=role, business_area=business_area)

    RegistrationDataImportFactory(
        business_area=business_area,
        program=program_with_sanction_list,
        name="Test Unique Name",
        status=RegistrationDataImport.IN_REVIEW,
    )

    import_data = ImportDataFactory(
        status=ImportData.STATUS_FINISHED,
        business_area_slug=business_area.slug,
        data_type=ImportData.XLSX,
        number_of_households=2,
        number_of_individuals=5,
    )

    url = reverse(
        "api:registration-data:registration-data-imports-registration-xlsx-import",
        args=["afghanistan", program_with_sanction_list.slug],
    )

    data = {
        "import_data_id": str(import_data.id),
        "name": "Test Unique Name",  # Same as existing RDI
        "screen_beneficiary": False,
    }

    response = api_client_no_permissions.post(url, data, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "name" in response.data
    assert "This field must be unique." in str(response.data["name"])
    assert RegistrationDataImport.objects.filter(name="Test Unique Name").count() == 1


@contextmanager
def capture_on_commit_callbacks(
    *, using: str = DEFAULT_DB_ALIAS, execute: bool = False
) -> Generator[list[Callable[[], None]], None, None]:
    callbacks: list[Callable[[], None]] = []
    start_count = len(connections[using].run_on_commit)
    try:
        yield callbacks
    finally:
        while True:
            callback_count = len(connections[using].run_on_commit)
            for _, callback, _ in connections[using].run_on_commit[start_count:]:
                callbacks.append(callback)
                if execute:
                    callback()

            if callback_count == len(connections[using].run_on_commit):
                break
            start_count = callback_count
