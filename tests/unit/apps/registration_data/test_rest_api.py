from contextlib import contextmanager
from typing import Callable, Generator
from unittest.mock import Mock, patch

from django.db import DEFAULT_DB_ALIAS, connections
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from hct_mis_api.apps.account.fixtures import PartnerFactory, UserFactory
from hct_mis_api.apps.account.models import Role, RoleAssignment
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.household.fixtures import \
    create_household_and_individuals
from hct_mis_api.apps.household.models import Household, Individual
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.registration_data.fixtures import \
    RegistrationDataImportFactory
from hct_mis_api.apps.registration_data.models import RegistrationDataImport
from tests.unit.api.base import HOPEApiTestCase


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
        cls.user = UserFactory(username="Hope_Test_DRF", password="HopePass", partner=unicef, is_superuser=True)
        permission_list = [perm.value for perm in user_permissions]
        role, created = Role.objects.update_or_create(name="TestName", defaults={"permissions": permission_list})
        user_role, _ = RoleAssignment.objects.get_or_create(user=cls.user, role=role, business_area=cls.business_area)
        cls.program = ProgramFactory(
            name="Test Program",
            status=Program.ACTIVE,
            biometric_deduplication_enabled=True,
        )
        cls.client = APIClient()

    @patch("hct_mis_api.apps.registration_datahub.celery_tasks.deduplication_engine_process.delay")
    def test_run_deduplication(self, mock_deduplication_engine_process: Mock) -> None:
        self.client.force_authenticate(user=self.user)
        url = reverse(
            "api:registration-data:registration-data-imports-run-deduplication",
            args=["afghanistan", self.program.slug],
        )
        resp = self.client.post(url, {}, format="json")

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data, {"message": "Deduplication process started"})
        mock_deduplication_engine_process.assert_called_once_with(str(self.program.id))

    @patch("hct_mis_api.apps.registration_datahub.celery_tasks.fetch_biometric_deduplication_results_and_process.delay")
    def test_webhook_deduplication(self, mock_fetch_dedup_results: Mock) -> None:
        url = reverse(
            "api:registration-data:registration-data-imports-webhook-deduplication",
            args=["afghanistan", self.program.slug],
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
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
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = response.data["results"]
        self.assertEqual(len(results), 2)
        self.assertEqual(set([r["name"] for r in results]), {rdi1.name, rdi2.name})

        for result in results:
            if result["name"] == "Test RDI 1":
                self.assertEqual(result["status"], "In Review")
                self.assertEqual(result["data_source"], "Excel")
                self.assertEqual(result["imported_by"], self.user.get_full_name())
            elif result["name"] == "Test RDI 2":
                self.assertEqual(result["status"], "Deduplication")
                self.assertEqual(result["data_source"], "KoBo")
                self.assertEqual(result["imported_by"], self.user.get_full_name())

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
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], rdi.name)
        self.assertEqual(response.data["id"], str(rdi.id))

        self.assertEqual(response.data["status_display"], "In Review")
        self.assertEqual(response.data["data_source"], "Excel")
        self.assertEqual(response.data["imported_by"], self.user.get_full_name())

        batch_duplicates = response.data["batch_duplicates_count_and_percentage"]
        self.assertEqual(len(batch_duplicates), 2)
        self.assertEqual(batch_duplicates[0]["count"], 5)
        self.assertAlmostEqual(batch_duplicates[0]["percentage"], 10.0)
        self.assertEqual(batch_duplicates[1]["count"], 4)
        self.assertAlmostEqual(batch_duplicates[1]["percentage"], 8.0)

        batch_unique = response.data["batch_unique_count_and_percentage"]
        self.assertEqual(len(batch_unique), 2)
        self.assertEqual(batch_unique[0]["count"], 45)
        self.assertAlmostEqual(batch_unique[0]["percentage"], 90.0)
        self.assertEqual(batch_unique[1]["count"], 46)
        self.assertAlmostEqual(batch_unique[1]["percentage"], 92.0)

        gr_duplicates = response.data["golden_record_duplicates_count_and_percentage"]
        self.assertEqual(gr_duplicates[0]["count"], 3)
        self.assertAlmostEqual(gr_duplicates[0]["percentage"], 6.0)

        gr_possible_duplicates = response.data["golden_record_possible_duplicates_count_and_percentage"]
        self.assertEqual(len(gr_possible_duplicates), 2)
        self.assertEqual(gr_possible_duplicates[0]["count"], 2)
        self.assertAlmostEqual(gr_possible_duplicates[0]["percentage"], 4.0)
        self.assertEqual(gr_possible_duplicates[1]["count"], 3)
        self.assertAlmostEqual(gr_possible_duplicates[1]["percentage"], 6.0)

        gr_unique = response.data["golden_record_unique_count_and_percentage"]
        self.assertEqual(len(gr_unique), 2)
        self.assertEqual(gr_unique[0]["count"], 45)
        self.assertAlmostEqual(gr_unique[0]["percentage"], 90.0)
        self.assertEqual(gr_unique[1]["count"], 47)
        self.assertAlmostEqual(gr_unique[1]["percentage"], 94.0)

        self.assertIn("admin_url", response.data)
        self.assertTrue(response.data["admin_url"])

    @patch("hct_mis_api.apps.registration_datahub.celery_tasks.merge_registration_data_import_task.delay")
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
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {"message": "Registration Data Import Merge Scheduled"})

        rdi.refresh_from_db()
        self.assertEqual(rdi.status, RegistrationDataImport.MERGE_SCHEDULED)
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
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        rdi.refresh_from_db()
        self.assertEqual(rdi.status, RegistrationDataImport.DEDUPLICATION)

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

        self.assertEqual(Household.all_objects.filter(registration_data_import=rdi).count(), 1)
        self.assertEqual(Individual.all_objects.filter(registration_data_import=rdi).count(), 2)

        url = reverse(
            "api:registration-data:registration-data-imports-erase",
            args=["afghanistan", self.program.slug, rdi.id],
        )

        response = self.client.post(url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {"message": "Registration Data Import Erased"})

        self.assertEqual(Household.all_objects.filter(registration_data_import=rdi).count(), 0)

        rdi.refresh_from_db()
        self.assertTrue(rdi.erased)

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
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertEqual(Household.all_objects.filter(registration_data_import=rdi).count(), 1)

        rdi.refresh_from_db()
        self.assertFalse(rdi.erased)

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

        self.assertEqual(Household.all_objects.filter(registration_data_import=rdi).count(), 1)
        self.assertEqual(Individual.all_objects.filter(registration_data_import=rdi).count(), 2)

        url = reverse(
            "api:registration-data:registration-data-imports-refuse",
            args=["afghanistan", self.program.slug, rdi.id],
        )

        response = self.client.post(url, {"reason": "Testing refuse endpoint"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {"message": "Registration Data Import Refused"})

        self.assertEqual(Household.all_objects.filter(registration_data_import=rdi).count(), 0)

        rdi.refresh_from_db()
        self.assertEqual(rdi.status, RegistrationDataImport.REFUSED_IMPORT)
        self.assertEqual(rdi.refuse_reason, "Testing refuse endpoint")

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
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertEqual(Household.all_objects.filter(registration_data_import=rdi).count(), 1)

        rdi.refresh_from_db()
        self.assertEqual(rdi.status, RegistrationDataImport.DEDUPLICATION)

    @patch("hct_mis_api.apps.registration_datahub.celery_tasks.rdi_deduplication_task.delay")
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
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        rdi.refresh_from_db()
        self.assertEqual(rdi.status, RegistrationDataImport.DEDUPLICATION)

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
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        rdi.refresh_from_db()
        self.assertEqual(rdi.status, RegistrationDataImport.IN_REVIEW)

    def test_status_choices(self) -> None:
        self.client.force_authenticate(user=self.user)
        url = reverse(
            "api:registration-data:registration-data-imports-status-choices",
            args=["afghanistan", self.program.slug],
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertTrue(all("name" in c and "value" in c for c in response.data))


class RegistrationDataImportPermissionTest(HOPEApiTestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        unicef_partner = PartnerFactory(name="UNICEF")
        unicef = PartnerFactory(name="UNICEF HQ", parent=unicef_partner)
        cls.user = UserFactory(username="Hope_Test_DRF", password="HopePass", partner=unicef, is_superuser=False)
        cls.program = ProgramFactory(
            name="Test Program",
            status=Program.ACTIVE,
        )
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
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        role, _ = Role.objects.update_or_create(
            name="TestPermissionListRole", defaults={"permissions": [Permissions.RDI_VIEW_LIST.value]}
        )
        RoleAssignment.objects.get_or_create(user=self.user, role=role, business_area=self.business_area)

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_permission_checks_retrieve(self) -> None:
        self.client.force_authenticate(user=self.user)

        url = reverse(
            "api:registration-data:registration-data-imports-detail",
            args=["afghanistan", self.program.slug, self.rdi.id],
        )

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        role, _ = Role.objects.update_or_create(
            name="TestPermissionRetrieveRole", defaults={"permissions": [Permissions.RDI_VIEW_DETAILS.value]}
        )
        RoleAssignment.objects.get_or_create(user=self.user, role=role, business_area=self.business_area)

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

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
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        role, _ = Role.objects.update_or_create(
            name="TestPermissionMergeRole", defaults={"permissions": [Permissions.RDI_MERGE_IMPORT.value]}
        )
        RoleAssignment.objects.get_or_create(user=self.user, role=role, business_area=self.business_area)

        response = self.client.post(url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

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
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        role, _ = Role.objects.update_or_create(
            name="TestPermissionEraseRole", defaults={"permissions": [Permissions.RDI_REFUSE_IMPORT.value]}
        )
        RoleAssignment.objects.get_or_create(user=self.user, role=role, business_area=self.business_area)

        response = self.client.post(url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

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
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        role, _ = Role.objects.update_or_create(
            name="TestPermissionRefuseRole", defaults={"permissions": [Permissions.RDI_REFUSE_IMPORT.value]}
        )
        RoleAssignment.objects.get_or_create(user=self.user, role=role, business_area=self.business_area)

        response = self.client.post(url, {"reason": "Test reason"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

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
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        role, _ = Role.objects.update_or_create(
            name="TestPermissionDeduplicateRole", defaults={"permissions": [Permissions.RDI_RERUN_DEDUPE.value]}
        )
        RoleAssignment.objects.get_or_create(user=self.user, role=role, business_area=self.business_area)

        response = self.client.post(url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_permission_checks_status_choices(self) -> None:
        self.client.force_authenticate(user=self.user)
        url = reverse(
            "api:registration-data:registration-data-imports-status-choices",
            args=["afghanistan", self.program.slug],
        )
        # Should be forbidden without permission
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Grant permission and try again
        role, _ = Role.objects.update_or_create(
            name="TestPermissionStatusChoicesRole", defaults={"permissions": [Permissions.RDI_VIEW_LIST.value]}
        )
        RoleAssignment.objects.get_or_create(user=self.user, role=role, business_area=self.business_area)

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertTrue(all("name" in c and "value" in c for c in response.data))

    @patch("hct_mis_api.apps.registration_datahub.celery_tasks.registration_program_population_import_task.delay")
    def test_create_registration_data_import(self, mock_registration_task: Mock) -> None:
        self.client.force_authenticate(user=self.user)
        # Grant permission for create
        role, _ = Role.objects.update_or_create(
            name="TestPermissionCreateRole", defaults={"permissions": [Permissions.RDI_IMPORT_DATA.value]}
        )
        RoleAssignment.objects.get_or_create(user=self.user, role=role, business_area=self.business_area)
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
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "Test Import")
        self.assertEqual(response.data["number_of_households"], 1)
        self.assertEqual(response.data["number_of_individuals"], 1)
        self.assertIn("id", response.data)
        mock_registration_task.assert_called_once()

    @patch("hct_mis_api.apps.registration_datahub.celery_tasks.registration_program_population_import_task.delay")
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
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
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
