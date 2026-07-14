"""Tests for program admin functionality."""

from datetime import timedelta
from io import BytesIO
from typing import Any
from unittest.mock import MagicMock, patch
import zipfile

from concurrency.forms import get_signer
from django.contrib.admin import AdminSite
from django.contrib.admin.options import get_content_type_for_model
from django.contrib.auth.models import Permission
from django.core.files.uploadedfile import SimpleUploadedFile
from django.forms.models import model_to_dict
from django.test import Client, RequestFactory
from django.urls import reverse
from django.utils import timezone
import pytest
from rest_framework import status

from extras.test_utils.factories import (
    AreaFactory,
    AreaTypeFactory,
    BusinessAreaFactory,
    IndividualFactory,
    PartnerFactory,
    ProgramFactory,
    RegistrationDataImportFactory,
    RoleAssignmentFactory,
    UserFactory,
)
from hope.admin.program import (
    ProgramAdmin,
    bulk_upload_individuals_photos_action,
    is_cw_merge_queue_retry_enabled,
)
from hope.models import (
    AdminAreaLimitedTo,
    Area,
    AreaType,
    BusinessArea,
    FileTemp,
    Partner,
    Program,
    RegistrationDataImport,
    RoleAssignment,
    User,
)

pytestmark = pytest.mark.django_db


def _program_form_data(program: Program, **overrides: object) -> dict:
    data = model_to_dict(program)
    data["collision_detector"] = program._meta.get_field("collision_detector").value_to_string(program)
    version = data.get("version")
    if version is not None:
        signed = get_signer().sign(version)
        data["version"] = signed if signed is not None else ""
    data.update(overrides)
    return data


@pytest.fixture
def user(db: Any) -> User:
    return UserFactory(username="adminuser", is_staff=True, is_superuser=True)


@pytest.fixture
def business_area(db: Any) -> BusinessArea:
    return BusinessAreaFactory(name="Afghanistan", slug="afghanistan")


@pytest.fixture
def program(business_area: BusinessArea) -> Program:
    return ProgramFactory(business_area=business_area)


@pytest.fixture
def area_type(db: Any) -> AreaType:
    return AreaTypeFactory(name="State1", area_level=1)


@pytest.fixture
def admin_area1(business_area: BusinessArea, area_type: AreaType) -> Area:
    return AreaFactory(
        name=f"{business_area.slug} city 1",
        p_code=f"{business_area.slug} 1",
        area_type=area_type,
    )


@pytest.fixture
def admin_area2(business_area: BusinessArea, area_type: AreaType) -> Area:
    return AreaFactory(
        name=f"{business_area.slug} city 2",
        p_code=f"{business_area.slug} 2",
        area_type=area_type,
    )


@pytest.fixture
def admin_area3(business_area: BusinessArea, area_type: AreaType) -> Area:
    return AreaFactory(
        name=f"{business_area.slug} city 3",
        p_code=f"{business_area.slug} 3",
        area_type=area_type,
    )


@pytest.fixture
def unicef(db: Any) -> Partner:
    return PartnerFactory(name="UNICEF")


@pytest.fixture
def unicef_hq(unicef: Partner) -> Partner:
    return PartnerFactory(name="UNICEF HQ", parent=unicef)


@pytest.fixture
def partner_without_role(db: Any) -> Partner:
    return PartnerFactory(name="Partner without role")


@pytest.fixture
def partner_with_role(business_area: BusinessArea, program: Program) -> Partner:
    partner = PartnerFactory(name="Partner with role")
    RoleAssignment.objects.all().delete()
    RoleAssignmentFactory(
        partner=partner,
        program=program,
        business_area=business_area,
    )
    return partner


@pytest.fixture
def django_app_no_csrf(django_app_factory: Any) -> Any:
    return django_app_factory(csrf_checks=False)


@pytest.fixture
def area_limits_url(program: Program) -> str:
    return reverse("admin:program_program_area_limits", args=[program.pk])


