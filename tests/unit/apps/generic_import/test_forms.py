from io import BytesIO

from django.core.files.uploadedfile import SimpleUploadedFile
import pytest

from extras.test_utils.factories import BusinessAreaFactory, ProgramFactory, UserFactory
from hope.apps.account.permissions import Permissions
from hope.apps.generic_import.forms import GenericImportForm
from hope.models import BusinessArea, Program, User


@pytest.fixture
def business_area() -> BusinessArea:
    return BusinessAreaFactory()


@pytest.fixture
def other_business_area() -> BusinessArea:
    return BusinessAreaFactory()


@pytest.fixture
def program(business_area) -> Program:
    return ProgramFactory(business_area=business_area)


@pytest.fixture
def other_program(other_business_area) -> Program:
    return ProgramFactory(business_area=other_business_area)


@pytest.fixture
def restricted_program(business_area) -> Program:
    return ProgramFactory(business_area=business_area)


@pytest.fixture
def user() -> User:
    return UserFactory(partner=None)


@pytest.fixture
def superuser() -> User:
    return UserFactory(is_superuser=True, partner=None)


@pytest.mark.django_db
def test_form_with_single_business_area_preselects_field(user, business_area, create_user_role_with_permissions):
    create_user_role_with_permissions(
        user,
        [Permissions.GENERIC_IMPORT_DATA],
        business_area,
    )

    form = GenericImportForm(user=user)

    assert form.fields["business_area"].initial == business_area
    assert form.fields["business_area"].queryset.count() == 1


@pytest.mark.django_db
def test_form_with_multiple_business_areas_shows_field(
    user, business_area, other_business_area, create_user_role_with_permissions
):
    create_user_role_with_permissions(
        user,
        [Permissions.GENERIC_IMPORT_DATA],
        business_area,
    )
    create_user_role_with_permissions(
        user,
        [Permissions.GENERIC_IMPORT_DATA],
        other_business_area,
    )

    form = GenericImportForm(user=user)

    assert form.fields["business_area"].widget.__class__.__name__ != "HiddenInput"


@pytest.mark.django_db
def test_form_with_single_program_preselects_field(user, business_area, program, create_user_role_with_permissions):
    create_user_role_with_permissions(
        user,
        [Permissions.GENERIC_IMPORT_DATA],
        business_area,
        program=program,
    )

    form = GenericImportForm(user=user)

    assert form.fields["business_area"].initial == business_area
    assert form.fields["program"].initial == program


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("filename", "content_type"),
    [
        ("test_import.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"),
        ("test_import.xls", "application/vnd.ms-excel"),
    ],
    ids=["xlsx", "xls"],
)
def test_valid_excel_file_upload(
    user, business_area, program, create_user_role_with_permissions, filename, content_type
):
    create_user_role_with_permissions(
        user,
        [Permissions.GENERIC_IMPORT_DATA],
        business_area,
        program=program,
    )

    file_content = BytesIO(b"fake excel content")
    uploaded_file = SimpleUploadedFile(
        filename,
        file_content.getvalue(),
        content_type=content_type,
    )

    form_data = {
        "business_area": business_area.id,
        "program": program.id,
    }
    form = GenericImportForm(
        user=user,
        data=form_data,
        files={"file": uploaded_file},
    )

    assert form.is_valid(), f"Form errors: {form.errors}"


@pytest.mark.django_db
def test_invalid_file_extension_rejects_non_excel(user, business_area, program, create_user_role_with_permissions):
    create_user_role_with_permissions(
        user,
        [Permissions.GENERIC_IMPORT_DATA],
        business_area,
        program=program,
    )

    file_content = BytesIO(b"fake content")
    uploaded_file = SimpleUploadedFile(
        "test_import.pdf",
        file_content.getvalue(),
        content_type="application/pdf",
    )

    form_data = {
        "business_area": business_area.id,
        "program": program.id,
    }
    form = GenericImportForm(
        user=user,
        data=form_data,
        files={"file": uploaded_file},
    )

    assert not form.is_valid()
    assert "file" in form.errors
    assert "Only Excel files" in str(form.errors["file"])


