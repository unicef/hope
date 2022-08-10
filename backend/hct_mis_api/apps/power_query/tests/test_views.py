import base64
import random

from django.test import TestCase, override_settings
from django.urls import reverse

from parameterized import parameterized

from ...account.fixtures import UserFactory
from ..apps import create_defaults
from .fixtures import FormatterFactory, QueryFactory, ReportFactory


@override_settings(POWER_QUERY_DB_ALIAS="default")
class TestPowerQueryViews(TestCase):
    databases = ["default"]

    @classmethod
    def setUpTestData(cls):
        create_defaults()
        cls.USER_PASSWORD = "123"
        cls.formatter_html = FormatterFactory(name="Queryset To HTML")
        cls.user = UserFactory(is_superuser=True, is_staff=True)
        cls.query = QueryFactory()
        cls.report1 = ReportFactory(formatter=cls.formatter_html, query=cls.query, owner=cls.user)
        cls.report2 = ReportFactory(formatter=cls.formatter_html, query=cls.query, owner=cls.user)
        cls.report2.execute(run_query=True)

    def test_pending_report(self):
        with self.settings(POWER_QUERY_DB_ALIAS="default"):
            url = reverse("power_query:report", args=[self.report1.pk])
            response = self.client.get(url)
            self.assertEqual(response.status_code, 302)
            self.client.force_login(self.report1.owner)
            response = self.client.get(url)
            self.assertEqual(response.status_code, 400)

    def test_pending_fetch(self):
        with self.settings(POWER_QUERY_DB_ALIAS="default"):
            url = reverse("power_query:data", args=[self.report1.pk])
            response = self.client.get(url)
            self.assertEqual(response.status_code, 401)
            self.client.force_login(self.report1.owner)

            response = self.client.get(url)
            self.assertEqual(response.status_code, 400)
            self.assertContains(response, b"This report is not currently available", status_code=400)

    def test_valid_report(self):
        url = reverse("power_query:report", args=[self.report2.pk])
        self.client.force_login(self.report1.owner)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, b"<h1>Query")

    def test_valid_fetch(self):
        with self.settings(POWER_QUERY_DB_ALIAS="default"):
            url = reverse("power_query:data", args=[self.report2.pk])
            self.client.force_login(self.report1.owner)
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, b"<h1>Query")


@override_settings(POWER_QUERY_DB_ALIAS="default")
class TestPowerQueryBasicAuth(TestCase):
    databases = ["default"]

    @classmethod
    def setUpTestData(cls):
        create_defaults()
        cls.USER_PASSWORD = "123"
        cls.formatter_json = FormatterFactory(name="Queryset To JSON")
        cls.user = UserFactory(
            username="superuser-{}".format(random.randint(1, 100)),
            is_superuser=True,
            is_staff=True,
            password=cls.USER_PASSWORD,
        )
        cls.query = QueryFactory()
        cls.report1 = ReportFactory(formatter=cls.formatter_json, query=cls.query, owner=cls.user)
        cls.report2 = ReportFactory(formatter=cls.formatter_json, query=cls.query, owner=cls.user)
        cls.report2.execute(run_query=True)

    def test_pending_fetch(self):
        url = reverse("power_query:data", args=[self.report1.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 401)

        username, password = self.report1.owner.username, self.USER_PASSWORD
        headers = {"HTTP_AUTHORIZATION": "Basic " + base64.b64encode(f"{username}:{password}".encode()).decode("ascii")}
        response = self.client.get(url, **headers)
        self.assertEqual(response.status_code, 400)
        self.assertContains(response, b"This report is not currently available", status_code=400)

    def test_valid_fetch(self):
        url = reverse("power_query:data", args=[self.report2.pk])
        username, password = self.report2.owner.username, self.USER_PASSWORD
        assert password == "123", password
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
        create_defaults()
        cls.USER_PASSWORD = "123"
        cls.formatter_json = FormatterFactory(name="Queryset To JSON")
        cls.user = UserFactory(
            username="superuser-{}".format(random.randint(1, 100)),
            is_superuser=True,
            is_staff=True,
            password=cls.USER_PASSWORD,
        )
        cls.query = QueryFactory()
        cls.report1 = ReportFactory(formatter=cls.formatter_json, query=cls.query, owner=cls.user)
        cls.report2 = ReportFactory(formatter=cls.formatter_json, query=cls.query, owner=cls.user)
        cls.report2.execute(run_query=True)

    @parameterized.expand(CONTENT_TYPES)
    def test_fetch_no_auth_content_types(self, accept, content_type):
        with self.settings(POWER_QUERY_DB_ALIAS="default"):
            url = reverse("power_query:data", args=[self.report2.pk])
            response = self.client.get(url, HTTP_ACCEPT=accept)
            self.assertEqual(response.status_code, 401)

    @parameterized.expand(CONTENT_TYPES)
    def test_fetch_nodata_content_types(self, accept, content_type):
        with self.settings(POWER_QUERY_DB_ALIAS="default"):
            url = reverse("power_query:data", args=[self.report1.pk])
            username, password = self.report1.owner.username, self.USER_PASSWORD
            assert password == "123", password
            headers = {
                "HTTP_AUTHORIZATION": "Basic " + base64.b64encode(f"{username}:{password}".encode()).decode("ascii"),
            }
            response = self.client.get(url, HTTP_ACCEPT=accept, **headers)
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response["content-type"], content_type)