def test_area_limits_get_request(
    django_app: Any,
    user: User,
    program: Program,
    business_area: BusinessArea,
    unicef_hq: Partner,
    partner_with_role: Partner,
    partner_without_role: Partner,
    admin_area1: Area,
    admin_area2: Area,
    admin_area3: Area,
    area_limits_url: str,
) -> None:
    response = django_app.get(area_limits_url, user=user)
    assert response.status_code == 200
    assert "program_area_formset" in response.context
    assert "business_area" in response.context
    assert "areas" in response.context
    assert list(response.context["areas"]) == list(
        Area.objects.filter(area_type__country__business_areas__id=program.business_area.id)
    )
    assert "partners" in response.context
    assert list(response.context["partners"]) == list(Partner.objects.filter(id=partner_with_role.id))
    assert "program" in response.context


def test_area_limits_post_request_create(
    django_app_no_csrf: Any,
    user: User,
    program: Program,
    unicef_hq: Partner,
    partner_with_role: Partner,
    partner_without_role: Partner,
    admin_area1: Area,
    admin_area2: Area,
    admin_area3: Area,
    area_limits_url: str,
) -> None:
    django_app_no_csrf.post(
        area_limits_url,
        user=user,
        params={
            "program_areas-TOTAL_FORMS": "1",
            "program_areas-INITIAL_FORMS": "0",
            "program_areas-0-partner": partner_with_role.id,
            "program_areas-0-areas": [admin_area1.id, admin_area2.id],
        },
    )

    assert AdminAreaLimitedTo.objects.filter(partner=partner_with_role, program=program).exists()
    assert list(AdminAreaLimitedTo.objects.get(partner=partner_with_role, program=program).areas.all()) == list(
        Area.objects.filter(id__in=[admin_area1.id, admin_area2.id])
    )


def test_area_limits_post_request_edit(
    django_app_no_csrf: Any,
    user: User,
    program: Program,
    unicef_hq: Partner,
    partner_with_role: Partner,
    partner_without_role: Partner,
    admin_area1: Area,
    admin_area2: Area,
    admin_area3: Area,
    area_limits_url: str,
) -> None:
    area_limit = AdminAreaLimitedTo.objects.create(partner=partner_with_role, program=program)
    area_limit.areas.set([admin_area1, admin_area2, admin_area3])
    django_app_no_csrf.post(
        area_limits_url,
        user=user,
        params={
            "program_areas-TOTAL_FORMS": "1",
            "program_areas-INITIAL_FORMS": "1",
            "program_areas-0-partner": partner_with_role.id,
            "program_areas-0-areas": [admin_area1.id],
        },
    )
    assert AdminAreaLimitedTo.objects.filter(partner=partner_with_role, program=program).exists()
    assert list(AdminAreaLimitedTo.objects.get(partner=partner_with_role, program=program).areas.all()) == list(
        Area.objects.filter(id__in=[admin_area1.id])
    )


def test_area_limits_post_request_delete(
    django_app_no_csrf: Any,
    user: User,
    program: Program,
    unicef_hq: Partner,
    partner_with_role: Partner,
    partner_without_role: Partner,
    admin_area1: Area,
    admin_area2: Area,
    admin_area3: Area,
    area_limits_url: str,
) -> None:
    area_limit = AdminAreaLimitedTo.objects.create(partner=partner_with_role, program=program)
    area_limit.areas.set([admin_area1, admin_area2, admin_area3])
    django_app_no_csrf.post(
        area_limits_url,
        user=user,
        params={
            "program_areas-TOTAL_FORMS": "1",
            "program_areas-INITIAL_FORMS": "1",
            "program_areas-0-partner": partner_with_role.id,
            "program_areas-0-areas": [],
            "program_areas-0-DELETE": True,
        },
    )
    assert not AdminAreaLimitedTo.objects.filter(partner=partner_with_role, program=program).exists()


def test_bulk_upload_individuals_photos_schedules_job(
    business_area: BusinessArea,
) -> None:
    program = ProgramFactory(business_area=business_area)
    request = RequestFactory().post("/admin/program/bulk-upload")
    request.user = UserFactory(is_staff=True, is_superuser=True)

    form_mock = MagicMock()
    upload = SimpleUploadedFile("photos.zip", b"zip-bytes", content_type="application/zip")
    form_mock.cleaned_data = {"file": upload}
    form_mock.is_valid.return_value = True

    admin_instance = ProgramAdmin(Program, AdminSite())
    admin_instance.get_common_context = MagicMock(return_value={"original": program})
    admin_instance.message_user = MagicMock()

    file_temp = MagicMock(pk="filepk")
    job = MagicMock(pk=789)
    job.queue = MagicMock()

    with (
        patch("hope.admin.program.BulkUploadIndividualsPhotosForm", return_value=form_mock) as form_cls,
        patch("hope.admin.program.FileTemp") as file_temp_cls,
        patch("hope.admin.program.AsyncJob") as async_job_cls,
    ):
        file_temp_cls.objects.create.return_value = file_temp
        async_job_cls.queue_task.return_value = job

        handler = admin_instance.bulk_upload_individuals_photos
        response = handler.__call__(admin_instance, request, program.pk)

    form_cls.assert_called_once()
    file_temp_cls.objects.create.assert_called_once_with(
        object_id=program.pk,
        content_type=get_content_type_for_model(program),
        file=upload,
    )
    async_job_cls.queue_task.assert_called_once()
    admin_instance.message_user.assert_called()
    assert response.status_code == 200


