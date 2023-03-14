from django.utils import timezone

from freezegun import freeze_time
from pytz import utc

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.household.fixtures import create_household
from hct_mis_api.apps.payment.fixtures import PaymentFactory, PaymentRecordFactory


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
    def setUpTestData(cls) -> None:
        cls.user = UserFactory()

    def test_status_choices_query(self) -> None:
        self.snapshot_graphql_request(
            request_string=self.QUERY_REPORT_STATUS_CHOICES,
            context={"user": self.user},
        )

    def test_report_types_choices(self) -> None:
        self.snapshot_graphql_request(
            request_string=self.QUERY_REPORT_TYPES_CHOICES,
            context={"user": self.user},
        )

    @freeze_time("2023-10-10")
    def test_dashboard_years_choices__no_objects(self) -> None:
        self.snapshot_graphql_request(
            request_string=self.QUERY_DASHBOARD_YEARS_CHOICES,
            context={"user": self.user},
            variables={"businessArea": "afghanistan"},
        )

    @freeze_time("2023-10-10")
    def test_dashboard_years_choices(self) -> None:
        create_afghanistan()
        business_area = BusinessArea.objects.get(slug="afghanistan")

        household, individuals = create_household(
            household_args={"size": 2, "business_area": business_area},
        )
        PaymentRecordFactory(
            delivery_date=timezone.datetime(2021, 10, 10, tzinfo=utc), business_area=business_area, household=household
        )
        PaymentFactory(
            delivery_date=timezone.datetime(2020, 10, 10, tzinfo=utc), business_area=business_area, household=household
        )

        self.snapshot_graphql_request(
            request_string=self.QUERY_DASHBOARD_YEARS_CHOICES,
            context={"user": self.user},
            variables={"businessArea": "afghanistan"},
        )
