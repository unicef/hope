import base64

from django.test import TestCase, override_settings
from django.urls import reverse

from parameterized import parameterized

from hct_mis_api.apps.account.fixtures import BusinessAreaFactory, UserFactory
from hct_mis_api.apps.power_query.defaults import create_defaults
from hct_mis_api.apps.power_query.models import Query, Report
from hct_mis_api.apps.power_query.tests.fixtures import FormatterFactory, ParametrizerFactory, QueryFactory, ReportFactory


@override_settings(POWER_QUERY_DB_ALIAS="default")
class TestPowerQueryViews(TestCase):
    databases = {"default"}

    @classmethod
    def setUpTestData(cls) -> None:
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
        cls.report3: Report = ReportFactory(
            name="Report3", formatter=cls.formatter_html, query=cls.query, owner=cls.user1
        )
        cls.report3.limit_access_to.add(cls.user2)
        cls.report3.save()
        cls.report3.execute()

    def test_valid_report(self) -> None:
        url = reverse("power_query:report", args=[self.report2.pk])
        self.client.login(username=self.report2.owner.username, password="password")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, b">Report2<")

    def test_valid_fetch(self) -> None:
        with self.settings(POWER_QUERY_DB_ALIAS="default"):
            url = reverse("power_query:data", args=[self.report2.documents.first().pk])
            username, password = self.report2.owner.username, "password"
            token = "Basic " + base64.b64encode(f"{username}:{password}".encode()).decode("ascii")
            response = self.client.get(url, HTTP_AUTHORIZATION=token)
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, b">Report2<")

    def test_permission_owner(self) -> None:
        with self.settings(POWER_QUERY_DB_ALIAS="default"):
            url = reverse("power_query:document", args=[self.report2.pk, self.report2.documents.first().pk])
            self.client.login(username=self.report1.owner.username, password="password")
            response = self.client.get(url)
            self.assertEqual(response.status_code, 403)

    def test_permission_business_area(self) -> None:
        with self.settings(POWER_QUERY_DB_ALIAS="default"):
            url = reverse("power_query:document", args=[self.report2.pk, self.report2.documents.first().pk])
            self.client.login(username=self.report1.owner.username, password="password")
            response = self.client.get(url)
            self.assertEqual(response.status_code, 403)

    def test_permission_limit_access_to(self) -> None:
        url = reverse("power_query:report", args=[self.report3.pk])
        self.client.login(username=self.report2.owner.username, password="password")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, b">Report3<")
        url = reverse("power_query:document", args=[self.report3.pk, self.report3.documents.first().pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)
        self.report3.documents.first().limit_access_to.add(self.user2)
        self.report3.documents.first().save()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


@override_settings(POWER_QUERY_DB_ALIAS="default")
class TestPowerQueryBasicAuth(TestCase):
    databases = {"default"}

    @classmethod
    def setUpTestData(cls) -> None:
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

    def test_valid_fetch(self) -> None:
        url = reverse("power_query:data", args=[self.report2.documents.first().pk])
        username, password = self.report2.owner.username, "password"
        token = "Basic " + base64.b64encode(f"{username}:{password}".encode()).decode("ascii")
        response = self.client.get(url, HTTP_AUTHORIZATION=token)
        self.assertEqual(response.status_code, 200)


CONTENT_TYPES = [
    ("application/json", "application/json"),
    ("text/html", "text/html; charset=utf-8"),
    ("text/plain", "text/plain"),
]


@override_settings(POWER_QUERY_DB_ALIAS="default")
class TestPowerQueryResponses(TestCase):
    databases = {"default"}

    @classmethod
    def setUpTestData(cls) -> None:
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
    def test_fetch_no_auth_content_types(self, accept: str, content_type: str) -> None:
        with self.settings(POWER_QUERY_DB_ALIAS="default"):
            url = reverse("power_query:data", args=[self.report2.pk])
            response = self.client.get(url, HTTP_ACCEPT=accept)
            self.assertEqual(response.status_code, 401)
