import csv
from io import StringIO

from django.contrib import admin
from django.core import mail
from django.core.management import call_command
from django.urls import reverse

from django_webtest import WebTest

from hct_mis_api.apps.account.fixtures import RoleFactory, UserFactory, UserRoleFactory
from hct_mis_api.apps.core.models import BusinessArea


class TestDOAP(WebTest):
    def setUp(self):
        call_command("loadbusinessareas")
        self.business_area = BusinessArea.objects.get(slug="afghanistan")
        self.user = UserFactory(is_superuser=True, is_staff=True)
        self.user_role = UserRoleFactory(role__name="Approver", role__subsystem="CA", business_area=self.business_area)
        self.officer = self.user_role.user

    def test_get_matrix(self):
        adm = admin.site._registry[BusinessArea]
        matrix = adm._get_doap_matrix(self.business_area)
        self.assertEqual(len(matrix), 2)
        self.assertEqual(matrix[0][0:5], ["org", "Last Name", "First Name", "Email", "Action"])
        self.assertEqual(
            list(matrix[1].values())[0:5],
            ["UNICEF", self.officer.last_name, self.officer.first_name, self.officer.email, "ADD"],
        )

    def test_show_doap(self):
        url = reverse("admin:core_businessarea_view_ca_doap", args=[self.business_area.pk])
        res = self.app.get(url, user=self.user)
        assert self.user_role.user.email in str(res.content)

    def test_send_doap(self):
        url = reverse("admin:core_businessarea_send_doap", args=[self.business_area.pk])
        res = self.app.get(url, user=self.user)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "DOAP updates for Afghanistan")

    def test_export_doap(self):
        url = reverse("admin:core_businessarea_export_doap", args=[self.business_area.pk])
        res = self.app.get(url, user=self.user)
        self.assertEqual(res.content_type, "text/csv")
        csv_content = list(csv.reader(StringIO(res.content.decode())))
        self.assertEqual(csv_content[0][0:5], ["org", "Last Name", "First Name", "Email", "Action"])
        self.assertEqual(
            csv_content[1][0:5], ["UNICEF", self.officer.last_name, self.officer.first_name, self.officer.email, "ADD"]
        )
