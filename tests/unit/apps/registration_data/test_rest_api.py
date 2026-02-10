from contextlib import contextmanager
from typing import Any, Callable, Generator
from unittest.mock import Mock, patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import DEFAULT_DB_ALIAS, connections
from django.urls import reverse
from flags.models import FlagState
from rest_framework import status
from rest_framework.test import APIClient

from extras.test_utils.old_factories.account import PartnerFactory, UserFactory
from extras.test_utils.old_factories.core import DataCollectingTypeFactory
from extras.test_utils.old_factories.household import create_household_and_individuals
from extras.test_utils.old_factories.program import BeneficiaryGroupFactory, ProgramFactory
from extras.test_utils.old_factories.registration_data import (
    ImportDataFactory,
    KoboImportDataFactory,
    RegistrationDataImportFactory,
)
from extras.test_utils.old_factories.sanction_list import SanctionListFactory
from hope.apps.account.permissions import Permissions
from hope.apps.household.documents import IndividualDocumentAfghanistan, get_individual_doc
from hope.apps.registration_data.services.biometric_deduplication import BiometricDeduplicationService
from hope.models import (
    DataCollectingType,
    Household,
    ImportData,
    Individual,
    KoboImportData,
    Program,
    RegistrationDataImport,
    Role,
    RoleAssignment,
    SanctionList,
)
from unit.api.base import HOPEApiTestCase


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
            Permissions.RDI_WEBHOOK_DEDUPLICATION,
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

    @patch("hope.apps.registration_data.celery_tasks.deduplication_engine_process.delay")
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

        RegistrationDataImportFactory(
            program=self.program, deduplication_engine_status=RegistrationDataImport.DEDUP_ENGINE_IN_PROGRESS
        )
        resp = self.client.post(url, {}, format="json")
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert resp.json() == ["Deduplication is already in progress for some RDIs"]

        self.program.biometric_deduplication_enabled = False
        self.program.save()
        resp = self.client.post(url, {}, format="json")
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert resp.json() == ["Biometric deduplication is not enabled for this program"]

    @patch("hope.apps.registration_data.celery_tasks.fetch_biometric_deduplication_results_and_process.delay")
    def test_webhook_deduplication(self, mock_fetch_dedup_results: Mock) -> None:
        self.client.force_authenticate(user=self.user)
        url = reverse(
            "api:registration-data:registration-data-imports-webhook-deduplication",
            args=["afghanistan", self.program.slug],
        )
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK
        mock_fetch_dedup_results.assert_called_once_with(str(self.program.id))

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

    @patch("hope.apps.registration_data.celery_tasks.merge_registration_data_import_task.delay")
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

    @patch("hope.apps.registration_data.api.views.BiometricDeduplicationService")
    @patch("hope.apps.registration_data.api.views.remove_elasticsearch_documents_by_matching_ids")
    def test_erase_rdi(self, mock_remove_es: Mock, mock_biometric_service: Mock) -> None:
        self.client.force_authenticate(user=self.user)
        mock_biometric_service.INDIVIDUALS_REFUSED = BiometricDeduplicationService.INDIVIDUALS_REFUSED
        mock_service = mock_biometric_service.return_value

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

        individual_ids = [ind.id for ind in individuals]

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

        mock_remove_es.assert_called_once()
        es_call_args = mock_remove_es.call_args[0]
        assert set(es_call_args[0]) == set(individual_ids)  # Order doesn't matter
        assert es_call_args[1] == get_individual_doc(self.business_area.slug)

        mock_service.report_individuals_status.assert_called_once()
        report_call_args = mock_service.report_individuals_status.call_args[0]
        assert report_call_args[0] == self.program
        assert set(report_call_args[1]) == {str(_id) for _id in individual_ids}  # Order doesn't matter
        assert report_call_args[2] == mock_biometric_service.INDIVIDUALS_REFUSED

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

    @patch.dict(
        "os.environ",
        {
            "DEDUPLICATION_ENGINE_API_KEY": "dedup_api_key",
            "DEDUPLICATION_ENGINE_API_URL": "http://dedup-fake-url.com",
        },
    )
    @patch(
        "hope.apps.registration_data.services"
        ".biometric_deduplication"
        ".BiometricDeduplicationService"
        ".report_individuals_status"
    )
    @patch("hope.apps.registration_data.api.views.remove_elasticsearch_documents_by_matching_ids")
    def test_refuse_rdi(
        self, remove_elasticsearch_documents_by_matching_ids_moc: Any, report_refused_individuals_mock: Any
    ) -> None:
        FlagState.objects.get_or_create(
            name="BIOMETRIC_DEDUPLICATION_REPORT_INDIVIDUALS_STATUS",
            condition="boolean",
            value="True",
            required=False,
        )

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
        individuals_ids_to_remove = list(
            Individual.all_objects.filter(registration_data_import=rdi).values_list("id", flat=True)
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

        report_refused_individuals_mock.assert_called_once_with(
            rdi.program, [str(_id) for _id in individuals_ids_to_remove], "rejected"
        )
        remove_elasticsearch_documents_by_matching_ids_moc.assert_called_once_with(
            individuals_ids_to_remove, IndividualDocumentAfghanistan
        )

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

    @patch("hope.apps.registration_data.celery_tasks.rdi_deduplication_task.delay")
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

    @patch("hope.apps.registration_data.celery_tasks.validate_xlsx_import_task.delay")
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

    @patch("hope.apps.registration_data.celery_tasks.pull_kobo_submissions_task.delay")
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

    @patch("hope.apps.registration_data.celery_tasks.registration_xlsx_import_task.delay")
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

    @patch("hope.apps.registration_data.celery_tasks.registration_kobo_import_task.delay")
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

    @patch("hope.apps.registration_data.celery_tasks.registration_program_population_import_task.delay")
    def test_create_rdi_social_worker_program_with_household_ids(self, mock_registration_task: Mock) -> None:
        self.client.force_authenticate(user=self.user)
        role, _ = Role.objects.update_or_create(
            name="TestPermissionCreateRole",
            defaults={"permissions": [Permissions.RDI_IMPORT_DATA.value]},
        )
        RoleAssignment.objects.get_or_create(user=self.user, role=role, business_area=self.business_area)

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
            business_area=self.business_area,
            beneficiary_group=beneficiary_group,
            data_collecting_type=social_dct,
        )

        social_dct.compatible_types.add(social_dct)

        # Create households with individuals in source program
        household1, individuals1 = create_household_and_individuals(
            household_data={
                "program": import_from_program,
                "business_area": self.business_area,
            },
            individuals_data=[
                {"program": import_from_program, "business_area": self.business_area},
            ],
        )

        household2, individuals2 = create_household_and_individuals(
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
            response = self.client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["name"] == "Test Social Worker Import - Households"
        # Should import both households
        assert response.data["number_of_households"] == 2
        assert response.data["number_of_individuals"] == 2
        mock_registration_task.assert_called_once()

    @patch("hope.apps.registration_data.celery_tasks.registration_program_population_import_task.delay")
    def test_create_rdi_social_worker_program_with_individual_ids(self, mock_registration_task: Mock) -> None:
        self.client.force_authenticate(user=self.user)
        role, _ = Role.objects.update_or_create(
            name="TestPermissionCreateRole",
            defaults={"permissions": [Permissions.RDI_IMPORT_DATA.value]},
        )
        RoleAssignment.objects.get_or_create(user=self.user, role=role, business_area=self.business_area)

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
            business_area=self.business_area,
            beneficiary_group=beneficiary_group,
            data_collecting_type=social_dct,
        )

        social_dct.compatible_types.add(social_dct)

        # Create households with individuals in source program
        household1, individuals1 = create_household_and_individuals(
            household_data={
                "program": import_from_program,
                "business_area": self.business_area,
            },
            individuals_data=[
                {"program": import_from_program, "business_area": self.business_area},
                {"program": import_from_program, "business_area": self.business_area},
            ],
        )

        household2, individuals2 = create_household_and_individuals(
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
            response = self.client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["name"] == "Test Social Worker Import - Individuals"
        assert response.data["number_of_households"] == 2
        assert response.data["number_of_individuals"] == 2
        mock_registration_task.assert_called_once()


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

    @patch(
        "hope.apps.registration_data.services"
        ".biometric_deduplication"
        ".BiometricDeduplicationService"
        ".report_individuals_status"
    )
    @patch("hope.apps.registration_data.api.views.remove_elasticsearch_documents_by_matching_ids")
    def test_permission_checks_refuse(
        self, remove_elasticsearch_documents_by_matching_ids_moc: Any, report_refused_individuals_mock: Any
    ) -> None:
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

    @patch("hope.apps.registration_data.celery_tasks.rdi_deduplication_task.delay")
    def test_permission_checks_deduplicate(self, mock_dedup_task: Mock) -> None:
        """Test that deduplicate endpoint requires RDI_RERUN_DEDUPE permission."""
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

    @patch("hope.apps.registration_data.celery_tasks.registration_program_population_import_task.delay")
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

    @patch("hope.apps.registration_data.celery_tasks.registration_program_population_import_task.delay")
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

    @patch("hope.apps.registration_data.celery_tasks.registration_program_population_import_task.delay")
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

    @patch("hope.apps.registration_data.celery_tasks.registration_program_population_import_task.delay")
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

    @patch("hope.apps.registration_data.celery_tasks.registration_program_population_import_task.delay")
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

    @patch("hope.apps.registration_data.celery_tasks.registration_program_population_import_task.delay")
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

    @patch("hope.apps.registration_data.celery_tasks.registration_program_population_import_task.delay")
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

    @patch("hope.apps.registration_data.celery_tasks.registration_program_population_import_task.delay")
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

    def test_rdi_name_not_unique(self) -> None:
        self.client.force_authenticate(user=self.user)

        role, _ = Role.objects.update_or_create(
            name="TestPermissionCreateRole",
            defaults={"permissions": [Permissions.RDI_IMPORT_DATA.value]},
        )
        RoleAssignment.objects.get_or_create(user=self.user, role=role, business_area=self.business_area)

        RegistrationDataImportFactory(
            business_area=self.business_area,
            program=self.program,
            name="Test Unique Name",
            status=RegistrationDataImport.IN_REVIEW,
        )

        import_data = ImportDataFactory(
            status=ImportData.STATUS_FINISHED,
            business_area_slug=self.business_area.slug,
            data_type=ImportData.XLSX,
            number_of_households=2,
            number_of_individuals=5,
        )

        url = reverse(
            "api:registration-data:registration-data-imports-registration-xlsx-import",
            args=["afghanistan", self.program.slug],
        )

        data = {
            "import_data_id": str(import_data.id),
            "name": "Test Unique Name",  # Same as existing RDI
            "screen_beneficiary": False,
        }

        response = self.client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "name" in response.data
        assert "This field must be unique." in response.data["name"]
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
