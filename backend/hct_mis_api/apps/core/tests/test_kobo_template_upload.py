from django.conf import settings
from django.contrib.admin import AdminSite
from django.contrib.messages import get_messages
from django.contrib.messages.storage.fallback import FallbackStorage
from django.test import Client, TestCase, RequestFactory
from django.urls import reverse

from hct_mis_api.apps.core.admin import XLSXKoboTemplateAdmin
from hct_mis_api.apps.core.models import XLSXKoboTemplate


class MockSuperUser:
    is_active = True
    is_superuser = True
    is_staff = True

    def has_perm(self, perm):
        return True


class TestKoboTemplateUpload(TestCase):
    def setUp(self):
        self.client = Client()
        self.factory = RequestFactory()
        self.site = AdminSite()
        self.admin = XLSXKoboTemplateAdmin(XLSXKoboTemplate, self.site)

    def prepare_request(self, name):
        with open(
            f"{settings.PROJECT_ROOT}/apps/core/tests/test_files/{name}",
            "rb",
        ) as f:
            data = {"xls_file": f}
            url = reverse("admin:core_xlsxkobotemplate_add")
            request = self.factory.post(url, data=data, format="multipart")
            request.user = MockSuperUser()

            return request

    def test_upload_invalid_template(self):
        request = self.prepare_request("kobo-template-invalid.xlsx")
        response = self.admin.add_view(request, form_url="", extra_context=None)
        form = response.context_data["form"]
        expected_errors = {
            "__all__": [
                "Field: size_h_c - Field must be required",
                "Field: marital_status_i_c - Choice: {'label': {'English(EN)': 'Married'}, "
                "'value': 'MARRIED'} is not present in the file",
            ]
        }

        self.assertEqual(form.errors, expected_errors)

    def test_upload_valid_template(self):
        request = self.prepare_request("kobo-template-valid.xlsx")
        setattr(request, "session", "session")
        messages = FallbackStorage(request)
        setattr(request, "_messages", messages)
        response = self.admin.add_view(request, form_url="", extra_context=None)
        stored_messages = tuple(get_messages(request))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(stored_messages[0].message, "Your xls file has been imported, ")
