from django.test import TestCase, override_settings

from hct_mis_api.apps.account.fixtures import BusinessAreaFactory, UserFactory
from hct_mis_api.apps.power_query.backends import PowerQueryBackend
from hct_mis_api.apps.power_query.defaults import create_defaults
from hct_mis_api.apps.power_query.models import Formatter, Query
from hct_mis_api.apps.power_query.tests.fixtures import (
    ParametrizerFactory,
    QueryFactory,
    user_grant_office_permission,
)


@override_settings(POWER_QUERY_DB_ALIAS="default")
class TestBackend(TestCase):
    databases = {"default"}

    @classmethod
    def setUpTestData(cls) -> None:
        from hct_mis_api.apps.power_query.tests.fixtures import Report, ReportFactory

        cls.superuser = UserFactory(is_superuser=True, is_staff=True, is_active=True)
        cls.ba = BusinessAreaFactory()
        cls.backend: PowerQueryBackend = PowerQueryBackend()
        cls.user1 = UserFactory(is_superuser=False, is_staff=False, is_active=True)
        cls.user2 = UserFactory(is_superuser=False, is_staff=False, is_active=True)
        create_defaults()

        p = ParametrizerFactory()
        cls.query1: Query = QueryFactory(parametrizer=p)
        fmt = Formatter.objects.get(name="Queryset To HTML")
        cls.report: Report = ReportFactory(formatter=fmt, query=cls.query1)
        cls.report.limit_access_to.add(cls.user2)
        cls.report.execute(run_query=True)
        cls.document = cls.report.documents.first()
        assert cls.document

    def test_get_office_permissions(self) -> None:
        with user_grant_office_permission(self.user1, self.ba, "power_query.change_report"):
            assert self.backend.get_office_permissions(self.user1, self.ba.slug) == {"power_query.change_report"}

    def test_report_has_perm(self) -> None:
        assert self.backend.has_perm(self.report.owner, "power_query.change_report", self.report)

    def test_report_limit_access(self) -> None:
        assert self.backend.has_perm(self.user2, "power_query.change_report", self.report)

    def test_report_has_perm_fail(self) -> None:
        assert not self.backend.has_perm(self.user1, "power_query.change_report", self.report)

    def test_report_has_perm_fail_miss(self) -> None:
        assert not self.backend.has_perm(None, "power_query.change_report", self.report)

    def test_document_has_perm(self) -> None:
        assert self.backend.has_perm(self.report.owner, "power_query.change_report", self.document)
