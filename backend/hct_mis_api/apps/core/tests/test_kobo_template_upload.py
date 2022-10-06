from datetime import timedelta
from tempfile import NamedTemporaryFile
from unittest.mock import patch

from django.conf import settings
from django.contrib.admin import AdminSite
from django.contrib.messages import get_messages
from django.contrib.messages.storage.fallback import FallbackStorage
from django.test import Client, RequestFactory
from django.urls import reverse
from django.utils import timezone

import requests

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.core.admin import XLSXKoboTemplateAdmin
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.models import XLSXKoboTemplate
from hct_mis_api.apps.core.tasks.upload_new_template_and_update_flex_fields import (
    KoboRetriableError,
    UploadNewKoboTemplateAndUpdateFlexFieldsTask,
)


class MockSuperUser:
    is_active = True
    is_superuser = True
    is_staff = True

    def has_perm(self, perm):
        return True


class MockResponse:
    def __init__(self, status_code, data):
        self.status_code = status_code
        self.data = data

    def json(self):
        return self.data


def raise_as_func(exception):
    def _raise(*args, **kwargs):
        raise exception

    return _raise


class TestKoboTemplateUpload(APITestCase):
    fixtures = ("hct_mis_api/apps/geo/fixtures/data.json",)

    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
        cls.factory = RequestFactory()
        cls.site = AdminSite()
        cls.admin = XLSXKoboTemplateAdmin(XLSXKoboTemplate, cls.site)

    def prepare_request(self, name):
        with open(
            f"{settings.PROJECT_ROOT}/apps/core/tests/test_files/{name}",
            "rb",
        ) as f:
            data = {"xls_file": f}
            url = reverse("admin:core_xlsxkobotemplate_add")
            request = self.factory.post(url, data=data, format="multipart")
            user = UserFactory()
            user.has_perm = lambda perm: True
            request.user = user

            return request

    def test_upload_invalid_template(self):
        request = self.prepare_request("kobo-template-invalid.xlsx")
        response = self.admin.add_view(request, form_url="", extra_context=None)
        form = response.context_data["form"]
        expected_errors = {
            "__all__": [
                "Field: size_h_c - Field must be required",
                "Field: fchild_hoh_i_c - Field is missing",
                "Field: child_hoh_i_c - Field is missing",
                "Field: relationship_i_c - Choice: OTHER is not present in the file",
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
                "Field: bank_name_i_c - Field is missing",
                "Field: bank_account_number_i_c - Field is missing",
            ]
        }
        self.assertEqual(form.errors, expected_errors)

    @patch(
        "hct_mis_api.apps.core.celery_tasks.upload_new_kobo_template_and_update_flex_fields_task.delay",
        new=lambda *args, **kwargs: None,
    )
    def test_upload_valid_template(self):
        request = self.prepare_request("kobo-template-valid.xlsx")
        setattr(request, "session", "session")
        messages = FallbackStorage(request)
        setattr(request, "_messages", messages)
        response = self.admin.add_view(request, form_url="", extra_context=None)
        stored_messages = tuple(get_messages(request))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            stored_messages[0].message,
            "Core field validation successful, running KoBo Template upload task..., "
            "Import status will change after task completion",
        )


