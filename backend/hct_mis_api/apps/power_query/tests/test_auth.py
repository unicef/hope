from django.test import TestCase, override_settings
from django.urls import reverse

from ...account.fixtures import (
    BusinessAreaFactory,
    PartnerFactory,
    UserFactory,
    UserRoleFactory,
)
from ...household.fixtures import HouseholdFactory, create_household
from ..defaults import create_defaults
from ..models import Dataset, Formatter, Query, Report
from .fixtures import (
    FormatterFactory,
    ParametrizerFactory,
    QueryFactory,
    ReportFactory,
    user_grant_office_permission,
)


@override_settings(POWER_QUERY_DB_ALIAS="default")
class TestPowerQuery(TestCase):
    databases = ["default"]

    @classmethod
    def setUpTestData(cls):
        cls.superuser = UserFactory(is_superuser=True, is_staff=True, is_active=True)

        cls.ba1 = BusinessAreaFactory()
        cls.ba2 = BusinessAreaFactory()
        cls.hh1 = create_household({"business_area": cls.ba1})
        cls.hh2 = create_household({"business_area": cls.ba2})
        # hh1 = HouseholdFactory(business_area=ba1)
        # hh2 = HouseholdFactory(business_area=ba2)
        cls.user1 = UserFactory(is_superuser=False, is_staff=False, is_active=True)
        cls.user2 = UserFactory(is_superuser=False, is_staff=False, is_active=True)
        cls.user3 = UserFactory(is_superuser=False, is_staff=False, is_active=True)
        create_defaults()

        p = ParametrizerFactory()

        cls.query1: Query = QueryFactory(name="Query1", code="result=conn.all()", parametrizer=p)
        cls.query1.execute_matrix()
        # cls.query2: Query = QueryFactory(name="Query2", code=f"result=invoke({cls.query1.pk}, arguments)")
        cls.formatter: Formatter = FormatterFactory(name="Queryset To HTML")
        cls.report1: Report = ReportFactory(formatter=cls.formatter, query=cls.query1)
        cls.report1.execute()

    def test_access_granted(self):
        with self.settings(POWER_QUERY_DB_ALIAS="default"):
            url = reverse("power_query:document", args=[self.report1.pk, self.report1.documents.first().pk])
            self.client.login(username=self.user1.username, password="password")
            with user_grant_office_permission(self.user1, self.ba1, "power_query.view_reportdocument"):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200)

    def test_access_forbidden(self):
        with self.settings(POWER_QUERY_DB_ALIAS="default"):
            url = reverse("power_query:document", args=[self.report1.pk, self.report1.documents.first().pk])
            self.client.login(username=self.user2.username, password="password")

            response = self.client.get(url)
            self.assertEqual(response.status_code, 403)
