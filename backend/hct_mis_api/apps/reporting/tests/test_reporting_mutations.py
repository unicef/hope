from datetime import date, timedelta
from typing import Any, List

from django.core.management import call_command
from django.utils import timezone

from parameterized import parameterized
from pytz import utc

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.core.utils import encode_id_base64
from hct_mis_api.apps.geo import models as geo_models
from hct_mis_api.apps.geo.fixtures import AreaFactory, AreaTypeFactory
from hct_mis_api.apps.household.fixtures import create_household_and_individuals
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.reporting.fixtures import ReportFactory
from hct_mis_api.apps.reporting.models import Report


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

    RESTART_CREATE_REPORT = """
        mutation RestartCreateReport($reportData: RestartCreateReportInput!) {
            restartCreateReport(reportData: $reportData) {
                report {
                    reportType
                    status
                }
            }
        }
        """

    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = UserFactory()
        create_afghanistan()
        call_command("loadcountries")
        cls.business_area_slug = "afghanistan"
        cls.business_area = BusinessArea.objects.get(slug=cls.business_area_slug)
        family_sizes_list = (2, 4, 5, 1, 3, 11, 14)
        last_registration_dates = (
            timezone.datetime(2020, 1, 1, tzinfo=utc),
            timezone.datetime(2021, 1, 1, tzinfo=utc),
        )

        country = geo_models.Country.objects.get(name="Afghanistan")
        area_type = AreaTypeFactory(
            name="Admin type one",
            country=country,
            area_level=2,
        )
        cls.admin_area_1 = AreaFactory(name="Adminarea Test", area_type=area_type, p_code="asdfgfhghkjltr")

        cls.program_1 = ProgramFactory(business_area=cls.business_area, end_date="2020-01-01")

        cls.households = []
        for index, family_size in enumerate(family_sizes_list):
            (household, individuals) = create_household_and_individuals(
                {
                    "size": family_size,
                    "address": "Lorem Ipsum",
                    "country_origin": geo_models.Country.objects.get(name="Poland"),
                    "business_area": cls.business_area,
                    "last_registration_date": last_registration_dates[0] if index % 2 else last_registration_dates[1],
                },
                [{"last_registration_date": last_registration_dates[0] if index % 2 else last_registration_dates[1]}],
            )
        report_updated_at = timezone.now() - timedelta(minutes=31)
        cls.report = ReportFactory(
            business_area=cls.business_area, status=Report.IN_PROGRESS, report_type=Report.INDIVIDUALS
        )
        cls.report.update_at = report_updated_at
        cls.report.save()

    @parameterized.expand(
        [
            (
                "with_permission_individuals_report_with_earlier_dateTo",
                [Permissions.REPORTING_EXPORT],
                Report.INDIVIDUALS,
                "2020-01-02",
            ),
            (
                "with_permission_individuals_report_with_later_dateTo",
                [Permissions.REPORTING_EXPORT],
                Report.INDIVIDUALS,
                "2022-01-02",
            ),
            (
                "with_permission_households_report_with_earlier_dateTo",
                [Permissions.REPORTING_EXPORT],
                Report.HOUSEHOLD_DEMOGRAPHICS,
                "2020-01-02",
            ),
            (
                "with_permission_households_report_with_later_dateTo",
                [Permissions.REPORTING_EXPORT],
                Report.HOUSEHOLD_DEMOGRAPHICS,
                "2022-01-02",
            ),
            ("without_permission_individuals_report", [], Report.INDIVIDUALS, "2022-01-02"),
        ]
    )
    def test_create_report_with_no_extra_filters(
        self, _: Any, permissions: List[Permissions], report_type: str, date_to: date
    ) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)
        self.snapshot_graphql_request(
            request_string=self.CREATE_REPORT,
            context={"user": self.user},
            variables={
                "reportData": {
                    "businessAreaSlug": self.business_area_slug,
                    "reportType": report_type,
                    "dateFrom": "2018-01-01",
                    "dateTo": date_to,
                }
            },
        )

    @parameterized.expand(
        [
            ("with_permission", [Permissions.REPORTING_EXPORT]),
            ("without_permission", []),
        ]
    )
    def test_restart_create_report(self, _: Any, permissions: List[Permissions]) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)
        self.snapshot_graphql_request(
            request_string=self.RESTART_CREATE_REPORT,
            context={"user": self.user},
            variables={
                "reportData": {
                    "businessAreaSlug": self.business_area_slug,
                    "reportId": encode_id_base64(self.report.id, "Report"),
                }
            },
        )

    def test_restart_create_report_invalid_status_update_time(self) -> None:
        self.create_user_role_with_permissions(self.user, [Permissions.REPORTING_EXPORT], self.business_area)
        self.report.status = Report.COMPLETED
        self.report.save()
        self.snapshot_graphql_request(
            request_string=self.RESTART_CREATE_REPORT,
            context={"user": self.user},
            variables={
                "reportData": {
                    "businessAreaSlug": self.business_area_slug,
                    "reportId": encode_id_base64(self.report.id, "Report"),
                }
            },
        )

        self.report.updated_at = timezone.now() - timedelta(minutes=29)
        self.report.save()
        self.snapshot_graphql_request(
            request_string=self.RESTART_CREATE_REPORT,
            context={"user": self.user},
            variables={
                "reportData": {
                    "businessAreaSlug": self.business_area_slug,
                    "reportId": encode_id_base64(self.report.id, "Report"),
                }
            },
        )