def test_bulk_upload_individuals_photos_action_updates_photos(
    business_area: BusinessArea,
) -> None:
    program = ProgramFactory(business_area=business_area)
    individual = IndividualFactory(program=program, unicef_id="IND-123", business_area=business_area)

    archive = BytesIO()
    with zipfile.ZipFile(archive, "w") as zf:
        zf.writestr("IND-123.jpg", b"image-bytes")
        zf.writestr("IND-999.jpg", b"missing-bytes")

    uploaded = SimpleUploadedFile("photos.zip", archive.getvalue(), content_type="application/zip")
    file_temp = FileTemp.objects.create(
        object_id=str(program.pk),
        content_type=get_content_type_for_model(program),
        file=uploaded,
    )

    job = MagicMock()
    job.config = {"file_id": str(file_temp.pk)}
    job.program = program
    job.errors = {}
    job.save = MagicMock()

    updated = bulk_upload_individuals_photos_action(job)

    individual.refresh_from_db()
    assert updated == 1
    assert individual.photo.name.startswith("IND-123")
    assert individual.photo.name.lower().endswith(".jpg")
    assert job.errors.get("missing_individuals") == ["IND-999.jpg"]
    job.save.assert_called_with(update_fields=["errors"])


def test_check_index_button(django_app: Any, program: Program) -> None:
    user_with_perm = UserFactory(is_staff=True, is_superuser=False)
    perm = Permission.objects.get(codename="can_reindex_programs")
    user_with_perm.user_permissions.add(perm)
    url = reverse("admin:program_program_check_index", args=[program.pk])
    with patch("hope.admin.program.check_program_indexes", return_value=(True, "ok")) as mock_check:
        response = django_app.get(url, user=user_with_perm, expect_errors=True)
    mock_check.assert_called_once_with(str(program.id))
    assert response.status_code == status.HTTP_302_FOUND
    assert reverse("admin:program_program_change", args=[program.pk]) in response.location


def test_check_index_button_no_permission(django_app: Any, program: Program) -> None:
    user_no_perm = UserFactory(is_staff=True, is_superuser=False)
    url = reverse("admin:program_program_check_index", args=[program.pk])
    with patch("hope.admin.program.check_program_indexes") as mock_check:
        response = django_app.get(url, user=user_no_perm, expect_errors=True)
    mock_check.assert_not_called()
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_reindex_program_button(django_app: Any, program: Program) -> None:
    user_with_perm = UserFactory(is_staff=True, is_superuser=False)
    perm = Permission.objects.get(codename="can_reindex_programs")
    user_with_perm.user_permissions.add(perm)
    url = reverse("admin:program_program_reindex_program", args=[program.pk])
    with patch("hope.admin.program.rebuild_program_indexes", return_value=(True, "ok")) as mock_rebuild:
        response = django_app.get(url, user=user_with_perm, expect_errors=True)
    mock_rebuild.assert_called_once_with(str(program.id))
    assert response.status_code == status.HTTP_302_FOUND
    assert reverse("admin:program_program_change", args=[program.pk]) in response.location


def test_reindex_program_button_no_permission(django_app: Any, program: Program) -> None:
    user_no_perm = UserFactory(is_staff=True, is_superuser=False)
    url = reverse("admin:program_program_reindex_program", args=[program.pk])
    with patch("hope.admin.program.rebuild_program_indexes") as mock_rebuild:
        response = django_app.get(url, user=user_no_perm, expect_errors=True)
    mock_rebuild.assert_not_called()
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.fixture
def cw_business_area(db: Any) -> BusinessArea:
    return BusinessAreaFactory(
        name="CW Only",
        slug="cw-only",
        ingest_source=BusinessArea.IngestSource.COUNTRY_WORKSPACE_ONLY,
    )


