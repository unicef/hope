import base64

from django.test import TestCase, override_settings
from django.urls import reverse

from parameterized import parameterized

from ...account.fixtures import BusinessAreaFactory, UserFactory
from ..defaults import create_defaults
from ..models import Query, Report
from .fixtures import FormatterFactory, ParametrizerFactory, QueryFactory, ReportFactory


@override_settings(POWER_QUERY_DB_ALIAS="default")
class TestPowerQueryViews(TestCase):
    databases = ["default"]

    @classmethod
    def setUpTestData(cls):
        from hct_mis_api.apps.power_query.models import Query, Report

        cls.superuser = UserFactory(is_superuser=True, is_staff=True, is_active=True)
        cls.user1 = UserFactory(is_superuser=False, is_staff=False, is_active=True)
        cls.user2 = UserFactory(is_superuser=False, is_staff=False, is_active=True)
        BusinessAreaFactory()
        create_defaults()
        cls.formatter_html = FormatterFactory(name="Queryset To HTML")
        # hh = ContentType.objects.get(app_label="household", model="household")

        p = ParametrizerFactory()
        cls.query: Query = QueryFactory(name="HH", parametrizer=p)
        cls.query.execute_matrix()
        cls.report1: Report = ReportFactory(
            name="Report1", formatter=cls.formatter_html, query=cls.query, owner=cls.user1
        )
        cls.report2: Report = ReportFactory(
            name="Report2", formatter=cls.formatter_html, query=cls.query, owner=cls.user2
        )
        cls.report2.execute()

    def test_valid_report(self):
        url = reverse("power_query:report", args=[self.report2.pk])
        self.client.login(username=self.report2.owner.username, password="password")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, b">Report2<")

    def test_valid_fetch(self):
        with self.settings(POWER_QUERY_DB_ALIAS="default"):
            url = reverse("power_query:data", args=[self.report2.documents.first().pk])
            username, password = self.report2.owner.username, "password"
            headers = {
                "HTTP_AUTHORIZATION": "Basic " + base64.b64encode(f"{username}:{password}".encode()).decode("ascii"),
            }
            response = self.client.get(url, **headers)
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, b">Report2<")

    def test_permission_owner(self):
        with self.settings(POWER_QUERY_DB_ALIAS="default"):
            url = reverse("power_query:document", args=[self.report2.pk, self.report2.documents.first().pk])
            self.client.login(username=self.report1.owner.username, password="password")
            response = self.client.get(url)
            self.assertEqual(response.status_code, 403)

    def test_permission_business_area(self):
        with self.settings(POWER_QUERY_DB_ALIAS="default"):
            url = reverse("power_query:document", args=[self.report2.pk, self.report2.documents.first().pk])
            self.client.login(username=self.report1.owner.username, password="password")
            response = self.client.get(url)
            self.assertEqual(response.status_code, 403)


@override_settings(POWER_QUERY_DB_ALIAS="default")
class TestPowerQueryBasicAuth(TestCase):
    databases = ["default"]

    @classmethod
    def setUpTestData(cls):
        cls.superuser = UserFactory(is_superuser=True, is_staff=True, is_active=True)
        cls.user1 = UserFactory(is_superuser=False, is_staff=False, is_active=True)
        cls.user2 = UserFactory(is_superuser=False, is_staff=False, is_active=True)
        BusinessAreaFactory()
        create_defaults()

        cls.formatter_json = FormatterFactory(name="Queryset To JSON", content_type="json", code="")
        cls.query: Query = QueryFactory()
        cls.query.execute_matrix()
        cls.report1: Report = ReportFactory(formatter=cls.formatter_json, query=cls.query, owner=cls.user1)
        cls.report2: Report = ReportFactory(formatter=cls.formatter_json, query=cls.query, owner=cls.user2)
        cls.report2.execute()

    def test_valid_fetch(self):
        url = reverse("power_query:data", args=[self.report2.documents.first().pk])
        username, password = self.report2.owner.username, "password"
        headers = {
            "HTTP_AUTHORIZATION": "Basic " + base64.b64encode(f"{username}:{password}".encode()).decode("ascii"),
        }
        response = self.client.get(url, **headers)
        self.assertEqual(response.status_code, 200)


CONTENT_TYPES = [
    ("application/json", "application/json"),
    ("text/html", "text/html; charset=utf-8"),
    ("text/plain", "text/plain"),
]


@override_settings(POWER_QUERY_DB_ALIAS="default")
class TestPowerQueryResponses(TestCase):
    databases = ["default"]

    @classmethod
    def setUpTestData(cls):
        cls.superuser = UserFactory(is_superuser=True, is_staff=True, is_active=True)
        cls.user1 = UserFactory(is_superuser=False, is_staff=False, is_active=True)
        cls.user2 = UserFactory(is_superuser=False, is_staff=False, is_active=True)
        BusinessAreaFactory()
        create_defaults()
        cls.formatter_json = FormatterFactory(name="Queryset To JSON", content_type="json", code="")
        cls.query = QueryFactory()
        cls.report1: Report = ReportFactory(formatter=cls.formatter_json, query=cls.query, owner=cls.user1)
        cls.report2: Report = ReportFactory(formatter=cls.formatter_json, query=cls.query, owner=cls.user2)
        cls.report2.execute(run_query=True)

    @parameterized.expand(CONTENT_TYPES)
    def test_fetch_no_auth_content_types(self, accept, content_type):
        with self.settings(POWER_QUERY_DB_ALIAS="default"):
            url = reverse("power_query:data", args=[self.report2.pk])
            response = self.client.get(url, HTTP_ACCEPT=accept)
            self.assertEqual(response.status_code, 401)
