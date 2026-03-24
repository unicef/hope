from collections.abc import Callable
from datetime import date, timedelta
from io import BytesIO
from unittest.mock import patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import DatabaseError
from django.test import Client, TestCase
from django.urls import reverse
import pytest

from extras.test_utils.factories import (
    BusinessAreaFactory,
    PartnerFactory,
    ProgramFactory,
    RoleAssignmentFactory,
    RoleFactory,
    UserFactory,
)
from hope.apps.account.permissions import Permissions
from hope.models import BusinessArea, ImportData, Partner, Program, RegistrationDataImport, Role, RoleAssignment, User


@pytest.fixture
def business_area() -> BusinessArea:
    return BusinessAreaFactory()


@pytest.fixture
def program(business_area) -> Program:
    return ProgramFactory(business_area=business_area, status=Program.ACTIVE)


@pytest.fixture
def user() -> User:
    return UserFactory()


@pytest.fixture
def upload_url() -> str:
    return reverse("generic_import:generic-import")


@pytest.fixture
def upload_file() -> Callable:
    def _create(filename="test.xlsx"):
        return SimpleUploadedFile(
            filename,
            BytesIO(b"fake excel content").getvalue(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

    return _create


@pytest.fixture
def authenticated_client(client, user) -> Client:
    client.force_login(user, "django.contrib.auth.backends.ModelBackend")
    return client


@pytest.fixture
def import_role() -> Role:
    return RoleFactory(permissions=[Permissions.GENERIC_IMPORT_DATA.value])


@pytest.fixture
def view_only_role() -> Role:
    return RoleFactory(permissions=[Permissions.RDI_VIEW_LIST.value])


@pytest.fixture
def import_role_assignment(user, import_role, business_area, program) -> RoleAssignment:
    return RoleAssignmentFactory(user=user, role=import_role, business_area=business_area, program=program)


@pytest.fixture
def client_with_import_permission(client, user, import_role_assignment) -> Client:
    client.force_login(user, "django.contrib.auth.backends.ModelBackend")
    return client


@pytest.fixture
def other_business_area() -> BusinessArea:
    return BusinessAreaFactory()


@pytest.fixture
def other_program(other_business_area) -> Program:
    return ProgramFactory(business_area=other_business_area, status=Program.ACTIVE)


@pytest.fixture
def view_only_role_assignment(user, view_only_role, business_area) -> RoleAssignment:
    return RoleAssignmentFactory(user=user, role=view_only_role, business_area=business_area)


@pytest.fixture
def expired_import_role_assignment(user, import_role, business_area) -> RoleAssignment:
    return RoleAssignmentFactory(
        user=user,
        role=import_role,
        business_area=business_area,
        expiry_date=date.today() - timedelta(days=1),
    )


@pytest.fixture
def deactivated_business_area(business_area, import_role_assignment) -> BusinessArea:
    business_area.active = False
    business_area.save()
    return business_area


@pytest.fixture
def test_partner(business_area) -> Partner:
    partner = PartnerFactory()
    partner.allowed_business_areas.add(business_area)
    return partner


@pytest.fixture
def partner_import_role_assignment(test_partner, import_role, business_area, program) -> RoleAssignment:
    return RoleAssignmentFactory(partner=test_partner, role=import_role, business_area=business_area, program=program)


@pytest.fixture
def user_with_test_partner(user, test_partner) -> User:
    user.partner = test_partner
    user.save()
    return user


@pytest.fixture
def program_2(business_area) -> Program:
    return ProgramFactory(business_area=business_area, status=Program.ACTIVE)


@pytest.fixture
def ba_wide_role_assignment(user, import_role, business_area) -> RoleAssignment:
    return RoleAssignmentFactory(user=user, role=import_role, business_area=business_area, program=None)


@pytest.fixture
def import_assignment_on_other_ba(user, import_role, other_business_area, other_program) -> RoleAssignment:
    return RoleAssignmentFactory(user=user, role=import_role, business_area=other_business_area, program=other_program)


@pytest.fixture
def invalid_upload_file() -> SimpleUploadedFile:
    return SimpleUploadedFile("test.pdf", b"fake content", content_type="application/pdf")


@pytest.mark.django_db
def test_unauthenticated_user_is_redirected(client, upload_url):
    response = client.get(upload_url)
    assert response.status_code == 302


@pytest.mark.django_db
def test_user_with_no_business_areas_gets_403(authenticated_client, upload_url):
    response = authenticated_client.get(upload_url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_user_without_import_permission_gets_403(authenticated_client, upload_url, view_only_role_assignment):
    response = authenticated_client.get(upload_url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_user_with_import_permission_can_access_view(client_with_import_permission, upload_url):
    response = client_with_import_permission.get(upload_url)
    assert response.status_code == 200
    assert "generic_import/upload.html" in [t.name for t in response.templates]


@pytest.mark.django_db
@patch("hope.apps.generic_import.views.process_generic_import_task.delay")
def test_successful_upload_creates_objects_and_triggers_task(
    mock_delay, client_with_import_permission, upload_url, upload_file, business_area, program, user
):
    with TestCase.captureOnCommitCallbacks(execute=True):
        response = client_with_import_permission.post(
            upload_url,
            data={
                "business_area": business_area.id,
                "program": program.id,
                "file": upload_file(),
            },
        )

    assert response.status_code == 302
    assert response.url == upload_url

    assert ImportData.objects.count() == 1
    import_data = ImportData.objects.first()
    assert import_data.status == ImportData.STATUS_PENDING
    assert import_data.business_area_slug == business_area.slug
    assert import_data.data_type == ImportData.XLSX
    assert import_data.created_by_id == user.id

    assert RegistrationDataImport.objects.count() == 1
    rdi = RegistrationDataImport.objects.first()
    assert rdi.status == RegistrationDataImport.IMPORT_SCHEDULED
    assert rdi.business_area == business_area
    assert rdi.program == program
    assert rdi.imported_by == user
    assert rdi.data_source == RegistrationDataImport.XLS
    assert rdi.import_data == import_data

    mock_delay.assert_called_once()
    call_kwargs = mock_delay.call_args[1]
    assert call_kwargs["registration_data_import_id"] == str(rdi.id)
    assert call_kwargs["import_data_id"] == str(import_data.id)


@pytest.mark.django_db
@patch("hope.apps.generic_import.views.process_generic_import_task.delay")
def test_upload_without_permission_for_selected_ba_fails(
    mock_delay, client_with_import_permission, upload_url, upload_file, other_business_area, other_program
):
    response = client_with_import_permission.post(
        upload_url,
        data={
            "business_area": other_business_area.id,
            "program": other_program.id,
            "file": upload_file(),
        },
    )

    assert response.status_code == 200
    assert ImportData.objects.count() == 0
    assert RegistrationDataImport.objects.count() == 0
    mock_delay.assert_not_called()


@pytest.mark.django_db
@patch("hope.apps.generic_import.views.process_generic_import_task.delay")
def test_upload_with_invalid_file_shows_errors(
    mock_delay, client_with_import_permission, upload_url, business_area, program, invalid_upload_file
):
    response = client_with_import_permission.post(
        upload_url,
        data={
            "business_area": business_area.id,
            "program": program.id,
            "file": invalid_upload_file,
        },
    )

    assert response.status_code == 200
    assert "form" in response.context
    assert not response.context["form"].is_valid()
    assert ImportData.objects.count() == 0
    mock_delay.assert_not_called()


@pytest.mark.django_db
@patch("hope.apps.generic_import.views.process_generic_import_task.delay")
def test_upload_without_file_shows_errors(
    mock_delay, client_with_import_permission, upload_url, business_area, program
):
    response = client_with_import_permission.post(
        upload_url,
        data={
            "business_area": business_area.id,
            "program": program.id,
        },
    )

    assert response.status_code == 200
    assert "form" in response.context
    assert not response.context["form"].is_valid()
    assert "file" in response.context["form"].errors
    mock_delay.assert_not_called()


@pytest.mark.django_db
@patch("hope.apps.generic_import.views.process_generic_import_task.delay")
def test_rdi_name_format(mock_delay, client_with_import_permission, upload_url, upload_file, business_area, program):
    response = client_with_import_permission.post(
        upload_url,
        data={
            "business_area": business_area.id,
            "program": program.id,
            "file": upload_file(),
        },
    )

    assert response.status_code == 302
    rdi = RegistrationDataImport.objects.first()
    assert "Generic Import" in rdi.name
    assert business_area.slug in rdi.name
    assert program.name in rdi.name


@pytest.mark.django_db
def test_context_data_includes_business_areas(client_with_import_permission, upload_url, business_area):
    response = client_with_import_permission.get(upload_url)

    assert response.status_code == 200
    assert "business_areas" in response.context
    assert business_area in list(response.context["business_areas"])


@pytest.mark.django_db
def test_expired_role_assignment_blocks_access(authenticated_client, upload_url, expired_import_role_assignment):
    response = authenticated_client.get(upload_url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_inactive_business_area_blocks_access(authenticated_client, upload_url, deactivated_business_area):
    response = authenticated_client.get(upload_url)
    assert response.status_code == 403


@pytest.mark.django_db
@patch("hope.apps.generic_import.views.process_generic_import_task.delay")
def test_user_with_partner_permissions(
    mock_delay,
    authenticated_client,
    upload_url,
    upload_file,
    business_area,
    program,
    user_with_test_partner,
    partner_import_role_assignment,
):
    response = authenticated_client.get(upload_url)
    assert response.status_code == 200

    with TestCase.captureOnCommitCallbacks(execute=True):
        response = authenticated_client.post(
            upload_url,
            data={
                "business_area": business_area.id,
                "program": program.id,
                "file": upload_file(),
            },
        )
    assert response.status_code == 302
    mock_delay.assert_called_once()


@pytest.mark.django_db
@patch("hope.apps.generic_import.views.process_generic_import_task.delay")
def test_ba_level_permission_grants_all_programs(
    mock_delay,
    authenticated_client,
    upload_url,
    upload_file,
    business_area,
    program,
    program_2,
    ba_wide_role_assignment,
):
    with TestCase.captureOnCommitCallbacks(execute=True):
        response_1 = authenticated_client.post(
            upload_url,
            data={
                "business_area": business_area.id,
                "program": program.id,
                "file": upload_file(),
            },
        )
    assert response_1.status_code == 302

    with TestCase.captureOnCommitCallbacks(execute=True):
        response_2 = authenticated_client.post(
            upload_url,
            data={
                "business_area": business_area.id,
                "program": program_2.id,
                "file": upload_file(),
            },
        )
    assert response_2.status_code == 302

    assert mock_delay.call_count == 2


@pytest.mark.django_db
@patch("hope.apps.generic_import.views.process_generic_import_task.delay")
@patch("hope.apps.generic_import.views.ImportData.objects.create")
def test_database_error_prevents_task_trigger(
    mock_create, mock_delay, client_with_import_permission, upload_url, upload_file, business_area, program
):
    mock_create.side_effect = DatabaseError("Database error")

    response = client_with_import_permission.post(
        upload_url,
        data={
            "business_area": business_area.id,
            "program": program.id,
            "file": upload_file(),
        },
    )

    assert response.status_code == 200
    mock_delay.assert_not_called()


@pytest.mark.django_db
@patch("hope.apps.generic_import.views.process_generic_import_task.delay")
def test_upload_to_ba_without_import_permission_for_that_ba(
    mock_delay,
    authenticated_client,
    upload_url,
    upload_file,
    business_area,
    program,
    import_assignment_on_other_ba,
    view_only_role_assignment,
):
    response = authenticated_client.post(
        upload_url,
        data={
            "business_area": business_area.id,
            "program": program.id,
            "file": upload_file(),
        },
    )

    assert response.status_code == 200
    mock_delay.assert_not_called()
    messages_list = list(response.context["messages"])
    assert any("permission" in str(m).lower() for m in messages_list)


@pytest.mark.django_db
@patch("hope.apps.generic_import.views.process_generic_import_task.delay")
def test_form_invalid_shows_non_field_errors(
    mock_delay,
    client_with_import_permission,
    upload_url,
    upload_file,
    business_area,
    import_assignment_on_other_ba,
    other_program,
):
    response = client_with_import_permission.post(
        upload_url,
        data={
            "business_area": business_area.id,
            "program": other_program.id,
            "file": upload_file(),
        },
    )

    assert response.status_code == 200
    mock_delay.assert_not_called()
