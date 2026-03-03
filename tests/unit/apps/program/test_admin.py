"""Tests for program admin functionality."""

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
from django.test import RequestFactory
from django.urls import reverse
import pytest

from extras.test_utils.factories import (
    AreaFactory,
    AreaTypeFactory,
    BusinessAreaFactory,
    IndividualFactory,
    PartnerFactory,
    ProgramFactory,
    RoleAssignmentFactory,
    UserFactory,
)
from hope.admin.program import ProgramAdmin, ProgramAdminForm, bulk_upload_individuals_photos_action
from hope.apps.registration_data.api.deduplication_engine import DeduplicationEngineAPI
from hope.models import (
    AdminAreaLimitedTo,
    Area,
    AreaType,
    BusinessArea,
    FileTemp,
    Partner,
    Program,
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


def test_form_existing_program_enable_biometric_deduplication_calls_service(
    business_area: BusinessArea,
) -> None:
    program = ProgramFactory(business_area=business_area, biometric_deduplication_enabled=False)
    data = _program_form_data(program, biometric_deduplication_enabled=True)
    form = ProgramAdminForm(data=data, instance=program)

    with patch("hope.admin.program.BiometricDeduplicationService") as service_cls:
        # If obj.pk exists and biometric_deduplication_enabled changes False -> True,
        # admin should create the deduplication set and mark RDIs as pending.
        assert form.is_valid()
        service = service_cls.return_value
        service.create_deduplication_set.assert_called_once_with(program)
        service.mark_rdis_as_pending.assert_called_once_with(program)
        service.delete_deduplication_set.assert_not_called()


def test_form_existing_program_disable_biometric_deduplication_calls_service(
    business_area: BusinessArea,
) -> None:
    """
    If obj.pk exists and biometric_deduplication_enabled changes True -> False,
    admin should delete the deduplication set.
    """
    program = ProgramFactory(business_area=business_area, biometric_deduplication_enabled=True)
    data = _program_form_data(program, biometric_deduplication_enabled=False)
    form = ProgramAdminForm(data=data, instance=program)

    with patch("hope.admin.program.BiometricDeduplicationService") as service_cls:
        assert form.is_valid()
        # If obj.pk exists and biometric_deduplication_enabled changes True -> False,
        # admin should delete the deduplication set.
        service = service_cls.return_value
        service.delete_deduplication_set.assert_called_once_with(program)
        service.create_deduplication_set.assert_not_called()
        service.mark_rdis_as_pending.assert_not_called()


def test_form_existing_program_same_biometric_deduplication_value_does_not_call_service(
    business_area: BusinessArea,
) -> None:
    program = ProgramFactory(business_area=business_area, biometric_deduplication_enabled=False)
    data = _program_form_data(program)
    form = ProgramAdminForm(data=data, instance=program)

    with patch("hope.admin.program.BiometricDeduplicationService") as service_cls:
        assert form.is_valid()

    service_cls.assert_not_called()


def test_form_new_program_biometric_enabled_calls_service(
    business_area: BusinessArea,
) -> None:
    program = ProgramFactory(business_area=business_area, biometric_deduplication_enabled=True)
    programme_code = program.generate_programme_code()
    data = _program_form_data(
        program,
        name=f"{program.name}-new",
        programme_code=programme_code,
        slug=programme_code.lower(),
    )
    form = ProgramAdminForm(data=data)

    with patch("hope.admin.program.BiometricDeduplicationService") as service_cls:
        assert form.is_valid()

    # When creating a new program with biometric deduplication enabled, admin should create the deduplication set.

    service = service_cls.return_value
    service.create_deduplication_set.assert_called_once()
    service.mark_rdis_as_pending.assert_called_once()
    service.delete_deduplication_set.assert_not_called()


def test_form_new_program_biometric_disabled_does_not_call_service(
    business_area: BusinessArea,
) -> None:
    program = ProgramFactory(business_area=business_area, biometric_deduplication_enabled=False)
    programme_code = program.generate_programme_code()
    data = _program_form_data(
        program,
        name=f"{program.name}-new",
        programme_code=programme_code,
        slug=programme_code.lower(),
        biometric_deduplication_enabled=False,
    )
    form = ProgramAdminForm(data=data)

    with patch("hope.admin.program.BiometricDeduplicationService") as service_cls:
        assert form.is_valid()

    service_cls.assert_not_called()


def test_form_api_exception_blocks_save_and_shows_error(
    business_area: BusinessArea,
) -> None:
    program = ProgramFactory(business_area=business_area, biometric_deduplication_enabled=False)
    data = _program_form_data(program, biometric_deduplication_enabled=True)
    form = ProgramAdminForm(data=data, instance=program)

    with patch("hope.admin.program.BiometricDeduplicationService") as service_cls:
        service = service_cls.return_value
        service.create_deduplication_set.side_effect = DeduplicationEngineAPI.DeduplicationEngineAPIError("API failure")
        assert not form.is_valid()

    assert "BiometricDeduplicationService Error" in form.errors["__all__"][0]
    program.refresh_from_db()
    assert program.biometric_deduplication_enabled is False


def test_form_missing_credentials_blocks_save_and_shows_error(
    business_area: BusinessArea,
) -> None:
    program = ProgramFactory(business_area=business_area, biometric_deduplication_enabled=False)
    data = _program_form_data(program, biometric_deduplication_enabled=True)
    form = ProgramAdminForm(data=data, instance=program)

    error = DeduplicationEngineAPI.DeduplicationEngineMissingAPICredentialsError("Missing credentials")
    with patch("hope.admin.program.BiometricDeduplicationService", side_effect=error):
        assert not form.is_valid()

    assert "BiometricDeduplicationService Error" in form.errors["__all__"][0]


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
        async_job_cls.objects.create.return_value = job

        handler = admin_instance.bulk_upload_individuals_photos
        response = handler.__call__(admin_instance, request, program.pk)

    form_cls.assert_called_once()
    file_temp_cls.objects.create.assert_called_once_with(
        object_id=program.pk,
        content_type=get_content_type_for_model(program),
        file=upload,
    )
    async_job_cls.objects.create.assert_called_once()
    job.queue.assert_called_once_with()
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
    assert response.status_code == 302
    assert reverse("admin:program_program_change", args=[program.pk]) in response.location


def test_check_index_button_no_permission(django_app: Any, program: Program) -> None:
    user_no_perm = UserFactory(is_staff=True, is_superuser=False)
    url = reverse("admin:program_program_check_index", args=[program.pk])
    with patch("hope.admin.program.check_program_indexes") as mock_check:
        response = django_app.get(url, user=user_no_perm, expect_errors=True)
    mock_check.assert_not_called()
    assert response.status_code == 403


def test_reindex_program_button(django_app: Any, program: Program) -> None:
    user_with_perm = UserFactory(is_staff=True, is_superuser=False)
    perm = Permission.objects.get(codename="can_reindex_programs")
    user_with_perm.user_permissions.add(perm)
    url = reverse("admin:program_program_reindex_program", args=[program.pk])
    with patch("hope.admin.program.rebuild_program_indexes", return_value=(True, "ok")) as mock_rebuild:
        response = django_app.get(url, user=user_with_perm, expect_errors=True)
    mock_rebuild.assert_called_once_with(str(program.id))
    assert response.status_code == 302
    assert reverse("admin:program_program_change", args=[program.pk]) in response.location


def test_reindex_program_button_no_permission(django_app: Any, program: Program) -> None:
    user_no_perm = UserFactory(is_staff=True, is_superuser=False)
    url = reverse("admin:program_program_reindex_program", args=[program.pk])
    with patch("hope.admin.program.rebuild_program_indexes") as mock_rebuild:
        response = django_app.get(url, user=user_no_perm, expect_errors=True)
    mock_rebuild.assert_not_called()
    assert response.status_code == 403
