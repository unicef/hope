from django.test import TestCase, override_settings

from hct_mis_api.apps.account.fixtures import BusinessAreaFactory, UserFactory
from hct_mis_api.apps.power_query.celery_tasks import (
    refresh_report,
    refresh_reports,
    run_background_query,
)
from hct_mis_api.apps.power_query.defaults import create_defaults
from hct_mis_api.apps.power_query.models import Formatter, Parametrizer, Query, Report
from hct_mis_api.apps.power_query.tests.fixtures import (
    FormatterFactory,
    ParametrizerFactory,
    QueryFactory,
    ReportFactory,
)


@override_settings(POWER_QUERY_DB_ALIAS="default")
class TestPowerQueryCelery(TestCase):
    databases = {"default"}

    @classmethod
    def setUpTestData(cls) -> None:
        cls.superuser = UserFactory(is_superuser=True, is_staff=True, is_active=True)
        cls.user1 = UserFactory(is_superuser=False, is_staff=False, is_active=True)
        cls.user2 = UserFactory(is_superuser=False, is_staff=False, is_active=True)
        BusinessAreaFactory()
        create_defaults()

        cls.params: Parametrizer = ParametrizerFactory()
        cls.query1: Query = QueryFactory(code="result=conn.all()")
        cls.query2: Query = QueryFactory(code=f"result=invoke({cls.query1.pk}, arguments)")
        cls.formatter: Formatter = FormatterFactory(name="Queryset To HTML")
        cls.report: Report = ReportFactory(formatter=cls.formatter, query=cls.query1, last_run=None)

    def test_query_direct_task(self) -> None:
        target = self.query1.pk
        run_background_query(target)
        assert self.query1.datasets.exists()

    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_query_queue(self) -> None:
        target = self.query1.pk
        res = run_background_query.delay(target)
        assert res
        assert self.query1.datasets.exists()

    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_reports_queue(self) -> None:
        refresh_reports.delay()
        assert self.report.documents.exists()

    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_report_queue(self) -> None:
        target = self.report.pk
        refresh_report.delay(target)
        assert self.report.documents.exists()