@pytest.fixture
def cw_program(cw_business_area: BusinessArea) -> Program:
    return ProgramFactory(name="CW Only Program", business_area=cw_business_area)


@pytest.fixture
def admin_client(user: User) -> Client:
    client = Client()
    client.force_login(user)
    return client


@pytest.mark.parametrize(
    ("ingest_source", "status", "expected"),
    [
        (BusinessArea.IngestSource.COUNTRY_WORKSPACE_ONLY, RegistrationDataImport.MERGE_ERROR, True),
        (BusinessArea.IngestSource.COUNTRY_WORKSPACE_ONLY, RegistrationDataImport.IMPORT_ERROR, True),
        (BusinessArea.IngestSource.COUNTRY_WORKSPACE_ONLY, RegistrationDataImport.MERGE_SCHEDULED, False),
        (BusinessArea.IngestSource.COUNTRY_WORKSPACE_ONLY, RegistrationDataImport.MERGED, False),
        (BusinessArea.IngestSource.ALL_EXCEPT_COUNTRY_WORKSPACE, RegistrationDataImport.MERGE_ERROR, False),
    ],
)
def test_is_cw_merge_queue_retry_enabled(ingest_source: str, status: str, expected: bool) -> None:
    business_area = BusinessAreaFactory(ingest_source=ingest_source)
    program = ProgramFactory(business_area=business_area)
    RegistrationDataImportFactory(business_area=business_area, program=program, status=status)
    button = type("Button", (), {"original": program})()

    assert is_cw_merge_queue_retry_enabled(button) is expected


def test_is_cw_merge_queue_retry_disabled_when_no_failed_rdi(cw_program: Program) -> None:
    button = type("Button", (), {"original": cw_program})()

    assert is_cw_merge_queue_retry_enabled(button) is False


@pytest.mark.parametrize(
    "status",
    [RegistrationDataImport.MERGE_ERROR, RegistrationDataImport.IMPORT_ERROR],
)
def test_retry_cw_merge_queue_reschedules_failed_head(
    admin_client: Client,
    cw_business_area: BusinessArea,
    cw_program: Program,
    django_capture_on_commit_callbacks: Any,
    status: str,
) -> None:
    rdi = RegistrationDataImportFactory(
        business_area=cw_business_area,
        program=cw_program,
        status=status,
        error_message="boom",
        sentry_id="abc123",
    )

    url = reverse("admin:program_program_retry_cw_merge_queue", args=[cw_program.pk])
    with patch("hope.apps.registration_data.celery_tasks.rdi_dispatcher_task") as mock_dispatcher:
        with django_capture_on_commit_callbacks(execute=True):
            response = admin_client.get(url)

    assert response.status_code == 302
    rdi.refresh_from_db()
    assert rdi.status == RegistrationDataImport.MERGE_SCHEDULED
    assert rdi.error_message == ""
    assert rdi.sentry_id == ""
    mock_dispatcher.assert_called_once_with(cw_program)


def test_retry_cw_merge_queue_reschedules_oldest_failed(
    admin_client: Client,
    cw_business_area: BusinessArea,
    cw_program: Program,
    django_capture_on_commit_callbacks: Any,
) -> None:
    older = RegistrationDataImportFactory(
        business_area=cw_business_area, program=cw_program, status=RegistrationDataImport.MERGE_ERROR
    )
    newer = RegistrationDataImportFactory(
        business_area=cw_business_area, program=cw_program, status=RegistrationDataImport.MERGE_ERROR
    )
    # import_date is auto_now_add; force a deterministic arrival order.
    RegistrationDataImport.objects.filter(pk=older.pk).update(import_date=timezone.now() - timedelta(hours=1))

    url = reverse("admin:program_program_retry_cw_merge_queue", args=[cw_program.pk])
    with patch("hope.apps.registration_data.celery_tasks.rdi_dispatcher_task"):
        with django_capture_on_commit_callbacks(execute=True):
            response = admin_client.get(url)

    assert response.status_code == status.HTTP_302_FOUND
    older.refresh_from_db()
    newer.refresh_from_db()
    assert older.status == RegistrationDataImport.MERGE_SCHEDULED
    assert newer.status == RegistrationDataImport.MERGE_ERROR


