from django.core.management import call_command
from parameterized import parameterized

from account.fixtures import UserFactory
from core.base_test_case import APITestCase
from core.models import BusinessArea
from reporting.fixtures import ReportFactory
from reporting.models import Report

ALL_REPORTS_QUERY = """
      query AllReports{
        allReports(orderBy: "status", businessArea: "afghanistan") {
          edges {
            node {
              reportType
              status
            }
          }
        }
      }
    """

ALL_REPORTS_FILTER_STATUS_QUERY = """
    query AllReports{
      allReports(status: "1",  businessArea: "afghanistan") {
        edges {
          node {
            reportType
              status
          }
        }
      }
    }
    """
ALL_REPORTS_FILTER_TYPE_QUERY = """
    query AllReports{
      allReports(reportType: "1", businessArea: "afghanistan") {
        edges {
          node {
            reportType
            status

          }
        }
      }
    }
    """
REPORT_QUERY = """
    query Report($id: ID!) {
      report(id: $id) {
        reportType
        status
      }
    }
    """


class TestReportsQuery(APITestCase):
    def setUp(self):
        super().setUp()
        call_command("loadbusinessareas")
        self.user = UserFactory.create()
        self.business_area = BusinessArea.objects.get(slug="afghanistan")
        self.report_1 = ReportFactory.create(
            created_by=self.user,
            business_area=self.business_area,
            report_type=Report.INDIVIDUALS,
            status=Report.IN_PROGRESS,
        )
        self.report_2 = ReportFactory.create(
            created_by=self.user, business_area=self.business_area, report_type=Report.PAYMENTS, status=Report.COMPLETED
        )

    @parameterized.expand(
        [
            ("all", ALL_REPORTS_QUERY),
            ("filter_by_status", ALL_REPORTS_FILTER_STATUS_QUERY),
            ("filter_by_type", ALL_REPORTS_FILTER_TYPE_QUERY),
        ]
    )
    def test_reports_query_all(self, _, query_string):

        self.snapshot_graphql_request(
            request_string=query_string,
            context={"user": self.user},
        )

    def test_report_query_single(self):

        self.snapshot_graphql_request(
            request_string=REPORT_QUERY,
            context={"user": self.user},
            variables={"id": self.id_to_base64(self.report_1.id, "ReportNode")},
        )
