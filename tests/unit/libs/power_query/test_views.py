import base64

from django.test import TestCase, override_settings
from django.urls import reverse

import pytest
from power_query.defaults import create_defaults
from power_query.fixtures import (
    FormatterFactory,
    ParametrizerFactory,
    QueryFactory,
    ReportFactory,
)
from power_query.models import Query, Report

from hct_mis_api.apps.account.fixtures import BusinessAreaFactory, UserFactory


@pytest.mark.skip(reason="This test is not working")
@override_settings(POWER_QUERY_DB_ALIAS="default")
@pytest.mark.xfail(reason="This test is failing")
class TestPowerQueryViews(TestCase):
    databases = {"default"}

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        from power_query.models import Query, Report

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


@pytest.mark.skip(reason="This test is not working")
@override_settings(POWER_QUERY_DB_ALIAS="default")
@pytest.mark.xfail(reason="This test is failing")
class TestPowerQueryBasicAuth(TestCase):
    databases = {"default"}

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
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
