import datetime
from freezegun import freeze_time
from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.payment.fixtures import PaymentRecordFactory, PaymentFactory
from hct_mis_api.apps.household.fixtures import create_household


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

    QUERY_DASHBOARD_YEARS_CHOICES = """
    query DashboardYearsChoiceData($businessArea: String!) {
        dashboardYearsChoices(businessAreaSlug: $businessArea)
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

    @freeze_time("2023-10-10")
    def test_dashboard_years_choices__no_objects(self):
        self.snapshot_graphql_request(
            request_string=self.QUERY_DASHBOARD_YEARS_CHOICES,
            context={"user": self.user},
            variables={"businessArea": "afghanistan"},
        )

    @freeze_time("2023-10-10")
    def test_dashboard_years_choices(self):
        create_afghanistan()
        business_area = BusinessArea.objects.get(slug="afghanistan")

        household, individuals = create_household(
            household_args={"size": 2, "business_area": business_area},
        )
        PaymentRecordFactory(
            delivery_date=datetime.date(2021, 10, 10), business_area=business_area, household=household
        )
        PaymentFactory(delivery_date=datetime.date(2020, 10, 10), business_area=business_area, household=household)

        self.snapshot_graphql_request(
            request_string=self.QUERY_DASHBOARD_YEARS_CHOICES,
            context={"user": self.user},
            variables={"businessArea": "afghanistan"},
        )
