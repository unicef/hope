from unittest.mock import patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from extras.test_utils.factories.account import BusinessAreaFactory, RoleFactory, UserFactory
from extras.test_utils.factories.program import ProgramFactory
from hope.api.models import Grant
from hope.apps.program.models import Program
from hope.apps.registration_data.models import ImportData, RegistrationDataImport
from unit.api.factories import APITokenFactory


class GenericImportAPITestCase(APITestCase):
    """Base test case for Generic Import API."""

    databases = {"default"}

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.user = UserFactory()
        cls.business_area = BusinessAreaFactory(name="Afghanistan", slug="afghanistan")
        cls.program = ProgramFactory(
            business_area=cls.business_area,
            status=Program.ACTIVE,
        )

        cls.token = APITokenFactory(
            user=cls.user,
            grants=[Grant.API_GENERIC_IMPORT.name],
        )
        cls.token.valid_for.set([cls.business_area])

        cls.role = RoleFactory(
            subsystem="API",
            name="GenericImportRole",
            permissions=[Grant.API_GENERIC_IMPORT.name],
        )
        cls.user.role_assignments.create(
            role=cls.role,
            business_area=cls.business_area,
        )

    def setUp(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")
        self.url = reverse(
            "api:generic-import:generic-import-upload-upload",
            args=[self.business_area.slug, self.program.slug],
        )

    def create_xlsx_file(self, filename="test.xlsx", content=b"test xlsx"):
        """Create test XLSX file."""
        return SimpleUploadedFile(
            filename,
            content,
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

    def create_xls_file(self, filename="test.xls", content=b"test xls"):
        """Create test XLS file."""
        return SimpleUploadedFile(
            filename,
            content,
            content_type="application/vnd.ms-excel",
        )

    @patch("hope.apps.generic_import.celery_tasks.process_generic_import_task.delay")
    def test_upload_valid_xlsx_file_success(self, mock_task):
        """Test successful upload of valid XLSX file."""
        file = self.create_xlsx_file()

        # Upload - capture on_commit callbacks
        with TestCase.captureOnCommitCallbacks(execute=True):
            response = self.client.post(self.url, {"file": file}, format="multipart")

        # Assert response
        assert response.status_code == status.HTTP_201_CREATED
        assert "import_data_id" in response.data
        assert "rdi_id" in response.data
        assert response.data["import_data_status"] == ImportData.STATUS_PENDING
        assert response.data["rdi_status"] == RegistrationDataImport.IMPORT_SCHEDULED

        # Assert ImportData created
        import_data = ImportData.objects.get(id=response.data["import_data_id"])
        assert import_data.status == ImportData.STATUS_PENDING
        assert import_data.business_area_slug == self.business_area.slug
        assert import_data.data_type == ImportData.XLSX
        assert import_data.created_by_id == self.user.id

        # Assert RDI created
        rdi = RegistrationDataImport.objects.get(id=response.data["rdi_id"])
        assert rdi.status == RegistrationDataImport.IMPORT_SCHEDULED
        assert rdi.business_area == self.business_area
        assert rdi.program == self.program
        assert rdi.imported_by == self.user
        assert rdi.data_source == RegistrationDataImport.XLS
        assert rdi.import_data == import_data

        # Assert Celery task scheduled
        mock_task.assert_called_once_with(
            registration_data_import_id=str(rdi.id),
            import_data_id=str(import_data.id),
        )

    def test_upload_invalid_file_type_pdf(self):
        """Test upload of PDF file - should fail validation."""
        file = SimpleUploadedFile(
            "document.pdf",
            b"fake pdf content",
            content_type="application/pdf",
        )

        response = self.client.post(self.url, {"file": file}, format="multipart")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "file" in response.data
        assert "Excel files" in str(response.data["file"])

    def test_upload_without_required_grant(self):
        """Test upload without API_GENERIC_IMPORT grant."""
        # Create token without grant
        token_no_grant = APITokenFactory(
            user=UserFactory(),
            grants=[Grant.API_READ_ONLY.name],
        )
        token_no_grant.valid_for.set([self.business_area])

        # Use token without grant
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token_no_grant.key}")

        file = self.create_xlsx_file()
        response = self.client.post(self.url, {"file": file}, format="multipart")

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_upload_file_too_large(self):
        """Test upload of file larger than 50MB."""
        # Create fake large file (51MB)
        large_content = b"x" * (51 * 1024 * 1024)
        file = self.create_xlsx_file(content=large_content)

        response = self.client.post(self.url, {"file": file}, format="multipart")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "file" in response.data
        assert "50 MB" in str(response.data["file"])

    def test_upload_without_authentication(self):
        """Test upload without Authorization header."""
        # Remove authorization
        self.client.credentials()

        file = self.create_xlsx_file()
        response = self.client.post(self.url, {"file": file}, format="multipart")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_upload_business_area_not_in_token_valid_for(self):
        """Test upload when token doesn't have access to business area."""
        # Create another business area
        other_ba = BusinessAreaFactory(name="Somalia", slug="somalia")

        # Token only has access to afghanistan, not somalia
        url = reverse(
            "api:generic-import:generic-import-upload-upload",
            args=[other_ba.slug, self.program.slug],
        )

        file = self.create_xlsx_file()
        response = self.client.post(url, {"file": file}, format="multipart")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_upload_invalid_program_slug(self):
        """Test upload with non-existent program slug."""
        url = reverse(
            "api:generic-import:generic-import-upload-upload",
            args=[self.business_area.slug, "nonexistent-program"],
        )

        file = self.create_xlsx_file()
        response = self.client.post(url, {"file": file}, format="multipart")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_upload_program_from_different_business_area(self):
        """Test upload when program belongs to different business area."""
        # Create another business area and program
        other_ba = BusinessAreaFactory(name="Somalia", slug="somalia")
        other_program = ProgramFactory(
            business_area=other_ba,
            status=Program.ACTIVE,
        )

        # Token has access to somalia
        self.token.valid_for.add(other_ba)

        # Try to use afghanistan BA with somalia's program
        url = reverse(
            "api:generic-import:generic-import-upload-upload",
            args=[self.business_area.slug, other_program.slug],
        )

        file = self.create_xlsx_file()
        response = self.client.post(url, {"file": file}, format="multipart")

        # Should fail because program doesn't belong to specified BA
        assert response.status_code == status.HTTP_404_NOT_FOUND
