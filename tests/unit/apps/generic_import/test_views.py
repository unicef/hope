from io import BytesIO
from unittest.mock import patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TransactionTestCase
from django.urls import reverse
from django.utils import timezone

from extras.test_utils.factories.account import UserFactory
from extras.test_utils.factories.core import create_afghanistan
from extras.test_utils.factories.program import ProgramFactory
from hope.apps.account.permissions import Permissions
from hope.apps.core.models import BusinessArea
from hope.apps.program.models import Program
from hope.apps.registration_data.models import ImportData, RegistrationDataImport


class TestGenericImportUploadView(TransactionTestCase):
    def setUp(self):
        """Set up test fixtures."""
        create_afghanistan()
        self.afghanistan = BusinessArea.objects.get(slug="afghanistan")
        self.program = ProgramFactory(
            business_area=self.afghanistan,
            status=Program.ACTIVE,
        )
        self.user = UserFactory()
        self.url = reverse("generic_import:generic-import")

    def _create_upload_file(self, filename="test.xlsx"):
        """Helper to create test Excel file."""
        file_content = BytesIO(b"fake excel content")
        return SimpleUploadedFile(
            filename,
            file_content.getvalue(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

    def _create_user_role_with_permissions(self, user, permissions, business_area, program=None):
        """Helper to create user role with permissions."""
        from hope.apps.account.models import Role, RoleAssignment

        permission_list = [perm.value for perm in permissions]
        role, _ = Role.objects.update_or_create(
            name=f"Test Role {permission_list[0]}", defaults={"permissions": permission_list}
        )

        if not program:
            program = ProgramFactory(business_area=business_area, name="Test Program")

        RoleAssignment.objects.get_or_create(
            user=user,
            role=role,
            business_area=business_area,
            program=program,
        )

    def test_view_requires_authentication(self):
        """Test that unauthenticated users are redirected."""
        response = self.client.get(self.url)
        assert response.status_code == 302  # Redirect to login

    def test_user_with_no_business_areas_gets_403(self):
        """Test that users with no business area access get 403."""
        self.client.force_login(self.user, "django.contrib.auth.backends.ModelBackend")
        response = self.client.get(self.url)
        assert response.status_code == 403

    def test_view_requires_permission(self):
        """Test that users without GENERIC_IMPORT_DATA permission get 403."""
        # Create role assignment but with wrong permission
        self._create_user_role_with_permissions(
            self.user,
            [Permissions.RDI_VIEW_LIST],  # Wrong permission
            self.afghanistan,
        )
        self.client.force_login(self.user, "django.contrib.auth.backends.ModelBackend")
        response = self.client.get(self.url)
        assert response.status_code == 403

    def test_view_with_correct_permission(self):
        """Test that users with GENERIC_IMPORT_DATA permission can access view."""
        self._create_user_role_with_permissions(
            self.user,
            [Permissions.GENERIC_IMPORT_DATA],
            self.afghanistan,
        )
        self.client.force_login(self.user, "django.contrib.auth.backends.ModelBackend")

        response = self.client.get(self.url)
        assert response.status_code == 200
        assert "generic_import/upload.html" in [t.name for t in response.templates]

    @patch("hope.apps.generic_import.views.process_generic_import_task.delay")
    def test_successful_upload_creates_objects_and_triggers_task(self, mock_delay):
        """Test successful file upload creates ImportData, RDI, and triggers Celery task."""
        self._create_user_role_with_permissions(
            self.user,
            [Permissions.GENERIC_IMPORT_DATA],
            self.afghanistan,
            program=self.program,
        )
        self.client.force_login(self.user, "django.contrib.auth.backends.ModelBackend")

        uploaded_file = self._create_upload_file()

        response = self.client.post(
            self.url,
            data={
                "business_area": self.afghanistan.id,
                "program": self.program.id,
                "file": uploaded_file,
            },
        )

        # Should redirect to success_url
        assert response.status_code == 302
        assert response.url == self.url

        # ImportData should be created
        assert ImportData.objects.count() == 1
        import_data = ImportData.objects.first()
        assert import_data.status == ImportData.STATUS_PENDING
        assert import_data.business_area_slug == self.afghanistan.slug
        assert import_data.data_type == ImportData.XLSX
        assert import_data.created_by_id == self.user.id

        # RegistrationDataImport should be created
        assert RegistrationDataImport.objects.count() == 1
        rdi = RegistrationDataImport.objects.first()
        assert rdi.status == RegistrationDataImport.IMPORT_SCHEDULED
        assert rdi.business_area == self.afghanistan
        assert rdi.program == self.program
        assert rdi.imported_by == self.user
        assert rdi.data_source == RegistrationDataImport.XLS
        assert rdi.import_data == import_data
        assert rdi.number_of_households == 0
        assert rdi.number_of_individuals == 0

        # Celery task should be called
        mock_delay.assert_called_once()
        call_kwargs = mock_delay.call_args[1]
        assert call_kwargs["registration_data_import_id"] == str(rdi.id)
        assert call_kwargs["import_data_id"] == str(import_data.id)

    @patch("hope.apps.generic_import.views.process_generic_import_task.delay")
    def test_upload_without_permission_for_selected_ba_fails(self, mock_delay):
        """Test that upload fails if user doesn't have permission for selected BA."""
        # Create another business area
        other_ba = BusinessArea.objects.create(
            name="Other Country",
            slug="other-country",
            code="OTH",
        )
        other_program = ProgramFactory(business_area=other_ba, status=Program.ACTIVE)

        # User only has permission for afghanistan
        self._create_user_role_with_permissions(
            self.user,
            [Permissions.GENERIC_IMPORT_DATA],
            self.afghanistan,
        )
        self.client.force_login(self.user, "django.contrib.auth.backends.ModelBackend")

        uploaded_file = self._create_upload_file()

        # Try to upload for other_ba (no permission)
        response = self.client.post(
            self.url,
            data={
                "business_area": other_ba.id,
                "program": other_program.id,
                "file": uploaded_file,
            },
        )

        # Should show error message and not create objects
        assert response.status_code == 200  # form_invalid returns 200
        assert ImportData.objects.count() == 0
        assert RegistrationDataImport.objects.count() == 0
        mock_delay.assert_not_called()

    @patch("hope.apps.generic_import.views.process_generic_import_task.delay")
    def test_upload_with_invalid_file_shows_errors(self, mock_delay):
        """Test that invalid file upload shows form errors."""
        self._create_user_role_with_permissions(
            self.user,
            [Permissions.GENERIC_IMPORT_DATA],
            self.afghanistan,
            program=self.program,
        )
        self.client.force_login(self.user, "django.contrib.auth.backends.ModelBackend")

        # Invalid file (wrong extension)
        invalid_file = SimpleUploadedFile(
            "test.pdf",
            b"fake content",
            content_type="application/pdf",
        )

        response = self.client.post(
            self.url,
            data={
                "business_area": self.afghanistan.id,
                "program": self.program.id,
                "file": invalid_file,
            },
        )

        # Should show form with errors
        assert response.status_code == 200
        assert "form" in response.context
        assert not response.context["form"].is_valid()

        # No objects created, no task called
        assert ImportData.objects.count() == 0
        assert RegistrationDataImport.objects.count() == 0
        mock_delay.assert_not_called()

    @patch("hope.apps.generic_import.views.process_generic_import_task.delay")
    def test_upload_without_file_shows_errors(self, mock_delay):
        """Test that upload without file shows form errors."""
        self._create_user_role_with_permissions(
            self.user,
            [Permissions.GENERIC_IMPORT_DATA],
            self.afghanistan,
            program=self.program,
        )
        self.client.force_login(self.user, "django.contrib.auth.backends.ModelBackend")

        response = self.client.post(
            self.url,
            data={
                "business_area": self.afghanistan.id,
                "program": self.program.id,
                # No file
            },
        )

        # Should show form with errors
        assert response.status_code == 200
        assert "form" in response.context
        assert not response.context["form"].is_valid()
        assert "file" in response.context["form"].errors

        # No objects created, no task called
        assert ImportData.objects.count() == 0
        assert RegistrationDataImport.objects.count() == 0
        mock_delay.assert_not_called()

    @patch("hope.apps.generic_import.views.process_generic_import_task.delay")
    def test_rdi_name_format(self, mock_delay):
        """Test that RDI name follows expected format."""
        self._create_user_role_with_permissions(
            self.user,
            [Permissions.GENERIC_IMPORT_DATA],
            self.afghanistan,
            program=self.program,
        )
        self.client.force_login(self.user, "django.contrib.auth.backends.ModelBackend")

        uploaded_file = self._create_upload_file()

        response = self.client.post(
            self.url,
            data={
                "business_area": self.afghanistan.id,
                "program": self.program.id,
                "file": uploaded_file,
            },
        )

        assert response.status_code == 302

        rdi = RegistrationDataImport.objects.first()
        # Check name format: "Generic Import {ba_slug} - {program_name} - {timestamp}"
        assert "Generic Import" in rdi.name
        assert self.afghanistan.slug in rdi.name
        assert self.program.name in rdi.name

    @patch("hope.apps.generic_import.views.process_generic_import_task.delay")
    def test_context_data_includes_business_areas(self, mock_delay):
        """Test that template context includes user's business areas."""
        self._create_user_role_with_permissions(
            self.user,
            [Permissions.GENERIC_IMPORT_DATA],
            self.afghanistan,
        )
        self.client.force_login(self.user, "django.contrib.auth.backends.ModelBackend")

        response = self.client.get(self.url)

        assert response.status_code == 200
        assert "business_areas" in response.context
        assert self.afghanistan in list(response.context["business_areas"])

    def test_expired_role_assignment_blocks_access(self):
        """Test that expired role assignments don't grant access."""
        from datetime import timedelta

        from hope.apps.account.models import Role, RoleAssignment

        role = Role.objects.create(
            name="Expired Role",
            permissions=[Permissions.GENERIC_IMPORT_DATA.value],
        )

        # Create expired role assignment
        RoleAssignment.objects.create(
            user=self.user,
            role=role,
            business_area=self.afghanistan,
            expiry_date=timezone.now() - timedelta(days=1),  # Expired yesterday
        )

        self.client.force_login(self.user, "django.contrib.auth.backends.ModelBackend")
        response = self.client.get(self.url)
        # Should get 403 because role assignment is expired
        assert response.status_code == 403

    def test_inactive_business_area_blocks_access(self):
        """Test that inactive business areas are filtered out."""
        self._create_user_role_with_permissions(
            self.user,
            [Permissions.GENERIC_IMPORT_DATA],
            self.afghanistan,
        )

        # Make BA inactive
        self.afghanistan.active = False
        self.afghanistan.save()

        self.client.force_login(self.user, "django.contrib.auth.backends.ModelBackend")
        response = self.client.get(self.url)
        # Should get 403 because no active BAs available
        assert response.status_code == 403

        # Restore BA state for other tests
        self.afghanistan.active = True
        self.afghanistan.save()

    @patch("hope.apps.generic_import.views.process_generic_import_task.delay")
    def test_user_with_partner_permissions(self, mock_delay):
        """Test that users inherit permissions from their partner."""
        from hope.apps.account.models import Partner, Role, RoleAssignment

        # Create partner with allowed business areas
        partner = Partner.objects.create(name="Test Partner")
        partner.allowed_business_areas.add(self.afghanistan)

        # Associate user with partner
        self.user.partner = partner
        self.user.save()

        # Create role assignment on partner, not user
        role = Role.objects.create(
            name="Partner Role",
            permissions=[Permissions.GENERIC_IMPORT_DATA.value],
        )
        RoleAssignment.objects.create(
            partner=partner,  # NOT user=self.user
            role=role,
            business_area=self.afghanistan,
            program=self.program,
        )

        self.client.force_login(self.user, "django.contrib.auth.backends.ModelBackend")
        response = self.client.get(self.url)
        # User should have access through partner
        assert response.status_code == 200

        # Also test that user can upload
        uploaded_file = self._create_upload_file()
        response = self.client.post(
            self.url,
            data={
                "business_area": self.afghanistan.id,
                "program": self.program.id,
                "file": uploaded_file,
            },
        )
        assert response.status_code == 302
        mock_delay.assert_called_once()

    @patch("hope.apps.generic_import.views.process_generic_import_task.delay")
    def test_ba_level_permission_grants_all_programs(self, mock_delay):
        """Test that BA-level role assignment grants access to all programs."""
        from hope.apps.account.models import Role, RoleAssignment

        program1 = ProgramFactory(business_area=self.afghanistan, status=Program.ACTIVE)
        program2 = ProgramFactory(business_area=self.afghanistan, status=Program.ACTIVE)

        # Create BA-level role assignment (program=None)
        role = Role.objects.create(
            name="BA Role",
            permissions=[Permissions.GENERIC_IMPORT_DATA.value],
        )
        RoleAssignment.objects.create(
            user=self.user,
            role=role,
            business_area=self.afghanistan,
            program=None,  # BA-wide access
        )

        self.client.force_login(self.user, "django.contrib.auth.backends.ModelBackend")

        # Should be able to upload for either program
        for program in [program1, program2]:
            uploaded_file = self._create_upload_file()
            response = self.client.post(
                self.url,
                data={
                    "business_area": self.afghanistan.id,
                    "program": program.id,
                    "file": uploaded_file,
                },
            )
            assert response.status_code == 302

        # Should have been called twice (once per program)
        assert mock_delay.call_count == 2

    @patch("hope.apps.generic_import.views.process_generic_import_task.delay")
    @patch("hope.apps.generic_import.views.ImportData.objects.create")
    def test_database_error_prevents_task_trigger(self, mock_create, mock_delay):
        """Test that database errors prevent task from being triggered."""
        self._create_user_role_with_permissions(
            self.user,
            [Permissions.GENERIC_IMPORT_DATA],
            self.afghanistan,
            program=self.program,
        )
        self.client.force_login(self.user, "django.contrib.auth.backends.ModelBackend")

        # Simulate database error
        mock_create.side_effect = Exception("Database error")

        uploaded_file = self._create_upload_file()

        response = self.client.post(
            self.url,
            data={
                "business_area": self.afghanistan.id,
                "program": self.program.id,
                "file": uploaded_file,
            },
        )

        # Should show error page
        assert response.status_code == 200

        # Task should NOT be called due to exception
        mock_delay.assert_not_called()
