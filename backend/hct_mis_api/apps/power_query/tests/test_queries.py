from django.db.models import QuerySet
from django.test import TestCase, override_settings

from ..apps import create_defaults
from .fixtures import FormatterFactory, QueryFactory, ReportFactory


@override_settings(POWER_QUERY_DB_ALIAS="default")
class TestPowerQuery(TestCase):
    databases = ["default"]

    @classmethod
    def setUpTestData(self):
        create_defaults()
        self.query1 = QueryFactory(code="dataset=conn.all()")
        self.query2 = QueryFactory(code=f"result, __=invoke({self.query1.pk})")
        self.formatter = FormatterFactory(name="Queryset To HTML")
        self.report = ReportFactory(formatter=self.formatter, query=self.query1)

    def test_query_execution(self):
        result, debug_info = self.query1.execute()
        self.assertIsInstance(result, QuerySet)

    def test_report_execution(self):
        result = self.report.execute(run_query=True)
        self.assertIn("<h1>Query", result)

    def test_nested_query(self):
        result, debug_info = self.query2.execute()
        self.assertIsInstance(result, QuerySet)
