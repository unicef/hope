from datetime import timedelta
from tempfile import NamedTemporaryFile
from typing import Any, Callable, Dict
from unittest.mock import patch

from django.conf import settings
from django.contrib.messages import get_messages
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.utils import timezone
from django_countries import countries
import pytest
import requests

from hope.apps.account.models import User
from hope.apps.core.base_test_case import BaseTestCase
from hope.apps.core.celery_tasks import (
    upload_new_kobo_template_and_update_flex_fields_task,
    upload_new_kobo_template_and_update_flex_fields_task_with_retry,
)
from hope.apps.core.tasks.upload_new_template_and_update_flex_fields import (
    KoboRetriableError,
    UploadNewKoboTemplateAndUpdateFlexFieldsTask,
)
from hope.models import XLSXKoboTemplate


class MockSuperUser:
    is_active = True
    is_superuser = True
    is_staff = True

    def has_perm(self, perm: Any) -> bool:
        return True


class MockResponse:
    def __init__(self, status_code: Any, data: Dict) -> None:
        self.status_code = status_code
        self.data: Dict = data

    def json(self) -> Dict:
        return self.data


def raise_as_func(exception: BaseException) -> Callable:
    def _raise(*args: Any, **kwargs: Any) -> None:
        raise exception

    return _raise


def get_all_country_choices() -> list[dict]:
    """Return all country choices from django_countries without requiring DB data."""
    return [{"label": {"English(EN)": c.name}, "value": countries.alpha3(c.code)} for c in countries]