class TestKoboErrorHandling(APITestCase):
    def generate_empty_template(self):
        with NamedTemporaryFile(mode="w+b") as tmp_file:
            tmp_file.write(b"abcdefg")
            tmp_file.seek(0)
            template = XLSXKoboTemplate(file_name="test.xlsx", status=XLSXKoboTemplate.UPLOADED)
            template.file.save("test.xlsx", tmp_file)
            template.save()
            return template

    @patch("hct_mis_api.apps.core.kobo.api.KoboAPI.__init__")
    def test_connection_retry_when_500(self, mock_parent_init):
        mock_parent_init.return_value = None
        error_500_response = MockResponse(500, "test_error")
        mock_create_template_from_file = raise_as_func(requests.exceptions.HTTPError(response=error_500_response))
        empty_template = self.generate_empty_template()
        with patch("hct_mis_api.apps.core.kobo.api.KoboAPI.create_template_from_file", mock_create_template_from_file):
            self.assertRaises(
                KoboRetriableError,
                UploadNewKoboTemplateAndUpdateFlexFieldsTask().execute,
                xlsx_kobo_template_id=empty_template.id,
            )
            empty_template.refresh_from_db()
            self.assertEqual(empty_template.status, XLSXKoboTemplate.CONNECTION_FAILED)
            self.assertNotEqual(empty_template.first_connection_failed_time, None)
            one_day_earlier_time = timezone.now() - timedelta(days=1)
            self.assertTrue(empty_template.first_connection_failed_time > one_day_earlier_time)

    @patch("hct_mis_api.apps.core.kobo.api.KoboAPI.__init__")
    def test_unsuccessful_when_400(self, mock_parent_init):
        mock_parent_init.return_value = None
        error_400_response = MockResponse(400, "test_error")
        mock_create_template_from_file = raise_as_func(requests.exceptions.HTTPError(response=error_400_response))
        empty_template = self.generate_empty_template()
        with patch("hct_mis_api.apps.core.kobo.api.KoboAPI.create_template_from_file", mock_create_template_from_file):
            UploadNewKoboTemplateAndUpdateFlexFieldsTask().execute(xlsx_kobo_template_id=empty_template.id)
            empty_template.refresh_from_db()
            self.assertEqual(empty_template.status, XLSXKoboTemplate.UNSUCCESSFUL)
            self.assertEqual(empty_template.first_connection_failed_time, None)

    @patch("hct_mis_api.apps.core.kobo.api.KoboAPI.__init__")
    def test_connection_retry_when_connection_problem(self, mock_parent_init):
        mock_parent_init.return_value = None
        mock_create_template_from_file = raise_as_func(requests.exceptions.ConnectionError())
        empty_template = self.generate_empty_template()
        with patch("hct_mis_api.apps.core.kobo.api.KoboAPI.create_template_from_file", mock_create_template_from_file):
            self.assertRaises(
                KoboRetriableError,
                UploadNewKoboTemplateAndUpdateFlexFieldsTask().execute,
                xlsx_kobo_template_id=empty_template.id,
            )
            empty_template.refresh_from_db()
            self.assertEqual(empty_template.status, XLSXKoboTemplate.CONNECTION_FAILED)
            self.assertNotEqual(empty_template.first_connection_failed_time, None)
            one_day_earlier_time = timezone.now() - timedelta(days=1)
            self.assertTrue(empty_template.first_connection_failed_time > one_day_earlier_time)

    @patch("hct_mis_api.apps.core.kobo.api.KoboAPI.__init__")
    def test_unsuccessful_when_exception(self, mock_parent_init):
        mock_parent_init.return_value = None
        mock_create_template_from_file = raise_as_func(Exception())
        empty_template = self.generate_empty_template()
        with patch("hct_mis_api.apps.core.kobo.api.KoboAPI.create_template_from_file", mock_create_template_from_file):
            self.assertRaises(
                Exception,
                UploadNewKoboTemplateAndUpdateFlexFieldsTask().execute,
                xlsx_kobo_template_id=empty_template.id,
            )
            empty_template.refresh_from_db()
            self.assertEqual(empty_template.status, XLSXKoboTemplate.UNSUCCESSFUL)
            self.assertEqual(empty_template.first_connection_failed_time, None)

    @patch("hct_mis_api.apps.core.kobo.api.KoboAPI.__init__")
    def test_unsuccessful_when_error_in_response(self, mock_parent_init):
        mock_parent_init.return_value = None
        mock_create_template_from_file = lambda *args, **kwargs: ({"status": "error"}, 123)
        empty_template = self.generate_empty_template()
        with patch("hct_mis_api.apps.core.kobo.api.KoboAPI.create_template_from_file", mock_create_template_from_file):
            UploadNewKoboTemplateAndUpdateFlexFieldsTask().execute(xlsx_kobo_template_id=empty_template.id)
            empty_template.refresh_from_db()
            self.assertEqual(empty_template.status, XLSXKoboTemplate.UNSUCCESSFUL)
            self.assertEqual(empty_template.first_connection_failed_time, None)
