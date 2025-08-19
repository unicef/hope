from contextlib import contextmanager
from typing import Callable, Generator
from unittest.mock import Mock, patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import DEFAULT_DB_ALIAS, connections
from django.urls import reverse
from extras.test_utils.factories.account import PartnerFactory, UserFactory
from extras.test_utils.factories.core import DataCollectingTypeFactory
from extras.test_utils.factories.household import create_household_and_individuals
from extras.test_utils.factories.program import BeneficiaryGroupFactory, ProgramFactory
from extras.test_utils.factories.registration_data import (
    ImportDataFactory,
    KoboImportDataFactory,
    RegistrationDataImportFactory,
)
from extras.test_utils.factories.sanction_list import SanctionListFactory
from rest_framework import status
from rest_framework.test import APIClient
from unit.api.base import HOPEApiTestCase

from hope.apps.account.models import Role, RoleAssignment
from hope.apps.account.permissions import Permissions
from hope.apps.household.models import Household, Individual
from hope.apps.program.models import Program
from hope.apps.registration_data.models import (
    ImportData,
    KoboImportData,
    RegistrationDataImport,
)
from hope.apps.sanction_list.models import SanctionList


class RegistrationDataImportViewSetTest(HOPEApiTestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        user_permissions = [
            Permissions.RDI_VIEW_LIST,
            Permissions.RDI_VIEW_DETAILS,
            Permissions.RDI_MERGE_IMPORT,
            Permissions.RDI_REFUSE_IMPORT,
            Permissions.RDI_RERUN_DEDUPE,
            Permissions.RDI_IMPORT_DATA,
        ]
        unicef_partner = PartnerFactory(name="UNICEF")
        unicef = PartnerFactory(name="UNICEF HQ", parent=unicef_partner)
        cls.user = UserFactory(
            username="Hope_Test_DRF",
            password="HopePass",
            partner=unicef,
            is_superuser=True,
        )
        permission_list = [perm.value for perm in user_permissions]
        role, created = Role.objects.update_or_create(name="TestName", defaults={"permissions": permission_list})
        user_role, _ = RoleAssignment.objects.get_or_create(user=cls.user, role=role, business_area=cls.business_area)
        cls.program = ProgramFactory(
            name="Test Program",
            status=Program.ACTIVE,
            biometric_deduplication_enabled=True,
        )
        cls.client = APIClient()

    @patch("hope.apps.registration_datahub.celery_tasks.deduplication_engine_process.delay")
    def test_run_deduplication(self, mock_deduplication_engine_process: Mock) -> None:
        self.client.force_authenticate(user=self.user)
        url = reverse(
            "api:registration-data:registration-data-imports-run-deduplication",
            args=["afghanistan", self.program.slug],
        )
        resp = self.client.post(url, {}, format="json")

        assert resp.status_code == status.HTTP_200_OK
        assert resp.data == {"message": "Deduplication process started"}
        mock_deduplication_engine_process.assert_called_once_with(str(self.program.id))

    @patch("hope.apps.registration_datahub.celery_tasks.fetch_biometric_deduplication_results_and_process.delay")
    def test_webhook_deduplication(self, mock_fetch_dedup_results: Mock) -> None:
        url = reverse(
            "api:registration-data:registration-data-imports-webhook-deduplication",
            args=["afghanistan", self.program.slug],
        )
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK
        mock_fetch_dedup_results.assert_called_once_with(self.program.deduplication_set_id)

    def test_list_registrations(self) -> None:
        self.client.force_authenticate(user=self.user)
        rdi1 = RegistrationDataImportFactory(
            business_area=self.business_area,
            program=self.program,
            name="Test RDI 1",
            status=RegistrationDataImport.IN_REVIEW,
            data_source=RegistrationDataImport.XLS,
            imported_by=self.user,
        )
        rdi2 = RegistrationDataImportFactory(
            business_area=self.business_area,
            program=self.program,
            name="Test RDI 2",
            status=RegistrationDataImport.DEDUPLICATION,
            data_source=RegistrationDataImport.KOBO,
            imported_by=self.user,
        )

        url = reverse(
            "api:registration-data:registration-data-imports-list",
            args=["afghanistan", self.program.slug],
        )

        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK

        results = response.data["results"]
        assert len(results) == 2
        assert {r["name"] for r in results} == {rdi1.name, rdi2.name}

        for result in results:
            if result["name"] == "Test RDI 1":
                assert result["status"] == "In Review"
                assert result["data_source"] == "Excel"
                assert result["imported_by"] == self.user.get_full_name()
            elif result["name"] == "Test RDI 2":
                assert result["status"] == "Deduplication"
                assert result["data_source"] == "KoBo"
                assert result["imported_by"] == self.user.get_full_name()

    def test_retrieve_registration(self) -> None:
        self.client.force_authenticate(user=self.user)
        rdi = RegistrationDataImportFactory(
            business_area=self.business_area,
            program=self.program,
            name="Test RDI",
            status=RegistrationDataImport.IN_REVIEW,
            data_source=RegistrationDataImport.XLS,
            imported_by=self.user,
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

        url = reverse(
            "api:registration-data:registration-data-imports-detail",
            args=["afghanistan", self.program.slug, rdi.id],
        )

        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == rdi.name
        assert response.data["id"] == str(rdi.id)

        assert response.data["status_display"] == "In Review"
        assert response.data["data_source"] == "Excel"
        assert response.data["imported_by"] == self.user.get_full_name()

        batch_duplicates = response.data["batch_duplicates_count_and_percentage"]
        assert len(batch_duplicates) == 2
        assert batch_duplicates[0]["count"] == 5
        assert round(batch_duplicates[0]["percentage"]) == 10
        assert batch_duplicates[1]["count"] == 4
        assert round(batch_duplicates[1]["percentage"]) == 8.0

        batch_unique = response.data["batch_unique_count_and_percentage"]
        assert len(batch_unique) == 2
        assert batch_unique[0]["count"] == 45
        assert round(batch_unique[0]["percentage"]) == 90
        assert batch_unique[1]["count"] == 46
        assert round(batch_unique[1]["percentage"]) == 92

        gr_duplicates = response.data["golden_record_duplicates_count_and_percentage"]
        assert gr_duplicates[0]["count"] == 3
        assert round(gr_duplicates[0]["percentage"]) == 6

        gr_possible_duplicates = response.data["golden_record_possible_duplicates_count_and_percentage"]
        assert len(gr_possible_duplicates) == 2
        assert gr_possible_duplicates[0]["count"] == 2
        assert round(gr_possible_duplicates[0]["percentage"]) == 4
        assert gr_possible_duplicates[1]["count"] == 3
        assert round(gr_possible_duplicates[1]["percentage"]) == 6

        gr_unique = response.data["golden_record_unique_count_and_percentage"]
        assert len(gr_unique) == 2
        assert gr_unique[0]["count"] == 45
        assert round(gr_unique[0]["percentage"]) == 90
        assert gr_unique[1]["count"] == 47
        assert round(gr_unique[1]["percentage"]) == 94

        assert "admin_url" in response.data
        assert response.data["admin_url"]

    @patch("hope.apps.registration_datahub.celery_tasks.merge_registration_data_import_task.delay")
    def test_merge_rdi(self, mock_merge_task: Mock) -> None:
        self.client.force_authenticate(user=self.user)
        rdi = RegistrationDataImportFactory(
            business_area=self.business_area,
            program=self.program,
            name="Test RDI",
            status=RegistrationDataImport.IN_REVIEW,
        )

        url = reverse(
            "api:registration-data:registration-data-imports-merge",
            args=["afghanistan", self.program.slug, rdi.id],
        )

        response = self.client.post(url, {}, format="json")
        assert response.status_code == status.HTTP_200_OK
        assert response.data == {"message": "Registration Data Import Merge Scheduled"}

        rdi.refresh_from_db()
        assert rdi.status == RegistrationDataImport.MERGE_SCHEDULED
        mock_merge_task.assert_called_once_with(registration_data_import_id=rdi.id)

    def test_merge_rdi_with_invalid_status(self) -> None:
        self.client.force_authenticate(user=self.user)
        rdi = RegistrationDataImportFactory(
            business_area=self.business_area,
            program=self.program,
            name="Test RDI",
            status=RegistrationDataImport.DEDUPLICATION,
        )

        url = reverse(
            "api:registration-data:registration-data-imports-merge",
            args=["afghanistan", self.program.slug, rdi.id],
        )

        response = self.client.post(url, {}, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

        rdi.refresh_from_db()
        assert rdi.status == RegistrationDataImport.DEDUPLICATION

    def test_erase_rdi(self) -> None:
        self.client.force_authenticate(user=self.user)
        rdi = RegistrationDataImportFactory(
            business_area=self.business_area,
            program=self.program,
            name="Test RDI",
            status=RegistrationDataImport.IMPORT_ERROR,
        )

        household, individuals = create_household_and_individuals(
            household_data={
                "registration_data_import": rdi,
                "program": self.program,
                "business_area": self.business_area,
            },
            individuals_data=[
                {"program": self.program, "registration_data_import": rdi},
                {"program": self.program, "registration_data_import": rdi},
            ],
        )

        assert Household.all_objects.filter(registration_data_import=rdi).count() == 1
        assert Individual.all_objects.filter(registration_data_import=rdi).count() == 2

        url = reverse(
            "api:registration-data:registration-data-imports-erase",
            args=["afghanistan", self.program.slug, rdi.id],
        )

        response = self.client.post(url, {}, format="json")
        assert response.status_code == status.HTTP_200_OK
        assert response.data == {"message": "Registration Data Import Erased"}

        assert Household.all_objects.filter(registration_data_import=rdi).count() == 0

        rdi.refresh_from_db()
        assert rdi.erased

    def test_erase_rdi_with_invalid_status(self) -> None:
        self.client.force_authenticate(user=self.user)
        rdi = RegistrationDataImportFactory(
            business_area=self.business_area,
            program=self.program,
            name="Test RDI",
            status=RegistrationDataImport.IN_REVIEW,
        )

        household, individuals = create_household_and_individuals(
            household_data={
                "registration_data_import": rdi,
                "program": self.program,
                "business_area": self.business_area,
            },
            individuals_data=[
                {"program": self.program, "registration_data_import": rdi},
            ],
        )

        url = reverse(
            "api:registration-data:registration-data-imports-erase",
            args=["afghanistan", self.program.slug, rdi.id],
        )

        response = self.client.post(url, {}, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

        assert Household.all_objects.filter(registration_data_import=rdi).count() == 1

        rdi.refresh_from_db()
        assert not rdi.erased

    def test_refuse_rdi(self) -> None:
        self.client.force_authenticate(user=self.user)
        rdi = RegistrationDataImportFactory(
            business_area=self.business_area,
            program=self.program,
            name="Test RDI",
            status=RegistrationDataImport.IN_REVIEW,
        )

        household, individuals = create_household_and_individuals(
            household_data={
                "registration_data_import": rdi,
                "program": self.program,
                "business_area": self.business_area,
            },
            individuals_data=[
                {"program": self.program, "registration_data_import": rdi},
                {"program": self.program, "registration_data_import": rdi},
            ],
        )

        assert Household.all_objects.filter(registration_data_import=rdi).count() == 1
        assert Individual.all_objects.filter(registration_data_import=rdi).count() == 2

        url = reverse(
            "api:registration-data:registration-data-imports-refuse",
            args=["afghanistan", self.program.slug, rdi.id],
        )

        response = self.client.post(url, {"reason": "Testing refuse endpoint"}, format="json")
        assert response.status_code == status.HTTP_200_OK
        assert response.data == {"message": "Registration Data Import Refused"}

        assert Household.all_objects.filter(registration_data_import=rdi).count() == 0

        rdi.refresh_from_db()
        assert rdi.status == RegistrationDataImport.REFUSED_IMPORT
        assert rdi.refuse_reason == "Testing refuse endpoint"

    def test_refuse_rdi_with_invalid_status(self) -> None:
        self.client.force_authenticate(user=self.user)
        rdi = RegistrationDataImportFactory(
            business_area=self.business_area,
            program=self.program,
            name="Test RDI",
            status=RegistrationDataImport.DEDUPLICATION,
        )

        household, individuals = create_household_and_individuals(
            household_data={
                "registration_data_import": rdi,
                "program": self.program,
                "business_area": self.business_area,
            },
            individuals_data=[
                {"program": self.program, "registration_data_import": rdi},
            ],
        )

        url = reverse(
            "api:registration-data:registration-data-imports-refuse",
            args=["afghanistan", self.program.slug, rdi.id],
        )

        response = self.client.post(url, {"reason": "Testing refuse endpoint"}, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

        assert Household.all_objects.filter(registration_data_import=rdi).count() == 1

        rdi.refresh_from_db()
        assert rdi.status == RegistrationDataImport.DEDUPLICATION

    @patch("hope.apps.registration_datahub.celery_tasks.rdi_deduplication_task.delay")
    def test_deduplicate_rdi(self, mock_deduplicate_task: Mock) -> None:
        self.client.force_authenticate(user=self.user)
        rdi = RegistrationDataImportFactory(
            business_area=self.business_area,
            program=self.program,
            name="Test RDI",
            status=RegistrationDataImport.DEDUPLICATION_FAILED,
        )

        url = reverse(
            "api:registration-data:registration-data-imports-deduplicate",
            args=["afghanistan", self.program.slug, rdi.id],
        )

        response = self.client.post(url, {}, format="json")
        assert response.status_code == status.HTTP_200_OK

        rdi.refresh_from_db()
        assert rdi.status == RegistrationDataImport.DEDUPLICATION

        mock_deduplicate_task.assert_called_once_with(registration_data_import_id=str(rdi.id))

    def test_deduplicate_rdi_with_invalid_status(self) -> None:
        self.client.force_authenticate(user=self.user)
        rdi = RegistrationDataImportFactory(
            business_area=self.business_area,
            program=self.program,
            name="Test RDI",
            status=RegistrationDataImport.IN_REVIEW,
        )

        url = reverse(
            "api:registration-data:registration-data-imports-deduplicate",
            args=["afghanistan", self.program.slug, rdi.id],
        )

        response = self.client.post(url, {}, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

        rdi.refresh_from_db()
        assert rdi.status == RegistrationDataImport.IN_REVIEW

    def test_status_choices(self) -> None:
        self.client.force_authenticate(user=self.user)
        url = reverse(
            "api:registration-data:registration-data-imports-status-choices",
            args=["afghanistan", self.program.slug],
        )
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data, list)
        assert all("name" in c and "value" in c for c in response.data)

    @patch("hope.apps.registration_datahub.celery_tasks.validate_xlsx_import_task.delay")
    def test_upload_xlsx_file(self, mock_validate_task: Mock) -> None:
        self.client.force_authenticate(user=self.user)
        url = reverse(
            "api:registration-data:import-data-upload-upload-xlsx-file",
            args=["afghanistan", self.program.slug],
        )

        # Create a test XLSX file
        file_content = b"test xlsx content"
        uploaded_file = SimpleUploadedFile(
            "test_data.xlsx",
            file_content,
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

        with capture_on_commit_callbacks(execute=True):
            response = self.client.post(url, {"file": uploaded_file}, format="multipart")

        assert response.status_code == status.HTTP_201_CREATED

        # Check response contains required fields
        assert "id" in response.data
        assert "status" in response.data
        assert response.data["data_type"] == ImportData.XLSX

        # Check ImportData was created
        import_data = ImportData.objects.get(id=response.data["id"])
        assert import_data.status == ImportData.STATUS_PENDING
        assert import_data.data_type == ImportData.XLSX
        assert import_data.business_area_slug == self.business_area.slug
        assert import_data.created_by_id == self.user.id

        # Check celery task was called
        mock_validate_task.assert_called_once()
        call_args = mock_validate_task.call_args[0]
        assert call_args[0] == import_data.id
        assert call_args[1] == str(self.program.id)

    @patch("hope.apps.registration_datahub.celery_tasks.pull_kobo_submissions_task.delay")
    def test_save_kobo_import_data(self, mock_pull_task: Mock) -> None:
        self.client.force_authenticate(user=self.user)
        url = reverse(
            "api:registration-data:kobo-import-data-upload-save-kobo-import-data",
            args=["afghanistan", self.program.slug],
        )

        data = {
            "uid": "test_kobo_asset_123",
            "only_active_submissions": True,
            "pull_pictures": False,
        }

        with capture_on_commit_callbacks(execute=True):
            response = self.client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED

        # Check response contains required fields
        assert "id" in response.data
        assert "status" in response.data
        assert response.data["kobo_asset_id"] == "test_kobo_asset_123"
        assert response.data["only_active_submissions"]
        assert not response.data["pull_pictures"]

        # Check KoboImportData was created
        kobo_import_data = KoboImportData.objects.get(id=response.data["id"])
        assert kobo_import_data.status == ImportData.STATUS_PENDING
        assert kobo_import_data.data_type == ImportData.JSON
        assert kobo_import_data.kobo_asset_id == "test_kobo_asset_123"
        assert kobo_import_data.only_active_submissions
        assert not kobo_import_data.pull_pictures
        assert kobo_import_data.business_area_slug == self.business_area.slug
        assert kobo_import_data.created_by_id == self.user.id

        # Check celery task was called
        mock_pull_task.assert_called_once()
        call_args = mock_pull_task.call_args[0]
        assert call_args[0] == kobo_import_data.id
        assert call_args[1] == str(self.program.id)

    @patch("hope.apps.registration_datahub.celery_tasks.registration_xlsx_import_task.delay")
    def test_registration_xlsx_import(self, mock_import_task: Mock) -> None:
        self.client.force_authenticate(user=self.user)

        # Create ImportData that's ready for import
        import_data = ImportDataFactory(
            status=ImportData.STATUS_FINISHED,
            business_area_slug=self.business_area.slug,
            data_type=ImportData.XLSX,
            number_of_households=5,
            number_of_individuals=15,
        )

        url = reverse(
            "api:registration-data:registration-data-imports-registration-xlsx-import",
            args=["afghanistan", self.program.slug],
        )

        data = {
            "import_data_id": str(import_data.id),
            "name": "Test XLSX Import",
            "screen_beneficiary": True,
        }

        with capture_on_commit_callbacks(execute=True):
            response = self.client.post(url, data, format="json")

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
        assert rdi.program == self.program
        assert rdi.imported_by == self.user

        # Check celery task was called
        mock_import_task.assert_called_once()

    def test_registration_xlsx_import_import_data_not_found(self) -> None:
        self.client.force_authenticate(user=self.user)

        url = reverse(
            "api:registration-data:registration-data-imports-registration-xlsx-import",
            args=["afghanistan", self.program.slug],
        )

        data = {
            "import_data_id": "00000000-0000-0000-0000-000000000000",
            "name": "Test XLSX Import",
            "screen_beneficiary": True,
        }

        response = self.client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Import data not found" in response.data

    def test_registration_xlsx_import_import_data_not_ready(self) -> None:
        self.client.force_authenticate(user=self.user)

        # Create ImportData that's not ready
        import_data = ImportDataFactory(
            status=ImportData.STATUS_PENDING,
            business_area_slug=self.business_area.slug,
        )

        url = reverse(
            "api:registration-data:registration-data-imports-registration-xlsx-import",
            args=["afghanistan", self.program.slug],
        )

        data = {
            "import_data_id": str(import_data.id),
            "name": "Test XLSX Import",
            "screen_beneficiary": True,
        }

        response = self.client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Import data is not ready for import" in response.data

    def test_registration_xlsx_import_program_finished(self) -> None:
        self.client.force_authenticate(user=self.user)

        # Create ImportData that's ready for import
        import_data = ImportDataFactory(
            status=ImportData.STATUS_FINISHED,
            business_area_slug=self.business_area.slug,
        )

        # Set program to finished
        self.program.status = Program.FINISHED
        self.program.save()

        url = reverse(
            "api:registration-data:registration-data-imports-registration-xlsx-import",
            args=["afghanistan", self.program.slug],
        )

        data = {
            "import_data_id": str(import_data.id),
            "name": "Test XLSX Import",
            "screen_beneficiary": True,
        }

        response = self.client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "In order to perform this action, program status must not be finished." in response.data

    @patch("hope.apps.registration_datahub.celery_tasks.registration_kobo_import_task.delay")
    def test_registration_kobo_import(self, mock_import_task: Mock) -> None:
        self.client.force_authenticate(user=self.user)

        # Create KoboImportData that's ready for import
        kobo_import_data = KoboImportDataFactory(
            status=ImportData.STATUS_FINISHED,
            business_area_slug=self.business_area.slug,
            kobo_asset_id="test_kobo_asset_456",
            number_of_households=8,
            number_of_individuals=25,
        )

        url = reverse(
            "api:registration-data:registration-data-imports-registration-kobo-import",
            args=["afghanistan", self.program.slug],
        )

        data = {
            "import_data_id": str(kobo_import_data.id),
            "name": "Test Kobo Import",
            "pull_pictures": True,
            "screen_beneficiary": False,
        }

        with capture_on_commit_callbacks(execute=True):
            response = self.client.post(url, data, format="json")

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
        assert rdi.program == self.program
        assert rdi.imported_by == self.user

        # Check celery task was called
        mock_import_task.assert_called_once()

    def test_registration_kobo_import_kobo_data_not_found(self) -> None:
        self.client.force_authenticate(user=self.user)

        url = reverse(
            "api:registration-data:registration-data-imports-registration-kobo-import",
            args=["afghanistan", self.program.slug],
        )

        data = {
            "import_data_id": "00000000-0000-0000-0000-000000000000",
            "name": "Test Kobo Import",
            "pull_pictures": True,
            "screen_beneficiary": False,
        }

        response = self.client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Kobo import data not found" in response.data

    def test_registration_kobo_import_kobo_data_not_ready(self) -> None:
        self.client.force_authenticate(user=self.user)

        # Create KoboImportData that's not ready
        kobo_import_data = KoboImportDataFactory(
            status=ImportData.STATUS_PENDING,
            business_area_slug=self.business_area.slug,
        )

        url = reverse(
            "api:registration-data:registration-data-imports-registration-kobo-import",
            args=["afghanistan", self.program.slug],
        )

        data = {
            "import_data_id": str(kobo_import_data.id),
            "name": "Test Kobo Import",
            "pull_pictures": True,
            "screen_beneficiary": False,
        }

        response = self.client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Kobo import data is not ready for import" in response.data

    def test_registration_kobo_import_program_finished(self) -> None:
        self.client.force_authenticate(user=self.user)

        # Create KoboImportData that's ready for import
        kobo_import_data = KoboImportDataFactory(
            status=ImportData.STATUS_FINISHED,
            business_area_slug=self.business_area.slug,
        )

        # Set program to finished
        self.program.status = Program.FINISHED
        self.program.save()

        url = reverse(
            "api:registration-data:registration-data-imports-registration-kobo-import",
            args=["afghanistan", self.program.slug],
        )

        data = {
            "import_data_id": str(kobo_import_data.id),
            "name": "Test Kobo Import",
            "pull_pictures": True,
            "screen_beneficiary": False,
        }

        response = self.client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "In order to perform this action, program status must not be finished." in response.data

    def test_import_data_retrieve(self) -> None:
        self.client.force_authenticate(user=self.user)

        # Create ImportData with validation errors
        import_data = ImportDataFactory(
            business_area_slug=self.business_area.slug,
            status=ImportData.STATUS_FINISHED,
            validation_errors='[{"row_number": 1, "header": "name", "message": "Name is required"}]',
            error="Test error message",
        )

        url = reverse(
            "api:registration-data:import-data-detail",
            args=["afghanistan", import_data.id],
        )

        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK

        # Check response structure
        assert response.data["id"] == str(import_data.id)
        assert response.data["status"] == import_data.status
        assert response.data["data_type"] == import_data.data_type
        assert response.data["error"] == "Test error message"

        # Check validation errors are parsed
        assert "xlsx_validation_errors" in response.data
        validation_errors = response.data["xlsx_validation_errors"]
        assert len(validation_errors) == 1
        assert validation_errors[0]["row_number"] == 1
        assert validation_errors[0]["header"] == "name"
        assert validation_errors[0]["message"] == "Name is required"

    def test_kobo_import_data_retrieve(self) -> None:
        self.client.force_authenticate(user=self.user)

        # Create KoboImportData with validation errors
        kobo_import_data = KoboImportDataFactory(
            business_area_slug=self.business_area.slug,
            status=ImportData.STATUS_FINISHED,
            kobo_asset_id="test_asset_123",
            validation_errors='[{"header": "age", "message": "Age must be a number"}]',
            only_active_submissions=True,
            pull_pictures=False,
        )

        url = reverse(
            "api:registration-data:kobo-import-data-detail",
            args=["afghanistan", kobo_import_data.id],
        )

        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK

        # Check response structure
        assert response.data["id"] == str(kobo_import_data.id)
        assert response.data["status"] == kobo_import_data.status
        assert response.data["kobo_asset_id"] == "test_asset_123"
        assert response.data["only_active_submissions"]
        assert not response.data["pull_pictures"]

        # Check validation errors are parsed
        assert "kobo_validation_errors" in response.data
        validation_errors = response.data["kobo_validation_errors"]
        assert len(validation_errors) == 1
        assert validation_errors[0]["header"] == "age"
        assert validation_errors[0]["message"] == "Age must be a number"

    def test_import_data_retrieve_different_business_area(self) -> None:
        self.client.force_authenticate(user=self.user)

        # Create ImportData in different business area
        import_data = ImportDataFactory(
            business_area_slug="different_area",
            status=ImportData.STATUS_FINISHED,
        )

        url = reverse(
            "api:registration-data:import-data-detail",
            args=["afghanistan", import_data.id],
        )

        response = self.client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_kobo_import_data_retrieve_different_business_area(self) -> None:
        self.client.force_authenticate(user=self.user)

        # Create KoboImportData in different business area
        kobo_import_data = KoboImportDataFactory(
            business_area_slug="different_area",
            status=ImportData.STATUS_FINISHED,
        )

        url = reverse(
            "api:registration-data:kobo-import-data-detail",
            args=["afghanistan", kobo_import_data.id],
        )

        response = self.client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND


class RegistrationDataImportPermissionTest(HOPEApiTestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        unicef_partner = PartnerFactory(name="UNICEF")
        unicef = PartnerFactory(name="UNICEF HQ", parent=unicef_partner)
        cls.user = UserFactory(
            username="Hope_Test_DRF",
            password="HopePass",
            partner=unicef,
            is_superuser=False,
        )
        cls.program = ProgramFactory(
            name="Test Program",
            status=Program.ACTIVE,
        )

        # program - screen beneficiary = True
        cls.program.sanction_lists.add(SanctionListFactory(name="Test Sanction List"))

        cls.rdi = RegistrationDataImportFactory(
            business_area=cls.business_area,
            program=cls.program,
            name="Test RDI",
            status=RegistrationDataImport.IN_REVIEW,
        )
        cls.client = APIClient()

    def test_permission_checks_list(self) -> None:
        self.client.force_authenticate(user=self.user)

        url = reverse(
            "api:registration-data:registration-data-imports-list",
            args=["afghanistan", self.program.slug],
        )

        response = self.client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

        role, _ = Role.objects.update_or_create(
            name="TestPermissionListRole",
            defaults={"permissions": [Permissions.RDI_VIEW_LIST.value]},
        )
        RoleAssignment.objects.get_or_create(user=self.user, role=role, business_area=self.business_area)

        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK

    def test_permission_checks_retrieve(self) -> None:
        self.client.force_authenticate(user=self.user)

        url = reverse(
            "api:registration-data:registration-data-imports-detail",
            args=["afghanistan", self.program.slug, self.rdi.id],
        )

        response = self.client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

        role, _ = Role.objects.update_or_create(
            name="TestPermissionRetrieveRole",
            defaults={"permissions": [Permissions.RDI_VIEW_DETAILS.value]},
        )
        RoleAssignment.objects.get_or_create(user=self.user, role=role, business_area=self.business_area)

        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK

    def test_permission_checks_merge(self) -> None:
        self.client.force_authenticate(user=self.user)

        rdi_to_merge = RegistrationDataImportFactory(
            business_area=self.business_area,
            program=self.program,
            name="Test RDI for Merge",
            status=RegistrationDataImport.IN_REVIEW,
        )

        url = reverse(
            "api:registration-data:registration-data-imports-merge",
            args=["afghanistan", self.program.slug, rdi_to_merge.id],
        )

        response = self.client.post(url, {}, format="json")
        assert response.status_code == status.HTTP_403_FORBIDDEN

        role, _ = Role.objects.update_or_create(
            name="TestPermissionMergeRole",
            defaults={"permissions": [Permissions.RDI_MERGE_IMPORT.value]},
        )
        RoleAssignment.objects.get_or_create(user=self.user, role=role, business_area=self.business_area)

        response = self.client.post(url, {}, format="json")
        assert response.status_code == status.HTTP_200_OK

    def test_permission_checks_erase(self) -> None:
        self.client.force_authenticate(user=self.user)

        rdi_to_erase = RegistrationDataImportFactory(
            business_area=self.business_area,
            program=self.program,
            name="Test RDI for Erase",
            status=RegistrationDataImport.IMPORT_ERROR,
        )

        url = reverse(
            "api:registration-data:registration-data-imports-erase",
            args=["afghanistan", self.program.slug, rdi_to_erase.id],
        )

        response = self.client.post(url, {}, format="json")
        assert response.status_code == status.HTTP_403_FORBIDDEN

        role, _ = Role.objects.update_or_create(
            name="TestPermissionEraseRole",
            defaults={"permissions": [Permissions.RDI_REFUSE_IMPORT.value]},
        )
        RoleAssignment.objects.get_or_create(user=self.user, role=role, business_area=self.business_area)

        response = self.client.post(url, {}, format="json")
        assert response.status_code == status.HTTP_200_OK

    def test_permission_checks_refuse(self) -> None:
        self.client.force_authenticate(user=self.user)

        rdi_to_refuse = RegistrationDataImportFactory(
            business_area=self.business_area,
            program=self.program,
            name="Test RDI for Refuse",
            status=RegistrationDataImport.IN_REVIEW,
        )

        url = reverse(
            "api:registration-data:registration-data-imports-refuse",
            args=["afghanistan", self.program.slug, rdi_to_refuse.id],
        )

        response = self.client.post(url, {"reason": "Test reason"}, format="json")
        assert response.status_code == status.HTTP_403_FORBIDDEN

        role, _ = Role.objects.update_or_create(
            name="TestPermissionRefuseRole",
            defaults={"permissions": [Permissions.RDI_REFUSE_IMPORT.value]},
        )
        RoleAssignment.objects.get_or_create(user=self.user, role=role, business_area=self.business_area)

        response = self.client.post(url, {"reason": "Test reason"}, format="json")
        assert response.status_code == status.HTTP_200_OK

    def test_permission_checks_deduplicate(self) -> None:
        self.client.force_authenticate(user=self.user)

        rdi_to_deduplicate = RegistrationDataImportFactory(
            business_area=self.business_area,
            program=self.program,
            name="Test RDI for Deduplicate",
            status=RegistrationDataImport.DEDUPLICATION_FAILED,
        )

        url = reverse(
            "api:registration-data:registration-data-imports-deduplicate",
            args=["afghanistan", self.program.slug, rdi_to_deduplicate.id],
        )

        response = self.client.post(url, {}, format="json")
        assert response.status_code == status.HTTP_403_FORBIDDEN

        role, _ = Role.objects.update_or_create(
            name="TestPermissionDeduplicateRole",
            defaults={"permissions": [Permissions.RDI_RERUN_DEDUPE.value]},
        )
        RoleAssignment.objects.get_or_create(user=self.user, role=role, business_area=self.business_area)

        response = self.client.post(url, {}, format="json")
        assert response.status_code == status.HTTP_200_OK

    def test_permission_checks_status_choices(self) -> None:
        self.client.force_authenticate(user=self.user)
        url = reverse(
            "api:registration-data:registration-data-imports-status-choices",
            args=["afghanistan", self.program.slug],
        )
        # Should be forbidden without permission
        response = self.client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

        # Grant permission and try again
        role, _ = Role.objects.update_or_create(
            name="TestPermissionStatusChoicesRole",
            defaults={"permissions": [Permissions.RDI_VIEW_LIST.value]},
        )
        RoleAssignment.objects.get_or_create(user=self.user, role=role, business_area=self.business_area)

        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data, list)
        assert all("name" in c and "value" in c for c in response.data)

    @patch("hope.apps.registration_datahub.celery_tasks.registration_program_population_import_task.delay")
    def test_create_registration_data_import(self, mock_registration_task: Mock) -> None:
        self.client.force_authenticate(user=self.user)
        # Grant permission for create
        role, _ = Role.objects.update_or_create(
            name="TestPermissionCreateRole",
            defaults={"permissions": [Permissions.RDI_IMPORT_DATA.value]},
        )
        RoleAssignment.objects.get_or_create(user=self.user, role=role, business_area=self.business_area)
        # Create a source program to import from, matching beneficiary group and data collecting type
        compatible_dct = DataCollectingTypeFactory(code="compatible_dct")
        import_from_program = ProgramFactory(
            name="Source Program",
            status=Program.ACTIVE,
            biometric_deduplication_enabled=True,
            beneficiary_group=self.program.beneficiary_group,
            data_collecting_type=compatible_dct,
        )
        import_from_program.data_collecting_type.compatible_types.add(self.program.data_collecting_type)
        # Create at least one household and individual in the source program
        create_household_and_individuals(
            household_data={
                "program": import_from_program,
                "business_area": self.business_area,
            },
            individuals_data=[
                {"program": import_from_program, "business_area": self.business_area},
            ],
        )
        create_household_and_individuals(
            household_data={
                "program": import_from_program,
                "business_area": self.business_area,
            },
            individuals_data=[
                {"program": import_from_program, "business_area": self.business_area},
                {"program": import_from_program, "business_area": self.business_area},
            ],
        )
        url = reverse(
            "api:registration-data:registration-data-imports-list",
            args=["afghanistan", self.program.slug],
        )
        data = {
            "import_from_program_id": str(import_from_program.id),
            "import_from_ids": "",  # No specific IDs, import all
            "name": "Test Import",
            "screen_beneficiary": True,
        }
        with capture_on_commit_callbacks(execute=True):
            response = self.client.post(url, data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["name"] == "Test Import"
        assert response.data["number_of_households"] == 2
        assert response.data["number_of_individuals"] == 3
        assert "id" in response.data
        mock_registration_task.assert_called_once()

    @patch("hope.apps.registration_datahub.celery_tasks.registration_program_population_import_task.delay")
    def test_create_registration_data_import_with_ids_filter(self, mock_registration_task: Mock) -> None:
        self.client.force_authenticate(user=self.user)
        # Grant permission for create
        role, _ = Role.objects.update_or_create(
            name="TestPermissionCreateRole",
            defaults={"permissions": [Permissions.RDI_IMPORT_DATA.value]},
        )
        RoleAssignment.objects.get_or_create(user=self.user, role=role, business_area=self.business_area)
        # Create a source program to import from, matching beneficiary group and data collecting type
        compatible_dct = DataCollectingTypeFactory(code="compatible_dct")
        import_from_program = ProgramFactory(
            name="Source Program",
            status=Program.ACTIVE,
            biometric_deduplication_enabled=True,
            beneficiary_group=self.program.beneficiary_group,
            data_collecting_type=compatible_dct,
        )
        import_from_program.data_collecting_type.compatible_types.add(self.program.data_collecting_type)
        # Create at least one household and individual in the source program
        create_household_and_individuals(
            household_data={
                "program": import_from_program,
                "business_area": self.business_area,
            },
            individuals_data=[
                {"program": import_from_program, "business_area": self.business_area},
            ],
        )
        household, individuals = create_household_and_individuals(
            household_data={
                "program": import_from_program,
                "business_area": self.business_area,
            },
            individuals_data=[
                {"program": import_from_program, "business_area": self.business_area},
                {"program": import_from_program, "business_area": self.business_area},
            ],
        )
        url = reverse(
            "api:registration-data:registration-data-imports-list",
            args=["afghanistan", self.program.slug],
        )
        data = {
            "import_from_program_id": str(import_from_program.id),
            "import_from_ids": f"{household.unicef_id}",  # Only 1 household
            "name": "Test Import",
            "screen_beneficiary": True,
        }
        with capture_on_commit_callbacks(execute=True):
            response = self.client.post(url, data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["name"] == "Test Import"
        assert response.data["number_of_households"] == 1
        assert response.data["number_of_individuals"] == 2
        mock_registration_task.assert_called_once()

    @patch("hope.apps.registration_datahub.celery_tasks.registration_program_population_import_task.delay")
    def test_create_registration_data_import_invalid_bg(self, mock_registration_task: Mock) -> None:
        self.client.force_authenticate(user=self.user)
        role, _ = Role.objects.update_or_create(
            name="TestPermissionCreateRole",
            defaults={"permissions": [Permissions.RDI_IMPORT_DATA.value]},
        )
        RoleAssignment.objects.get_or_create(user=self.user, role=role, business_area=self.business_area)
        import_from_program = ProgramFactory(
            name="Source Program",
            status=Program.ACTIVE,
            biometric_deduplication_enabled=True,
            beneficiary_group=BeneficiaryGroupFactory(
                name="Different Beneficiary Group",
            ),
            data_collecting_type=self.program.data_collecting_type,
        )
        create_household_and_individuals(
            household_data={
                "program": import_from_program,
                "business_area": self.business_area,
            },
            individuals_data=[
                {"program": import_from_program, "business_area": self.business_area},
            ],
        )
        url = reverse(
            "api:registration-data:registration-data-imports-list",
            args=["afghanistan", self.program.slug],
        )
        data = {
            "import_from_program_id": str(import_from_program.id),
            "import_from_ids": "",
            "name": "Test Import",
            "screen_beneficiary": True,
        }
        with capture_on_commit_callbacks(execute=True):
            response = self.client.post(url, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Cannot import data from a program with a different Beneficiary Group." in response.data

    @patch("hope.apps.registration_datahub.celery_tasks.registration_program_population_import_task.delay")
    def test_create_registration_data_import_invalid_dct(self, mock_registration_task: Mock) -> None:
        self.client.force_authenticate(user=self.user)
        role, _ = Role.objects.update_or_create(
            name="TestPermissionCreateRole",
            defaults={"permissions": [Permissions.RDI_IMPORT_DATA.value]},
        )
        RoleAssignment.objects.get_or_create(user=self.user, role=role, business_area=self.business_area)
        import_from_program = ProgramFactory(
            name="Source Program",
            status=Program.ACTIVE,
            biometric_deduplication_enabled=True,
            beneficiary_group=self.program.beneficiary_group,
            data_collecting_type=DataCollectingTypeFactory(
                code="incompatible_dct",
            ),
        )
        create_household_and_individuals(
            household_data={
                "program": import_from_program,
                "business_area": self.business_area,
            },
            individuals_data=[
                {"program": import_from_program, "business_area": self.business_area},
            ],
        )
        url = reverse(
            "api:registration-data:registration-data-imports-list",
            args=["afghanistan", self.program.slug],
        )
        data = {
            "import_from_program_id": str(import_from_program.id),
            "import_from_ids": "",
            "name": "Test Import",
            "screen_beneficiary": True,
        }
        with capture_on_commit_callbacks(execute=True):
            response = self.client.post(url, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Cannot import data from a program with not compatible data collecting type." in response.data

    @patch("hope.apps.registration_datahub.celery_tasks.registration_program_population_import_task.delay")
    def test_create_registration_data_import_program_finished(self, mock_registration_task: Mock) -> None:
        self.client.force_authenticate(user=self.user)
        role, _ = Role.objects.update_or_create(
            name="TestPermissionCreateRole",
            defaults={"permissions": [Permissions.RDI_IMPORT_DATA.value]},
        )
        RoleAssignment.objects.get_or_create(user=self.user, role=role, business_area=self.business_area)
        import_from_program = ProgramFactory(
            name="Source Program",
            status=Program.ACTIVE,
            biometric_deduplication_enabled=True,
            beneficiary_group=self.program.beneficiary_group,
            data_collecting_type=self.program.data_collecting_type,
        )
        create_household_and_individuals(
            household_data={
                "program": import_from_program,
                "business_area": self.business_area,
            },
            individuals_data=[
                {"program": import_from_program, "business_area": self.business_area},
            ],
        )
        self.program.status = Program.FINISHED
        self.program.save()
        url = reverse(
            "api:registration-data:registration-data-imports-list",
            args=["afghanistan", self.program.slug],
        )
        data = {
            "import_from_program_id": str(import_from_program.id),
            "import_from_ids": "",
            "name": "Test Import",
            "screen_beneficiary": True,
        }
        with capture_on_commit_callbacks(execute=True):
            response = self.client.post(url, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "In order to perform this action, program status must not be finished." in response.data

    @patch("hope.apps.registration_datahub.celery_tasks.registration_program_population_import_task.delay")
    def test_create_registration_data_import_cannot_check_against_sanction_list(
        self, mock_registration_task: Mock
    ) -> None:
        self.client.force_authenticate(user=self.user)
        role, _ = Role.objects.update_or_create(
            name="TestPermissionCreateRole",
            defaults={"permissions": [Permissions.RDI_IMPORT_DATA.value]},
        )
        SanctionList.objects.all().delete()  # screen_beneficiary=False
        assert self.program.screen_beneficiary is False
        RoleAssignment.objects.get_or_create(user=self.user, role=role, business_area=self.business_area)
        import_from_program = ProgramFactory(
            name="Source Program",
            status=Program.ACTIVE,
            biometric_deduplication_enabled=True,
            beneficiary_group=self.program.beneficiary_group,
            data_collecting_type=self.program.data_collecting_type,
        )
        create_household_and_individuals(
            household_data={
                "program": import_from_program,
                "business_area": self.business_area,
            },
            individuals_data=[
                {"program": import_from_program, "business_area": self.business_area},
            ],
        )
        url = reverse(
            "api:registration-data:registration-data-imports-list",
            args=["afghanistan", self.program.slug],
        )
        data = {
            "import_from_program_id": str(import_from_program.id),
            "import_from_ids": "",
            "name": "Test Import",
            "screen_beneficiary": True,
        }
        with capture_on_commit_callbacks(execute=True):
            response = self.client.post(url, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Cannot check against sanction list." in response.data

    @patch("hope.apps.registration_datahub.celery_tasks.registration_program_population_import_task.delay")
    def test_create_registration_data_import_0_objects(self, mock_registration_task: Mock) -> None:
        self.client.force_authenticate(user=self.user)
        role, _ = Role.objects.update_or_create(
            name="TestPermissionCreateRole",
            defaults={"permissions": [Permissions.RDI_IMPORT_DATA.value]},
        )
        RoleAssignment.objects.get_or_create(user=self.user, role=role, business_area=self.business_area)
        import_from_program = ProgramFactory(
            name="Source Program",
            status=Program.ACTIVE,
            biometric_deduplication_enabled=True,
            beneficiary_group=self.program.beneficiary_group,
            data_collecting_type=self.program.data_collecting_type,
        )
        url = reverse(
            "api:registration-data:registration-data-imports-list",
            args=["afghanistan", self.program.slug],
        )
        data = {
            "import_from_program_id": str(import_from_program.id),
            "import_from_ids": "",
            "name": "Test Import",
            "screen_beneficiary": True,
        }
        with capture_on_commit_callbacks(execute=True):
            response = self.client.post(url, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "This action would result in importing 0 households and 0 individuals." in response.data

    def test_permission_checks_upload_xlsx_file(self) -> None:
        self.client.force_authenticate(user=self.user)

        url = reverse(
            "api:registration-data:import-data-upload-upload-xlsx-file",
            args=["afghanistan", self.program.slug],
        )

        file_content = b"test xlsx content"
        uploaded_file = SimpleUploadedFile(
            "test_data.xlsx",
            file_content,
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

        # Should be forbidden without permission
        response = self.client.post(url, {"file": uploaded_file}, format="multipart")
        assert response.status_code == status.HTTP_403_FORBIDDEN

        # Grant permission and try again
        role, _ = Role.objects.update_or_create(
            name="TestPermissionUploadXlsxRole",
            defaults={"permissions": [Permissions.RDI_IMPORT_DATA.value]},
        )
        RoleAssignment.objects.get_or_create(user=self.user, role=role, business_area=self.business_area)

        # Create a fresh file upload
        uploaded_file2 = SimpleUploadedFile(
            "test_data.xlsx",
            file_content,
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        response = self.client.post(url, {"file": uploaded_file2}, format="multipart")
        assert response.status_code == status.HTTP_201_CREATED

    def test_permission_checks_save_kobo_import_data(self) -> None:
        self.client.force_authenticate(user=self.user)

        url = reverse(
            "api:registration-data:kobo-import-data-upload-save-kobo-import-data",
            args=["afghanistan", self.program.slug],
        )

        data = {
            "uid": "test_kobo_asset_123",
            "only_active_submissions": True,
            "pull_pictures": False,
        }

        # Should be forbidden without permission
        response = self.client.post(url, data, format="json")
        assert response.status_code == status.HTTP_403_FORBIDDEN

        # Grant permission and try again
        role, _ = Role.objects.update_or_create(
            name="TestPermissionSaveKoboRole",
            defaults={"permissions": [Permissions.RDI_IMPORT_DATA.value]},
        )
        RoleAssignment.objects.get_or_create(user=self.user, role=role, business_area=self.business_area)

        response = self.client.post(url, data, format="json")
        assert response.status_code == status.HTTP_201_CREATED

    def test_permission_checks_registration_xlsx_import(self) -> None:
        self.client.force_authenticate(user=self.user)

        # Create ImportData that's ready for import
        import_data = ImportDataFactory(
            status=ImportData.STATUS_FINISHED,
            business_area_slug=self.business_area.slug,
        )

        url = reverse(
            "api:registration-data:registration-data-imports-registration-xlsx-import",
            args=["afghanistan", self.program.slug],
        )

        data = {
            "import_data_id": str(import_data.id),
            "name": "Test XLSX Import",
            "screen_beneficiary": True,
        }

        # Should be forbidden without permission
        response = self.client.post(url, data, format="json")
        assert response.status_code == status.HTTP_403_FORBIDDEN

        # Grant permission and try again
        role, _ = Role.objects.update_or_create(
            name="TestPermissionXlsxImportRole",
            defaults={"permissions": [Permissions.RDI_IMPORT_DATA.value]},
        )
        RoleAssignment.objects.get_or_create(user=self.user, role=role, business_area=self.business_area)

        response = self.client.post(url, data, format="json")
        assert response.status_code == status.HTTP_201_CREATED

    def test_permission_checks_registration_kobo_import(self) -> None:
        self.client.force_authenticate(user=self.user)

        # Create KoboImportData that's ready for import
        kobo_import_data = KoboImportDataFactory(
            status=ImportData.STATUS_FINISHED,
            business_area_slug=self.business_area.slug,
        )

        url = reverse(
            "api:registration-data:registration-data-imports-registration-kobo-import",
            args=["afghanistan", self.program.slug],
        )

        data = {
            "import_data_id": str(kobo_import_data.id),
            "name": "Test Kobo Import",
            "pull_pictures": True,
            "screen_beneficiary": False,
        }

        # Should be forbidden without permission
        response = self.client.post(url, data, format="json")
        assert response.status_code == status.HTTP_403_FORBIDDEN

        # Grant permission and try again
        role, _ = Role.objects.update_or_create(
            name="TestPermissionKoboImportRole",
            defaults={"permissions": [Permissions.RDI_IMPORT_DATA.value]},
        )
        RoleAssignment.objects.get_or_create(user=self.user, role=role, business_area=self.business_area)

        response = self.client.post(url, data, format="json")
        assert response.status_code == status.HTTP_201_CREATED

    def test_permission_checks_import_data_retrieve(self) -> None:
        self.client.force_authenticate(user=self.user)

        import_data = ImportDataFactory(business_area_slug=self.business_area.slug)

        url = reverse(
            "api:registration-data:import-data-detail",
            args=["afghanistan", import_data.id],
        )

        # Should be forbidden without permission
        response = self.client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

        # Grant permission and try again
        role, _ = Role.objects.update_or_create(
            name="TestPermissionImportDataRole",
            defaults={"permissions": [Permissions.RDI_VIEW_DETAILS.value]},
        )
        RoleAssignment.objects.get_or_create(user=self.user, role=role, business_area=self.business_area)

        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK

    def test_permission_checks_kobo_import_data_retrieve(self) -> None:
        self.client.force_authenticate(user=self.user)

        kobo_import_data = KoboImportDataFactory(business_area_slug=self.business_area.slug)

        url = reverse(
            "api:registration-data:kobo-import-data-detail",
            args=["afghanistan", kobo_import_data.id],
        )

        # Should be forbidden without permission
        response = self.client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

        # Grant permission and try again
        role, _ = Role.objects.update_or_create(
            name="TestPermissionKoboImportDataRole",
            defaults={"permissions": [Permissions.RDI_VIEW_DETAILS.value]},
        )
        RoleAssignment.objects.get_or_create(user=self.user, role=role, business_area=self.business_area)

        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK

    @patch("hope.apps.registration_datahub.celery_tasks.registration_program_population_import_task.delay")
    def test_create_registration_data_import_permission_denied(self, mock_registration_task: Mock) -> None:
        self.client.force_authenticate(user=self.user)
        # Create a source program to import from, matching beneficiary group and data collecting type
        import_from_program = ProgramFactory(
            name="Source Program",
            status=Program.ACTIVE,
            biometric_deduplication_enabled=True,
            beneficiary_group=self.program.beneficiary_group,
            data_collecting_type=self.program.data_collecting_type,
        )
        # Create at least one household and individual in the source program
        create_household_and_individuals(
            household_data={
                "program": import_from_program,
                "business_area": self.business_area,
            },
            individuals_data=[
                {"program": import_from_program, "business_area": self.business_area},
            ],
        )
        url = reverse(
            "api:registration-data:registration-data-imports-list",
            args=["afghanistan", self.program.slug],
        )
        data = {
            "import_from_program_id": str(import_from_program.id),
            "import_from_ids": "",  # No specific IDs, import all
            "name": "Test Import",
            "screen_beneficiary": True,
        }
        with capture_on_commit_callbacks(execute=True):
            response = self.client.post(url, data, format="json")
        assert response.status_code == status.HTTP_403_FORBIDDEN
        mock_registration_task.assert_not_called()


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
            for _, callback in connections[using].run_on_commit[start_count:]:
                callbacks.append(callback)
                if execute:
                    callback()

            if callback_count == len(connections[using].run_on_commit):
                break
            start_count = callback_count
