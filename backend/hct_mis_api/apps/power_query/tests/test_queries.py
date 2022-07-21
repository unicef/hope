from django.db.models import QuerySet
from django.test import TestCase, override_settings

from ..apps import create_defaults
from .fixtures import FormatterFactory, QueryFactory, ReportFactory


@override_settings(POWER_QUERY_DB_ALIAS="default")
class TestPowerQuery(TestCase):
    databases = ["default"]

    @classmethod
    def setUpTestData(cls):
        create_defaults()
        cls.query1 = QueryFactory(code="result=conn.all()")
        cls.query2 = QueryFactory(code=f"result, __=invoke({cls.query1.pk})")
        cls.formatter = FormatterFactory(name="Queryset To HTML")
        cls.report = ReportFactory(formatter=cls.formatter, query=cls.query1)

    def test_query_execution(self):
        result, debug_info = self.query1.execute()
        self.assertIsInstance(result, QuerySet)

    def test_report_execution(self):
        result = self.report.execute(run_query=True)
        self.assertIn("<h1>Query", result)

    def test_nested_query(self):
        result, debug_info = self.query2.execute()
        self.assertIsInstance(result, QuerySet)
