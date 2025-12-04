from io import BytesIO

from django.core.files.uploadedfile import SimpleUploadedFile
import pytest

from extras.test_utils.factories.account import UserFactory
from extras.test_utils.factories.core import create_afghanistan
from extras.test_utils.factories.program import ProgramFactory
from hope.apps.core.models import BusinessArea
from hope.apps.generic_import.forms import GenericImportForm
from hope.apps.program.models import Program


@pytest.mark.django_db
class TestGenericImportForm:
    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test fixtures."""
        # Create business areas
        create_afghanistan()
        self.afghanistan = BusinessArea.objects.get(slug="afghanistan")
        self.other_ba = BusinessArea.objects.create(
            name="Other Country",
            slug="other-country",
            code="OTH",
            active=True,  # Must be active to be included in queryset
        )

        # Create programs - create them as needed in individual tests
        self.program_afg = ProgramFactory(
            business_area=self.afghanistan,
            status=Program.ACTIVE,
        )
        self.program_other = ProgramFactory(
            business_area=self.other_ba,
            status=Program.ACTIVE,
        )

        # Create users without partners to avoid shared partner issues
        # (PartnerFactory uses get_or_create which causes users to share partners)
        self.user_single_ba = UserFactory(partner=None)
        self.user_multi_ba = UserFactory(partner=None)

    def test_form_with_single_business_area_preselects_field(self, create_user_role_with_permissions):
        """Test that BA field is pre-selected when user has access to only one BA."""
        from hope.apps.account.permissions import Permissions

        # Create user with access to single BA
        create_user_role_with_permissions(
            self.user_single_ba,
            [Permissions.GENERIC_IMPORT_DATA],
            self.afghanistan,
        )

        form = GenericImportForm(user=self.user_single_ba)

        # BA field should be pre-selected (autoselect behavior)
        assert form.fields["business_area"].initial == self.afghanistan
        # Queryset should contain only one BA
        assert form.fields["business_area"].queryset.count() == 1

    def test_form_with_multiple_business_areas_shows_field(self, create_user_role_with_permissions):
        """Test that BA field is visible when user has access to multiple BAs."""
        from hope.apps.account.permissions import Permissions

        # Create user with access to multiple BAs
        create_user_role_with_permissions(
            self.user_multi_ba,
            [Permissions.GENERIC_IMPORT_DATA],
            self.afghanistan,
        )
        create_user_role_with_permissions(
            self.user_multi_ba,
            [Permissions.GENERIC_IMPORT_DATA],
            self.other_ba,
        )

        form = GenericImportForm(user=self.user_multi_ba)

        # BA field should be visible (not hidden)
        assert form.fields["business_area"].widget.__class__.__name__ != "HiddenInput"

    def test_form_with_single_program_preselects_field(self, create_user_role_with_permissions):
        """Test that Program field is pre-selected when user has access to only one program."""
        from hope.apps.account.permissions import Permissions

        # Create user with access to single BA and single program
        create_user_role_with_permissions(
            self.user_single_ba,
            [Permissions.GENERIC_IMPORT_DATA],
            self.afghanistan,
            program=self.program_afg,
        )

        form = GenericImportForm(user=self.user_single_ba)

        # BA field should be pre-selected (autoselect behavior)
        assert form.fields["business_area"].initial == self.afghanistan
        # Program field should be pre-selected (autoselect behavior)
        assert form.fields["program"].initial == self.program_afg

    def test_valid_file_upload(self, create_user_role_with_permissions):
        """Test form validation with valid Excel file."""
        from hope.apps.account.permissions import Permissions

        create_user_role_with_permissions(
            self.user_single_ba,
            [Permissions.GENERIC_IMPORT_DATA],
            self.afghanistan,
            program=self.program_afg,
        )

        # Create valid Excel file
        file_content = BytesIO(b"fake excel content")
        uploaded_file = SimpleUploadedFile(
            "test_import.xlsx",
            file_content.getvalue(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

        form_data = {
            "business_area": self.afghanistan.id,
            "program": self.program_afg.id,
        }
        form = GenericImportForm(
            user=self.user_single_ba,
            data=form_data,
            files={"file": uploaded_file},
        )

        assert form.is_valid(), f"Form errors: {form.errors}"

    def test_invalid_file_extension(self, create_user_role_with_permissions):
        """Test that non-Excel files are rejected."""
        from hope.apps.account.permissions import Permissions

        create_user_role_with_permissions(
            self.user_single_ba,
            [Permissions.GENERIC_IMPORT_DATA],
            self.afghanistan,
            program=self.program_afg,
        )

        # Create file with invalid extension
        file_content = BytesIO(b"fake content")
        uploaded_file = SimpleUploadedFile(
            "test_import.pdf",
            file_content.getvalue(),
            content_type="application/pdf",
        )

        form_data = {
            "business_area": self.afghanistan.id,
            "program": self.program_afg.id,
        }
        form = GenericImportForm(
            user=self.user_single_ba,
            data=form_data,
            files={"file": uploaded_file},
        )

        assert not form.is_valid()
        assert "file" in form.errors
        assert "Only Excel files" in str(form.errors["file"])

    def test_file_size_validation(self, create_user_role_with_permissions):
        """Test that files larger than 50MB are rejected."""
        from hope.apps.account.permissions import Permissions

        create_user_role_with_permissions(
            self.user_single_ba,
            [Permissions.GENERIC_IMPORT_DATA],
            self.afghanistan,
            program=self.program_afg,
        )

        # Create oversized file (simulate 51MB)
        # Note: We don't actually create 51MB of data, just set the size attribute
        uploaded_file = SimpleUploadedFile(
            "test_import.xlsx",
            b"fake content",
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        uploaded_file.size = 51 * 1024 * 1024  # 51 MB

        form_data = {
            "business_area": self.afghanistan.id,
            "program": self.program_afg.id,
        }
        form = GenericImportForm(
            user=self.user_single_ba,
            data=form_data,
            files={"file": uploaded_file},
        )

        assert not form.is_valid()
        assert "file" in form.errors
        assert "50 MB" in str(form.errors["file"])

    def test_program_belongs_to_business_area_validation(self, create_user_role_with_permissions):
        """Test that program must belong to selected business area."""
        from hope.apps.account.permissions import Permissions

        create_user_role_with_permissions(
            self.user_multi_ba,
            [Permissions.GENERIC_IMPORT_DATA],
            self.afghanistan,
            program=self.program_afg,
        )
        create_user_role_with_permissions(
            self.user_multi_ba,
            [Permissions.GENERIC_IMPORT_DATA],
            self.other_ba,
            program=self.program_other,
        )

        file_content = BytesIO(b"fake excel content")
        uploaded_file = SimpleUploadedFile(
            "test_import.xlsx",
            file_content.getvalue(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

        # Try to submit program from different BA
        form_data = {
            "business_area": self.afghanistan.id,
            "program": self.program_other.id,  # This program belongs to other_ba!
        }
        form = GenericImportForm(
            user=self.user_multi_ba,
            data=form_data,
            files={"file": uploaded_file},
        )

        # Form should be invalid (Django field validation catches this before clean())
        assert not form.is_valid()
        assert "program" in form.errors or "__all__" in form.errors

    def test_missing_file(self, create_user_role_with_permissions):
        """Test that file field is required."""
        from hope.apps.account.permissions import Permissions

        create_user_role_with_permissions(
            self.user_single_ba,
            [Permissions.GENERIC_IMPORT_DATA],
            self.afghanistan,
            program=self.program_afg,
        )

        form_data = {
            "business_area": self.afghanistan.id,
            "program": self.program_afg.id,
        }
        form = GenericImportForm(
            user=self.user_single_ba,
            data=form_data,
            files={},  # No file
        )

        assert not form.is_valid()
        assert "file" in form.errors

    def test_business_area_queryset_filtered_by_user(self, create_user_role_with_permissions):
        """Test that business_area queryset only includes accessible BAs."""
        from hope.apps.account.permissions import Permissions

        # User only has access to afghanistan
        create_user_role_with_permissions(
            self.user_single_ba,
            [Permissions.GENERIC_IMPORT_DATA],
            self.afghanistan,
        )

        form = GenericImportForm(user=self.user_single_ba)

        # Queryset should only contain afghanistan
        ba_ids = list(form.fields["business_area"].queryset.values_list("id", flat=True))
        assert self.afghanistan.id in ba_ids
        assert self.other_ba.id not in ba_ids
