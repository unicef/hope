from django.test import TestCase, override_settings
from django.urls import reverse

import pytest
from power_query.fixtures import (
    FormatterFactory,
    ParametrizerFactory,
    QueryFactory,
    ReportFactory,
)
from power_query.models import Formatter, Query, Report

from hct_mis_api.apps.account.fixtures import BusinessAreaFactory, UserFactory
from hct_mis_api.apps.household.fixtures import create_household
from hct_mis_api.libs.power_query.defaults import hope_create_defaults
from tests.unit.libs.power_query.utils import user_grant_office_permission


@pytest.mark.skip(reason="This test is not working")
@override_settings(POWER_QUERY_DB_ALIAS="default")
@pytest.mark.xfail(reason="This test is failing")
class TestPowerQuery(TestCase):
    databases = {"default"}

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.superuser = UserFactory(is_superuser=True, is_staff=True, is_active=True)

        # code should be unique but the test depends on both BAs having the same, empty code
        cls.ba1 = BusinessAreaFactory()
        cls.hh1 = create_household({"business_area": cls.ba1})
        cls.user1 = UserFactory(is_superuser=False, is_staff=False, is_active=True)
        cls.user2 = UserFactory(is_superuser=False, is_staff=False, is_active=True)
        cls.user3 = UserFactory(is_superuser=False, is_staff=False, is_active=True)
        hope_create_defaults()

        p = ParametrizerFactory()

        cls.query1: Query = QueryFactory(name="Query1", code="result=conn.all()", parametrizer=p)
        res = cls.query1.execute_matrix()
        assert res
        cls.formatter: Formatter = FormatterFactory(name="Queryset To HTML")
        cls.report1: Report = ReportFactory(formatter=cls.formatter, query=cls.query1)
        cls.report1.execute()

    def test_access_granted(self) -> None:
        with self.settings(POWER_QUERY_DB_ALIAS="default"):
            url = reverse("power_query:document", args=[self.report1.pk, self.report1.documents.first().pk])
            self.client.login(username=self.user1.username, password="password")
            with user_grant_office_permission(self.user1, self.ba1, "power_query.view_reportdocument"):
                response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_access_forbidden(self) -> None:
        with self.settings(POWER_QUERY_DB_ALIAS="default"):
            url = reverse("power_query:document", args=[self.report1.pk, self.report1.documents.first().pk])
            self.client.login(username=self.user2.username, password="password")
            response = self.client.get(url)
            self.assertEqual(response.status_code, 403)
