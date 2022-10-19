import csv
from io import StringIO

from django.contrib import admin
from django.core import mail
from django.urls import reverse

from django_webtest import WebTest

from hct_mis_api.apps.account.fixtures import UserFactory, UserRoleFactory
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea


class TestDOAP(WebTest):
    @classmethod
    def setUpTestData(cls):
        create_afghanistan()
        cls.business_area = BusinessArea.objects.get(slug="afghanistan")
        cls.user = UserFactory(is_superuser=True, is_staff=True)
        cls.user_role = UserRoleFactory(role__name="Approver", role__subsystem="CA", business_area=cls.business_area)
        cls.officer = cls.user_role.user

    def test_get_matrix(self):
        adm = admin.site._registry[BusinessArea]
        matrix = adm._get_doap_matrix(self.business_area)
        self.assertEqual(len(matrix), 2)
        expected_headers = ["org", "Last Name", "First Name", "Email", "Business Unit", "Partner Instance ID", "Action"]
        self.assertEqual(matrix[0][0:7], expected_headers)
        self.assertEqual(
            list(matrix[1].values())[0:7],
            [
                "UNICEF",
                self.officer.last_name,
                self.officer.first_name,
                self.officer.email,
                f"UNICEF - {self.business_area.name}",
                int(self.business_area.code),
                "ADD",
            ],
        )

    def test_show_doap(self):
        url = reverse("admin:core_businessarea_view_ca_doap", args=[self.business_area.pk])
        res = self.app.get(url, user=self.user)
        assert self.user_role.user.email in str(res.content)

    def test_send_doap(self):
        url = reverse("admin:core_businessarea_send_doap", args=[self.business_area.pk])
        self.app.get(url, user=self.user)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "CashAssist - UNICEF - Afghanistan user updates")

    def test_export_doap(self):
        url = reverse("admin:core_businessarea_export_doap", args=[self.business_area.pk])
        res = self.app.get(url, user=self.user)
        self.assertEqual(res.content_type, "text/csv")
        csv_content = list(csv.reader(StringIO(res.content.decode())))
        expected_headers = ["org", "Last Name", "First Name", "Email", "Business Unit", "Partner Instance ID", "Action"]
        self.assertEqual(csv_content[0][0:7], expected_headers)
        self.assertEqual(
            csv_content[1][0:7],
            [
                "UNICEF",
                self.officer.last_name,
                self.officer.first_name,
                self.officer.email,
                f"UNICEF - {self.business_area.name}",
                str(int(self.business_area.code)),
                "ADD",
            ],
        )