def test_retry_cw_merge_queue_ignores_other_programme(
    admin_client: Client,
    cw_business_area: BusinessArea,
    cw_program: Program,
    django_capture_on_commit_callbacks: Any,
) -> None:
    other_program = ProgramFactory(name="Other CW Program", business_area=cw_business_area)
    target_rdi = RegistrationDataImportFactory(
        business_area=cw_business_area, program=cw_program, status=RegistrationDataImport.MERGE_ERROR
    )
    other_rdi = RegistrationDataImportFactory(
        business_area=cw_business_area, program=other_program, status=RegistrationDataImport.MERGE_ERROR
    )

    url = reverse("admin:program_program_retry_cw_merge_queue", args=[cw_program.pk])
    with patch("hope.apps.registration_data.celery_tasks.rdi_dispatcher_task") as mock_dispatcher:
        with django_capture_on_commit_callbacks(execute=True):
            response = admin_client.get(url)

    assert response.status_code == status.HTTP_302_FOUND
    target_rdi.refresh_from_db()
    other_rdi.refresh_from_db()
    assert target_rdi.status == RegistrationDataImport.MERGE_SCHEDULED
    assert other_rdi.status == RegistrationDataImport.MERGE_ERROR
    mock_dispatcher.assert_called_once_with(cw_program)


def test_retry_cw_merge_queue_no_failed_rdi_does_nothing(
    admin_client: Client,
    cw_program: Program,
    django_capture_on_commit_callbacks: Any,
) -> None:
    url = reverse("admin:program_program_retry_cw_merge_queue", args=[cw_program.pk])
    with patch("hope.apps.registration_data.celery_tasks.rdi_dispatcher_task") as mock_dispatcher:
        with django_capture_on_commit_callbacks(execute=True):
            response = admin_client.get(url)

    assert response.status_code == status.HTTP_302_FOUND
    mock_dispatcher.assert_not_called()


def test_retry_cw_merge_queue_rejected_for_non_cw_business_area(
    admin_client: Client,
    business_area: BusinessArea,
    program: Program,
    django_capture_on_commit_callbacks: Any,
) -> None:
    rdi = RegistrationDataImportFactory(
        business_area=business_area, program=program, status=RegistrationDataImport.MERGE_ERROR
    )

    url = reverse("admin:program_program_retry_cw_merge_queue", args=[program.pk])
    with patch("hope.apps.registration_data.celery_tasks.rdi_dispatcher_task") as mock_dispatcher:
        with django_capture_on_commit_callbacks(execute=True):
            response = admin_client.get(url)

    assert response.status_code == 302
    rdi.refresh_from_db()
    assert rdi.status == RegistrationDataImport.MERGE_ERROR
    mock_dispatcher.assert_not_called()


def test_biometric_flag_readonly_on_non_cw_business_area() -> None:
    ba = BusinessAreaFactory(ingest_source=BusinessArea.IngestSource.ALL_EXCEPT_COUNTRY_WORKSPACE)
    program = ProgramFactory(business_area=ba)
    request = RequestFactory().get("/admin/program/program/")
    request.user = UserFactory(is_staff=True, is_superuser=True)
    admin_instance = ProgramAdmin(Program, AdminSite())

    assert "biometric_deduplication_enabled" in admin_instance.get_readonly_fields(request, program)


def test_biometric_flag_editable_on_cw_business_area() -> None:
    ba = BusinessAreaFactory(ingest_source=BusinessArea.IngestSource.COUNTRY_WORKSPACE_ONLY)
    program = ProgramFactory(business_area=ba)
    request = RequestFactory().get("/admin/program/program/")
    request.user = UserFactory(is_staff=True, is_superuser=True)
    admin_instance = ProgramAdmin(Program, AdminSite())

    assert "biometric_deduplication_enabled" not in admin_instance.get_readonly_fields(request, program)


def test_biometric_flag_editable_on_add_view_without_object() -> None:
    request = RequestFactory().get("/admin/program/program/add/")
    request.user = UserFactory(is_staff=True, is_superuser=True)
    admin_instance = ProgramAdmin(Program, AdminSite())

    assert "biometric_deduplication_enabled" not in admin_instance.get_readonly_fields(request, None)
