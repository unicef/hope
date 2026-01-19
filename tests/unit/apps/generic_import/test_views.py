from datetime import timedelta
from io import BytesIO
from unittest.mock import patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import DatabaseError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
import pytest

from extras.test_utils.factories.account import UserFactory
from extras.test_utils.factories.core import create_afghanistan
from extras.test_utils.factories.program import ProgramFactory
from hope.apps.account.permissions import Permissions
from hope.models import BusinessArea, ImportData, Partner, Program, RegistrationDataImport, Role, RoleAssignment

pytestmark = pytest.mark.django_db


# ============ Fixtures ============


@pytest.fixture
def afghanistan():
    create_afghanistan()
    return BusinessArea.objects.get(slug="afghanistan")


@pytest.fixture
def program(afghanistan):
    return ProgramFactory(business_area=afghanistan, status=Program.ACTIVE)


@pytest.fixture
def user():
    return UserFactory()


@pytest.fixture
def upload_url():
    return reverse("generic_import:generic-import")


@pytest.fixture
def upload_file():
    """Factory fixture for creating test upload files."""

    def _create(filename="test.xlsx"):
        return SimpleUploadedFile(
            filename,
            BytesIO(b"fake excel content").getvalue(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

    return _create


@pytest.fixture
def authenticated_client(client, user):
    """Client with user logged in."""
    client.force_login(user, "django.contrib.auth.backends.ModelBackend")
    return client


@pytest.fixture
def create_role_with_permissions():
    """Factory fixture for creating roles with permissions."""

    def _create(user, permissions, business_area, program=None):
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

    return _create


@pytest.fixture
def user_with_import_permission(user, afghanistan, program, create_role_with_permissions):
    """User with GENERIC_IMPORT_DATA permission."""
    create_role_with_permissions(user, [Permissions.GENERIC_IMPORT_DATA], afghanistan, program=program)
    return user


@pytest.fixture
def client_with_import_permission(client, user_with_import_permission):
    """Authenticated client with import permission."""
    client.force_login(user_with_import_permission, "django.contrib.auth.backends.ModelBackend")
    return client


# ============ Tests ============


class TestGenericImportUploadView:
    """Tests for GenericImportUploadView."""

    def test_view_requires_authentication(self, client, upload_url):
        """Unauthenticated users are redirected."""
        response = client.get(upload_url)
        assert response.status_code == 302

    def test_user_with_no_business_areas_gets_403(self, authenticated_client, upload_url):
        """Users with no business area access get 403."""
        response = authenticated_client.get(upload_url)
        assert response.status_code == 403

    def test_view_requires_permission(
        self, authenticated_client, upload_url, user, afghanistan, create_role_with_permissions
    ):
        """Users without GENERIC_IMPORT_DATA permission get 403."""
        create_role_with_permissions(user, [Permissions.RDI_VIEW_LIST], afghanistan)
        response = authenticated_client.get(upload_url)
        assert response.status_code == 403

    def test_view_with_correct_permission(self, client_with_import_permission, upload_url):
        """Users with GENERIC_IMPORT_DATA permission can access view."""
        response = client_with_import_permission.get(upload_url)
        assert response.status_code == 200
        assert "generic_import/upload.html" in [t.name for t in response.templates]

    @patch("hope.apps.generic_import.views.process_generic_import_task.delay")
    def test_successful_upload_creates_objects_and_triggers_task(
        self,
        mock_delay,
        client_with_import_permission,
        upload_url,
        upload_file,
        afghanistan,
        program,
        user_with_import_permission,
    ):
        """Successful file upload creates ImportData, RDI, and triggers Celery task."""
        with TestCase.captureOnCommitCallbacks(execute=True):
            response = client_with_import_permission.post(
                upload_url,
                data={
                    "business_area": afghanistan.id,
                    "program": program.id,
                    "file": upload_file(),
                },
            )

        assert response.status_code == 302
        assert response.url == upload_url

        # ImportData created
        assert ImportData.objects.count() == 1
        import_data = ImportData.objects.first()
        assert import_data.status == ImportData.STATUS_PENDING
        assert import_data.business_area_slug == afghanistan.slug
        assert import_data.data_type == ImportData.XLSX
        assert import_data.created_by_id == user_with_import_permission.id

        # RDI created
        assert RegistrationDataImport.objects.count() == 1
        rdi = RegistrationDataImport.objects.first()
        assert rdi.status == RegistrationDataImport.IMPORT_SCHEDULED
        assert rdi.business_area == afghanistan
        assert rdi.program == program
        assert rdi.imported_by == user_with_import_permission
        assert rdi.data_source == RegistrationDataImport.XLS
        assert rdi.import_data == import_data

        # Task called
        mock_delay.assert_called_once()
        call_kwargs = mock_delay.call_args[1]
        assert call_kwargs["registration_data_import_id"] == str(rdi.id)
        assert call_kwargs["import_data_id"] == str(import_data.id)

    @patch("hope.apps.generic_import.views.process_generic_import_task.delay")
    def test_upload_without_permission_for_selected_ba_fails(
        self, mock_delay, client_with_import_permission, upload_url, upload_file
    ):
        """Upload fails if user doesn't have permission for selected BA."""
        other_ba = BusinessArea.objects.create(name="Other Country", slug="other-country", code="OTH")
        other_program = ProgramFactory(business_area=other_ba, status=Program.ACTIVE)

        response = client_with_import_permission.post(
            upload_url,
            data={
                "business_area": other_ba.id,
                "program": other_program.id,
                "file": upload_file(),
            },
        )

        assert response.status_code == 200  # form_invalid returns 200
        assert ImportData.objects.count() == 0
        assert RegistrationDataImport.objects.count() == 0
        mock_delay.assert_not_called()

    @patch("hope.apps.generic_import.views.process_generic_import_task.delay")
    def test_upload_with_invalid_file_shows_errors(
        self, mock_delay, client_with_import_permission, upload_url, afghanistan, program
    ):
        """Invalid file upload shows form errors."""
        invalid_file = SimpleUploadedFile("test.pdf", b"fake content", content_type="application/pdf")

        response = client_with_import_permission.post(
            upload_url,
            data={
                "business_area": afghanistan.id,
                "program": program.id,
                "file": invalid_file,
            },
        )

        assert response.status_code == 200
        assert "form" in response.context
        assert not response.context["form"].is_valid()
        assert ImportData.objects.count() == 0
        mock_delay.assert_not_called()

    @patch("hope.apps.generic_import.views.process_generic_import_task.delay")
    def test_upload_without_file_shows_errors(
        self, mock_delay, client_with_import_permission, upload_url, afghanistan, program
    ):
        """Upload without file shows form errors."""
        response = client_with_import_permission.post(
            upload_url,
            data={
                "business_area": afghanistan.id,
                "program": program.id,
            },
        )

        assert response.status_code == 200
        assert "form" in response.context
        assert not response.context["form"].is_valid()
        assert "file" in response.context["form"].errors
        mock_delay.assert_not_called()

    @patch("hope.apps.generic_import.views.process_generic_import_task.delay")
    def test_rdi_name_format(
        self, mock_delay, client_with_import_permission, upload_url, upload_file, afghanistan, program
    ):
        """RDI name follows expected format."""
        response = client_with_import_permission.post(
            upload_url,
            data={
                "business_area": afghanistan.id,
                "program": program.id,
                "file": upload_file(),
            },
        )

        assert response.status_code == 302
        rdi = RegistrationDataImport.objects.first()
        assert "Generic Import" in rdi.name
        assert afghanistan.slug in rdi.name
        assert program.name in rdi.name

    def test_context_data_includes_business_areas(self, client_with_import_permission, upload_url, afghanistan):
        """Template context includes user's business areas."""
        response = client_with_import_permission.get(upload_url)

        assert response.status_code == 200
        assert "business_areas" in response.context
        assert afghanistan in list(response.context["business_areas"])

    def test_expired_role_assignment_blocks_access(self, authenticated_client, upload_url, user, afghanistan):
        """Expired role assignments don't grant access."""
        role = Role.objects.create(
            name="Expired Role",
            permissions=[Permissions.GENERIC_IMPORT_DATA.value],
        )
        RoleAssignment.objects.create(
            user=user,
            role=role,
            business_area=afghanistan,
            expiry_date=timezone.now() - timedelta(days=1),
        )

        response = authenticated_client.get(upload_url)
        assert response.status_code == 403

    def test_inactive_business_area_blocks_access(
        self, authenticated_client, upload_url, user, afghanistan, create_role_with_permissions
    ):
        """Inactive business areas are filtered out."""
        create_role_with_permissions(user, [Permissions.GENERIC_IMPORT_DATA], afghanistan)
        afghanistan.active = False
        afghanistan.save()

        response = authenticated_client.get(upload_url)
        assert response.status_code == 403

    @patch("hope.apps.generic_import.views.process_generic_import_task.delay")
    def test_user_with_partner_permissions(
        self, mock_delay, client, upload_url, upload_file, user, afghanistan, program
    ):
        """Users inherit permissions from their partner."""
        partner = Partner.objects.create(name="Test Partner")
        partner.allowed_business_areas.add(afghanistan)

        user.partner = partner
        user.save()

        role = Role.objects.create(
            name="Partner Role",
            permissions=[Permissions.GENERIC_IMPORT_DATA.value],
        )
        RoleAssignment.objects.create(
            partner=partner,
            role=role,
            business_area=afghanistan,
            program=program,
        )

        client.force_login(user, "django.contrib.auth.backends.ModelBackend")

        response = client.get(upload_url)
        assert response.status_code == 200

        with TestCase.captureOnCommitCallbacks(execute=True):
            response = client.post(
                upload_url,
                data={
                    "business_area": afghanistan.id,
                    "program": program.id,
                    "file": upload_file(),
                },
            )
        assert response.status_code == 302
        mock_delay.assert_called_once()

    @patch("hope.apps.generic_import.views.process_generic_import_task.delay")
    def test_ba_level_permission_grants_all_programs(
        self, mock_delay, client, upload_url, upload_file, user, afghanistan
    ):
        """BA-level role assignment grants access to all programs."""
        program1 = ProgramFactory(business_area=afghanistan, status=Program.ACTIVE)
        program2 = ProgramFactory(business_area=afghanistan, status=Program.ACTIVE)

        role = Role.objects.create(
            name="BA Role",
            permissions=[Permissions.GENERIC_IMPORT_DATA.value],
        )
        RoleAssignment.objects.create(
            user=user,
            role=role,
            business_area=afghanistan,
            program=None,  # BA-wide access
        )

        client.force_login(user, "django.contrib.auth.backends.ModelBackend")

        for prog in [program1, program2]:
            with TestCase.captureOnCommitCallbacks(execute=True):
                response = client.post(
                    upload_url,
                    data={
                        "business_area": afghanistan.id,
                        "program": prog.id,
                        "file": upload_file(),
                    },
                )
            assert response.status_code == 302

        assert mock_delay.call_count == 2

    @patch("hope.apps.generic_import.views.process_generic_import_task.delay")
    @patch("hope.apps.generic_import.views.ImportData.objects.create")
    def test_database_error_prevents_task_trigger(
        self, mock_create, mock_delay, client_with_import_permission, upload_url, upload_file, afghanistan, program
    ):
        """Database errors prevent task from being triggered."""
        mock_create.side_effect = DatabaseError("Database error")

        response = client_with_import_permission.post(
            upload_url,
            data={
                "business_area": afghanistan.id,
                "program": program.id,
                "file": upload_file(),
            },
        )

        assert response.status_code == 200
        mock_delay.assert_not_called()

    @patch("hope.apps.generic_import.views.process_generic_import_task.delay")
    def test_upload_to_ba_without_import_permission_for_that_ba(
        self, mock_delay, authenticated_client, upload_url, upload_file, user, afghanistan, program
    ):
        """Upload fails when user has BA access but not GENERIC_IMPORT_DATA for selected BA."""
        other_ba = BusinessArea.objects.create(
            name="Other Country",
            slug="other-country",
            code="OTH",
            active=True,
        )
        other_program = ProgramFactory(business_area=other_ba, status=Program.ACTIVE)

        role_import = Role.objects.create(
            name="TestImportRole",
            permissions=[Permissions.GENERIC_IMPORT_DATA.value],
        )
        role_basic = Role.objects.create(
            name="TestBasicRole",
            permissions=[Permissions.RDI_VIEW_LIST.value],
        )

        RoleAssignment.objects.create(user=user, role=role_import, business_area=other_ba, program=other_program)
        RoleAssignment.objects.create(user=user, role=role_basic, business_area=afghanistan, program=program)

        response = authenticated_client.post(
            upload_url,
            data={
                "business_area": afghanistan.id,
                "program": program.id,
                "file": upload_file(),
            },
        )

        assert response.status_code == 200
        mock_delay.assert_not_called()
        messages_list = list(response.context["messages"])
        assert any("permission" in str(m).lower() for m in messages_list)

    @patch("hope.apps.generic_import.views.process_generic_import_task.delay")
    def test_form_invalid_shows_non_field_errors(
        self,
        mock_delay,
        client_with_import_permission,
        upload_url,
        upload_file,
        afghanistan,
        user_with_import_permission,
        create_role_with_permissions,
    ):
        """Non-field errors (__all__) are displayed correctly."""
        other_ba = BusinessArea.objects.create(
            name="Other Country",
            slug="other-country",
            code="OTH",
            active=True,
        )
        other_program = ProgramFactory(business_area=other_ba, status=Program.ACTIVE)

        create_role_with_permissions(
            user_with_import_permission, [Permissions.GENERIC_IMPORT_DATA], other_ba, program=other_program
        )

        # Submit with program from different BA
        response = client_with_import_permission.post(
            upload_url,
            data={
                "business_area": afghanistan.id,
                "program": other_program.id,
                "file": upload_file(),
            },
        )

        assert response.status_code == 200
        mock_delay.assert_not_called()