class TestKoboTemplateUpload(BaseTestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.admin_user = User.objects.create_superuser(username="root", email="root@root.com", password="password")
        cls.maxDiff = None

    def upload_file(self, filename: str):
        """Helper to upload a test file via the Django test client."""
        file_path = f"{settings.TESTS_ROOT}/apps/core/test_files/{filename}"
        with open(file_path, "rb") as f:
            uploaded_file = SimpleUploadedFile(
                filename,
                f.read(),
                content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        url = reverse("admin:core_xlsxkobotemplate_add")
        self.client.login(username=self.admin_user.username, password="password")

        return self.client.post(url, {"xls_file": uploaded_file}, follow=True, format="multipart")

    @patch("hope.apps.core.field_attributes.core_fields_attributes.Country.get_choices")
    def test_upload_invalid_template(self, mock_country_choices: Any) -> None:
        mock_country_choices.return_value = get_all_country_choices()
        response = self.upload_file("kobo-template-invalid.xlsx")
        form = response.context["form"]

        expected_errors = {
            "__all__": [
                "Field: residence_status_h_c - Choice: RETURNEE is not present in the file",
                "Field: size_h_c - Field must be required",
                "Field: fchild_hoh_i_c - Field is missing",
                "Field: child_hoh_i_c - Field is missing",
                "Field: relationship_i_c - Choice: OTHER is not present in the file",
                "Field: relationship_i_c - Choice: FOSTER_CHILD is not present in the file",
                "Field: relationship_i_c - Choice: FREE_UNION is not present in the file",
                "Field: marital_status_i_c - Choice: MARRIED is not present in the file",
                "Field: marital_status_i_c - Choice: WRONG_CHOICE is not present in HOPE",
                "Field: currency_h_c - Choice: BOV is not present in the file",
                "Field: currency_h_c - Choice: MRU is not present in the file",
                "Field: currency_h_c - Choice: STN is not present in the file",
                "Field: currency_h_c - Choice: UYW is not present in the file",
                "Field: currency_h_c - Choice: VES is not present in the file",
                "Field: currency_h_c - Choice: MRO is not present in HOPE",
                "Field: currency_h_c - Choice: STD is not present in HOPE",
                "Field: currency_h_c - Choice: VEF is not present in HOPE",
                "Field: currency_h_c - Choice: XBA is not present in HOPE",
                "Field: currency_h_c - Choice: XBB is not present in HOPE",
                "Field: currency_h_c - Choice: XBC is not present in HOPE",
                "Field: currency_h_c - Choice: XBD is not present in HOPE",
                "Field: currency_h_c - Choice: XDR is not present in HOPE",
                "Field: currency_h_c - Choice: XPD is not present in HOPE",
                "Field: currency_h_c - Choice: XPT is not present in HOPE",
                "Field: currency_h_c - Choice: XSU is not present in HOPE",
                "Field: currency_h_c - Choice: XTS is not present in HOPE",
                "Field: currency_h_c - Choice: XUA is not present in HOPE",
                "Field: currency_h_c - Choice: XXX is not present in HOPE",
                "Field: tax_id_no_i_c - Field is missing",
                "Field: tax_id_issuer_i_c - Field is missing",
                "Field: national_passport_no_i_c - Field is missing",
                "Field: program_registration_id_h_c - Field is missing",
            ]
        }
        assert form.errors == expected_errors

    @patch(
        "hope.apps.core.celery_tasks.upload_new_kobo_template_and_update_flex_fields_task.run",
        new=lambda *args, **kwargs: None,
    )
    @patch("hope.apps.core.field_attributes.core_fields_attributes.Country.get_choices")
    def test_upload_valid_template(self, mock_country_choices: Any) -> None:
        mock_country_choices.return_value = get_all_country_choices()
        response = self.upload_file("kobo-template-valid.xlsx")
        messages = [m.message for m in get_messages(response.wsgi_request)]

        assert response.status_code == 302 or response.redirect_chain
        assert (
            "Core field validation successful, running KoBo Template upload task..., "
            "Import status will change after task completion"
        ) in messages

    @patch("hope.apps.core.field_attributes.core_fields_attributes.Country.get_choices")
    def test_upload_template_with_validation_error(self, mock_country_choices: Any) -> None:
        mock_country_choices.return_value = get_all_country_choices()
        response = self.upload_file("kobo-template-invalid.xlsx")
        assert "Field: residence_status_h_c" in response.text
        assert "Choice: RETURNEE is not present" in response.text
        assert "Field: size_h_c - Field must be required" in response.text
        assert "Field: tax_id_no_i_c - Field is missing" in response.text
        assert "Upload XLS" in response.text

    def test_upload_template_with_missing_sheet_error(self) -> None:
        response = self.upload_file("kobo-template-invalid-missing-sheet.xlsx")
        form = response.context["form"]
        assert "Missing sheet: 'Worksheet survey does not exist.'" in form.errors["xls_file"]


class TestKoboErrorHandling(BaseTestCase):
    def generate_empty_template(self) -> XLSXKoboTemplate:
        with NamedTemporaryFile(mode="w+b") as tmp_file:
            tmp_file.write(b"abcdefg")
            tmp_file.seek(0)
            template = XLSXKoboTemplate(file_name="test.xlsx", status=XLSXKoboTemplate.UPLOADED)
            template.file.save("test.xlsx", tmp_file)
            template.save()
            return template

    @patch("hope.apps.core.kobo.api.KoboAPI.__init__")
    def test_connection_retry_when_500(self, mock_parent_init: Any) -> None:
        mock_parent_init.return_value = None
        error_500_response = MockResponse(500, {"msg": "test_error"})
        mock_create_template_from_file = raise_as_func(requests.exceptions.HTTPError(response=error_500_response))  # type: ignore
        empty_template = self.generate_empty_template()
        with patch(
            "hope.apps.core.kobo.api.KoboAPI.create_template_from_file",
            mock_create_template_from_file,
        ):
            with pytest.raises(KoboRetriableError):
                UploadNewKoboTemplateAndUpdateFlexFieldsTask().execute(xlsx_kobo_template_id=empty_template.id)
            empty_template.refresh_from_db()
            assert empty_template.status == XLSXKoboTemplate.CONNECTION_FAILED
            assert empty_template.first_connection_failed_time is not None
            one_day_earlier_time = timezone.now() - timedelta(days=1)
            assert empty_template.first_connection_failed_time > one_day_earlier_time

    @patch("hope.apps.core.kobo.api.KoboAPI.__init__")
    def test_unsuccessful_when_400(self, mock_parent_init: Any) -> None:
        mock_parent_init.return_value = None
        error_400_response = MockResponse(400, {"msg": "test_error"})
        mock_create_template_from_file = raise_as_func(requests.exceptions.HTTPError(response=error_400_response))  # type: ignore
        empty_template = self.generate_empty_template()
        with patch(
            "hope.apps.core.kobo.api.KoboAPI.create_template_from_file",
            mock_create_template_from_file,
        ):
            UploadNewKoboTemplateAndUpdateFlexFieldsTask().execute(xlsx_kobo_template_id=empty_template.id)
            empty_template.refresh_from_db()
            assert empty_template.status == XLSXKoboTemplate.UNSUCCESSFUL
            assert empty_template.first_connection_failed_time is None

    @patch("hope.apps.core.kobo.api.KoboAPI.__init__")
    def test_connection_retry_when_connection_problem(self, mock_parent_init: Any) -> None:
        mock_parent_init.return_value = None
        mock_create_template_from_file = raise_as_func(requests.exceptions.ConnectionError())
        empty_template = self.generate_empty_template()
        with patch(
            "hope.apps.core.kobo.api.KoboAPI.create_template_from_file",
            mock_create_template_from_file,
        ):
            with pytest.raises(KoboRetriableError):
                UploadNewKoboTemplateAndUpdateFlexFieldsTask().execute(xlsx_kobo_template_id=empty_template.id)
            empty_template.refresh_from_db()
            assert empty_template.status == XLSXKoboTemplate.CONNECTION_FAILED
            assert empty_template.first_connection_failed_time is not None
            one_day_earlier_time = timezone.now() - timedelta(days=1)
            assert empty_template.first_connection_failed_time > one_day_earlier_time

    @patch("hope.apps.core.kobo.api.KoboAPI.__init__")
    def test_unsuccessful_when_exception(self, mock_parent_init: Any) -> None:
        mock_parent_init.return_value = None
        mock_create_template_from_file = raise_as_func(Exception())
        empty_template = self.generate_empty_template()
        with patch(
            "hope.apps.core.kobo.api.KoboAPI.create_template_from_file",
            mock_create_template_from_file,
        ):
            with pytest.raises(Exception):  # noqa
                UploadNewKoboTemplateAndUpdateFlexFieldsTask().execute(xlsx_kobo_template_id=empty_template.id)
            empty_template.refresh_from_db()
            assert empty_template.status == XLSXKoboTemplate.UNSUCCESSFUL
            assert empty_template.first_connection_failed_time is None

    @patch("hope.apps.core.kobo.api.KoboAPI.__init__")
    def test_unsuccessful_when_error_in_response(self, mock_parent_init: Any) -> None:
        mock_parent_init.return_value = None
        mock_create_template_from_file = lambda *args, **kwargs: (
            {"status": "error"},
            123,
        )
        empty_template = self.generate_empty_template()
        with patch(
            "hope.apps.core.kobo.api.KoboAPI.create_template_from_file",
            mock_create_template_from_file,
        ):
            UploadNewKoboTemplateAndUpdateFlexFieldsTask().execute(xlsx_kobo_template_id=empty_template.id)
            empty_template.refresh_from_db()
            assert empty_template.status == XLSXKoboTemplate.UNSUCCESSFUL
            assert empty_template.first_connection_failed_time is None

    def test_upload_new_kobo_template_and_update_flex_fields_task_with_retry(self) -> None:
        # coverage imports
        empty_template = self.generate_empty_template()
        upload_new_kobo_template_and_update_flex_fields_task_with_retry(str(empty_template.id))

    def test_upload_new_kobo_template_and_update_flex_fields_task(self) -> None:
        # coverage imports
        template = self.generate_empty_template()
        upload_new_kobo_template_and_update_flex_fields_task(str(template.id))