@pytest.mark.django_db
def test_file_size_validation_rejects_oversized_file(user, business_area, program, create_user_role_with_permissions):
    create_user_role_with_permissions(
        user,
        [Permissions.GENERIC_IMPORT_DATA],
        business_area,
        program=program,
    )

    uploaded_file = SimpleUploadedFile(
        "test_import.xlsx",
        b"fake content",
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    uploaded_file.size = 51 * 1024 * 1024  # 51 MB

    form_data = {
        "business_area": business_area.id,
        "program": program.id,
    }
    form = GenericImportForm(
        user=user,
        data=form_data,
        files={"file": uploaded_file},
    )

    assert not form.is_valid()
    assert "file" in form.errors
    assert "50 MB" in str(form.errors["file"])


@pytest.mark.django_db
def test_program_belongs_to_business_area_validation(
    user, business_area, other_business_area, program, other_program, create_user_role_with_permissions
):
    create_user_role_with_permissions(
        user,
        [Permissions.GENERIC_IMPORT_DATA],
        business_area,
        program=program,
    )
    create_user_role_with_permissions(
        user,
        [Permissions.GENERIC_IMPORT_DATA],
        other_business_area,
        program=other_program,
    )

    file_content = BytesIO(b"fake excel content")
    uploaded_file = SimpleUploadedFile(
        "test_import.xlsx",
        file_content.getvalue(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

    form_data = {
        "business_area": business_area.id,
        "program": other_program.id,
    }
    form = GenericImportForm(
        user=user,
        data=form_data,
        files={"file": uploaded_file},
    )

    assert not form.is_valid()
    assert "program" in form.errors or "__all__" in form.errors


@pytest.mark.django_db
def test_missing_file_is_required(user, business_area, program, create_user_role_with_permissions):
    create_user_role_with_permissions(
        user,
        [Permissions.GENERIC_IMPORT_DATA],
        business_area,
        program=program,
    )

    form_data = {
        "business_area": business_area.id,
        "program": program.id,
    }
    form = GenericImportForm(
        user=user,
        data=form_data,
        files={},
    )

    assert not form.is_valid()
    assert "file" in form.errors


@pytest.mark.django_db
def test_business_area_queryset_filtered_by_user(
    user, business_area, other_business_area, create_user_role_with_permissions
):
    create_user_role_with_permissions(
        user,
        [Permissions.GENERIC_IMPORT_DATA],
        business_area,
    )

    form = GenericImportForm(user=user)

    ba_ids = list(form.fields["business_area"].queryset.values_list("id", flat=True))
    assert business_area.id in ba_ids
    assert other_business_area.id not in ba_ids


@pytest.mark.django_db
def test_superuser_has_access_to_all_business_areas(superuser, business_area, other_business_area):
    form = GenericImportForm(user=superuser)

    ba_ids = list(form.fields["business_area"].queryset.values_list("id", flat=True))
    assert business_area.id in ba_ids
    assert other_business_area.id in ba_ids


@pytest.mark.django_db
def test_clean_program_with_invalid_string_id(user, business_area, create_user_role_with_permissions):
    create_user_role_with_permissions(
        user,
        [Permissions.GENERIC_IMPORT_DATA],
        business_area,
    )

    file_content = BytesIO(b"fake excel content")
    uploaded_file = SimpleUploadedFile(
        "test_import.xlsx",
        file_content.getvalue(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

    form_data = {
        "business_area": business_area.id,
        "program": "99999999-9999-9999-9999-999999999999",
    }
    form = GenericImportForm(
        user=user,
        data=form_data,
        files={"file": uploaded_file},
    )

    assert not form.is_valid()
    assert "program" in form.errors
    assert "valid choice" in str(form.errors["program"]).lower() or "does not exist" in str(form.errors["program"])


@pytest.mark.django_db
def test_user_without_program_access(
    user, business_area, program, restricted_program, create_user_role_with_permissions
):
    create_user_role_with_permissions(
        user,
        [Permissions.GENERIC_IMPORT_DATA],
        business_area,
        program=program,
    )

    file_content = BytesIO(b"fake excel content")
    uploaded_file = SimpleUploadedFile(
        "test_import.xlsx",
        file_content.getvalue(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

    form_data = {
        "business_area": business_area.id,
        "program": restricted_program.id,
    }
    form = GenericImportForm(
        user=user,
        data=form_data,
        files={"file": uploaded_file},
    )

    assert not form.is_valid()
    error_message = str(form.errors)
    assert "do not have access" in error_message or "program" in form.errors


@pytest.mark.django_db
def test_business_area_widget_adds_data_slug(user, business_area, create_user_role_with_permissions):
    create_user_role_with_permissions(
        user,
        [Permissions.GENERIC_IMPORT_DATA],
        business_area,
    )

    form = GenericImportForm(user=user)

    html = str(form["business_area"])

    assert "data-slug" in html
    assert business_area.slug in html


@pytest.mark.django_db
def test_program_widget_adds_data_slug(user, business_area, program, create_user_role_with_permissions):
    create_user_role_with_permissions(
        user,
        [Permissions.GENERIC_IMPORT_DATA],
        business_area,
        program=program,
    )

    form = GenericImportForm(user=user)

    form.fields["program"].initial = program

    html = str(form["program"])

    assert program.name in html or str(program.id) in html
