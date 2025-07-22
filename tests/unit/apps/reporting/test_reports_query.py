from typing import Any, List

from extras.test_utils.factories.account import PartnerFactory, UserFactory
from extras.test_utils.factories.core import create_afghanistan
from extras.test_utils.factories.reporting import ReportFactory
from parameterized import parameterized

from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.reporting.models import Report

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
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        create_afghanistan()
        cls.partner = PartnerFactory(name="Test1")
        cls.user = UserFactory.create(partner=cls.partner)
        cls.business_area = BusinessArea.objects.get(slug="afghanistan")
        cls.report_1 = ReportFactory.create(
            created_by=cls.user,
            business_area=cls.business_area,
            report_type=Report.INDIVIDUALS,
            status=Report.IN_PROGRESS,
        )
        cls.report_2 = ReportFactory.create(
            created_by=cls.user, business_area=cls.business_area, report_type=Report.PAYMENTS, status=Report.COMPLETED
        )

    @parameterized.expand(
        [
            ("all_with_permissions", [Permissions.REPORTING_EXPORT], ALL_REPORTS_QUERY),
            ("all_without_permissions", [], ALL_REPORTS_QUERY),
            ("filter_by_status_with_permissions", [Permissions.REPORTING_EXPORT], ALL_REPORTS_FILTER_STATUS_QUERY),
            ("filter_by_status_without_permissions", [], ALL_REPORTS_FILTER_STATUS_QUERY),
            ("filter_by_type_with_permissions", [Permissions.REPORTING_EXPORT], ALL_REPORTS_FILTER_TYPE_QUERY),
        ]
    )
    def test_reports_query_all(self, _: Any, permissions: List[Permissions], query_string: str) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        self.snapshot_graphql_request(
            request_string=query_string,
            context={"user": self.user},
        )

    @parameterized.expand(
        [
            ("with_permissions", [Permissions.REPORTING_EXPORT]),
            ("without_permissions", []),
        ]
    )
    def test_report_query_single(self, _: Any, permissions: List[Permissions]) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        self.snapshot_graphql_request(
            request_string=REPORT_QUERY,
            context={"user": self.user},
            variables={"id": self.id_to_base64(self.report_1.id, "ReportNode")},
        )
