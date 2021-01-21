from parameterized import parameterized
from django.core.management import call_command

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.household.fixtures import create_household_and_individuals


class TestReportingMutation(APITestCase):

    CREATE_REPORT = """
    mutation CreateReport($reportData: CreateReportInput!) {
        createReport(reportData: $reportData) {
            report {
                reportType
                dateFrom
                dateTo
                status
            }
        }
    }
    """

    def setUp(self):
        super().setUp()
        self.user = UserFactory()
        call_command("loadbusinessareas")
        self.business_area_slug = "afghanistan"
        self.business_area = BusinessArea.objects.get(slug=self.business_area_slug)
        family_sizes_list = (2, 4, 5, 1, 3, 11, 14)
        last_registration_dates = ("2020-01-01", "2021-01-01")

        self.households = []
        for index, family_size in enumerate(family_sizes_list):
            (household, individuals) = create_household_and_individuals(
                {
                    "size": family_size,
                    "address": "Lorem Ipsum",
                    "country_origin": "PL",
                    "business_area": self.business_area,
                    "last_registration_date": last_registration_dates[0] if index % 2 else last_registration_dates[1],
                },
                [{"last_registration_date": last_registration_dates[0] if index % 2 else last_registration_dates[1]}],
            )

    @parameterized.expand(
        [
            ("with_permission_individuals_report_with_earlier_dateTo", [Permissions.REPORTING_EXPORT], 1, "2020-01-02"),
            ("with_permission_individuals_report_with_later_dateTo", [Permissions.REPORTING_EXPORT], 1, "2022-01-02"),
            ("with_permission_households_report_with_earlier_dateTo", [Permissions.REPORTING_EXPORT], 2, "2020-01-02"),
            ("with_permission_households_report_with_later_dateTo", [Permissions.REPORTING_EXPORT], 2, "2022-01-02"),
            ("without_permission_individuals_report", [], 1, "2022-01-02"),
        ]
    )
    def test_create_report_with_no_extra_filters(self, _, permissions, report_type, date_to):
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)
        self.snapshot_graphql_request(
            request_string=self.CREATE_REPORT,
            context={"user": self.user},
            variables={
                "reportData": {
                    "businessAreaSlug": self.business_area_slug,
                    "reportType": report_type,
                    "dateFrom": "2019-01-01",
                    "dateTo": date_to,
                }
            },
        )
