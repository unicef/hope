from io import BytesIO
from unittest.mock import MagicMock, patch
import zipfile

from django.contrib.admin import AdminSite
from django.contrib.admin.options import get_content_type_for_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import RequestFactory
from django.urls import reverse
from django_webtest import WebTest
import pytest

from extras.test_utils.factories.account import (
    PartnerFactory,
    RoleAssignmentFactory,
    UserFactory,
)
from extras.test_utils.factories.core import create_afghanistan
from extras.test_utils.factories.geo import AreaFactory, AreaTypeFactory
from extras.test_utils.factories.household import IndividualFactory
from extras.test_utils.factories.program import ProgramFactory
from hope.admin.program import ProgramAdmin, bulk_upload_individuals_photos_action
from hope.models import AdminAreaLimitedTo, Area, FileTemp, Partner, Program, RoleAssignment

pytestmark = pytest.mark.django_db()


class ProgramAdminTest(WebTest):
    csrf_checks = False

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.user = UserFactory(username="adminuser", is_staff=True, is_superuser=True)
        cls.business_area = create_afghanistan()
        cls.program = ProgramFactory(business_area=cls.business_area)
        cls.url = reverse("admin:program_program_area_limits", args=[cls.program.pk])

        area_type = AreaTypeFactory(name="State1", area_level=1)
        cls.admin_area1 = AreaFactory(
            name=f"{cls.business_area.slug} city 1",
            p_code=f"{cls.business_area.slug} 1",
            area_type=area_type,
        )
        cls.admin_area2 = AreaFactory(
            name=f"{cls.business_area.slug} city 2",
            p_code=f"{cls.business_area.slug} 2",
            area_type=area_type,
        )
        cls.admin_area3 = AreaFactory(
            name=f"{cls.business_area.slug} city 3",
            p_code=f"{cls.business_area.slug} 3",
            area_type=area_type,
        )
        cls.unicef = PartnerFactory(name="UNICEF")
        cls.unicef_hq = PartnerFactory(name="UNICEF HQ", parent=cls.unicef)
        cls.partner_without_role = PartnerFactory(name="Partner without role")
        cls.partner_with_role = PartnerFactory(name="Partner with role")

        RoleAssignment.objects.all().delete()
        RoleAssignmentFactory(
            partner=cls.partner_with_role,
            program=cls.program,
            business_area=cls.business_area,
        )

    def test_area_limits_get_request(self) -> None:
        response = self.app.get(self.url, user=self.user)
        assert response.status_code == 200
        assert "program_area_formset" in response.context
        assert "business_area" in response.context
        assert "areas" in response.context
        self.assertQuerySetEqual(
            response.context["areas"],
            Area.objects.filter(area_type__country__business_areas__id=self.program.business_area.id),
        )
        assert "partners" in response.context
        self.assertQuerySetEqual(
            response.context["partners"],
            Partner.objects.filter(id=self.partner_with_role.id),
        )
        assert "program" in response.context

    def test_area_limits_post_request_create(self) -> None:
        self.app.post(
            self.url,
            user=self.user,
            params={
                "program_areas-TOTAL_FORMS": "1",
                "program_areas-INITIAL_FORMS": "0",
                "program_areas-0-partner": self.partner_with_role.id,
                "program_areas-0-areas": [self.admin_area1.id, self.admin_area2.id],
            },
        )

        assert AdminAreaLimitedTo.objects.filter(partner=self.partner_with_role, program=self.program).exists()
        self.assertQuerySetEqual(
            AdminAreaLimitedTo.objects.get(partner=self.partner_with_role, program=self.program).areas.all(),
            Area.objects.filter(id__in=[self.admin_area1.id, self.admin_area2.id]),
        )

    def test_area_limits_post_request_edit(self) -> None:
        area_limit = AdminAreaLimitedTo.objects.create(partner=self.partner_with_role, program=self.program)
        area_limit.areas.set([self.admin_area1, self.admin_area2, self.admin_area3])
        self.app.post(
            self.url,
            user=self.user,
            params={
                "program_areas-TOTAL_FORMS": "1",
                "program_areas-INITIAL_FORMS": "1",
                "program_areas-0-partner": self.partner_with_role.id,
                "program_areas-0-areas": [self.admin_area1.id],
            },
        )
        assert AdminAreaLimitedTo.objects.filter(partner=self.partner_with_role, program=self.program).exists()
        self.assertQuerySetEqual(
            AdminAreaLimitedTo.objects.get(partner=self.partner_with_role, program=self.program).areas.all(),
            Area.objects.filter(id__in=[self.admin_area1.id]),
        )

    def test_area_limits_post_request_delete(self) -> None:
        area_limit = AdminAreaLimitedTo.objects.create(partner=self.partner_with_role, program=self.program)
        area_limit.areas.set([self.admin_area1, self.admin_area2, self.admin_area3])
        self.app.post(
            self.url,
            user=self.user,
            params={
                "program_areas-TOTAL_FORMS": "1",
                "program_areas-INITIAL_FORMS": "1",
                "program_areas-0-partner": self.partner_with_role.id,
                "program_areas-0-areas": [],
                "program_areas-0-DELETE": True,
            },
        )
        assert not AdminAreaLimitedTo.objects.filter(partner=self.partner_with_role, program=self.program).exists()

    def test_save_model_existing_program_enable_biometric_deduplication_calls_service(self) -> None:
        """
        If obj.pk exists and biometric_deduplication_enabled changes False -> True,
        admin should create the deduplication set and mark RDIs as pending.
        """
        program = ProgramFactory(business_area=self.business_area, biometric_deduplication_enabled=False)
        obj = Program.objects.get(pk=program.pk)  # original in DB: False
        obj.biometric_deduplication_enabled = True  # changed in memory: True

        url = reverse(
            "admin:program_program_change",
            args=[program.pk],
        )
        request = RequestFactory().post(url)
        request.user = self.user

        admin_instance = ProgramAdmin(Program, AdminSite())

        with patch("hope.admin.program.BiometricDeduplicationService") as service_cls:
            admin_instance.save_model(request, obj, None, True)
            service = service_cls.return_value
            service.mark_rdis_as_pending.assert_called_once_with(program)
            service.delete_deduplication_set.assert_not_called()

    def test_save_model_existing_program_disable_biometric_deduplication_calls_service(self) -> None:
        """
        If obj.pk exists and biometric_deduplication_enabled changes True -> False,
        admin should delete the deduplication set.
        """
        program = ProgramFactory(business_area=self.business_area, biometric_deduplication_enabled=True)
        obj = Program.objects.get(pk=program.pk)
        obj.biometric_deduplication_enabled = False

        url = reverse(
            "admin:program_program_change",
            args=[program.pk],
        )
        request = RequestFactory().post(url)
        request.user = self.user

        admin_instance = ProgramAdmin(Program, AdminSite())

        with patch("hope.admin.program.BiometricDeduplicationService") as service_cls:
            admin_instance.save_model(request, obj, None, True)

            service = service_cls.return_value
            service.delete_deduplication_set.assert_called_once_with(obj)
            service.create_deduplication_set.assert_not_called()
            service.mark_rdis_as_pending.assert_not_called()

    def test_save_model_new_program_does_not_call_deduplication_service(self) -> None:
        """
        When creating a new program (no pk yet), deduplication hooks should not run.
        """
        obj = ProgramFactory.build(
            business_area=self.business_area,
            biometric_deduplication_enabled=True,
        )
        obj.pk = None  # emulate new unsaved instance

        request = RequestFactory().post(reverse("admin:program_program_add"))
        request.user = self.user
        admin_instance = ProgramAdmin(Program, AdminSite())

        with patch("hope.admin.program.BiometricDeduplicationService") as service_cls:
            admin_instance.save_model(request, obj, None, False)

        service_cls.assert_not_called()
        assert obj.pk is not None
        assert Program.objects.filter(pk=obj.pk).exists()


class TestProgramAdminBulkUploadIndividualsPhotos:
    def test_bulk_upload_individuals_photos_schedules_job(self) -> None:
        business_area = create_afghanistan()
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

    def test_bulk_upload_individuals_photos_action_updates_photos(self) -> None:
        business_area = create_afghanistan()
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
