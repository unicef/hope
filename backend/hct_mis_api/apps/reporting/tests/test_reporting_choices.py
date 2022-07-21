from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.core.base_test_case import APITestCase


class TestProgramChoices(APITestCase):

    QUERY_REPORT_STATUS_CHOICES = """
    query ReportStatusChoices {
        reportStatusChoices{
            name
            value
        }
    }
    """

    QUERY_REPORT_TYPES_CHOICES = """
    query ReportTypesChoices {
        reportTypesChoices{
            name
            value
        }
    }
    """

    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory()

    def test_status_choices_query(self):
        self.snapshot_graphql_request(
            request_string=self.QUERY_REPORT_STATUS_CHOICES,
            context={"user": self.user},
        )

    def test_report_types_choices(self):
        self.snapshot_graphql_request(
            request_string=self.QUERY_REPORT_TYPES_CHOICES,
            context={"user": self.user},
        )
