from datetime import timedelta
from django.utils import timezone

from parameterized import parameterized

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import (
    AdminAreaFactory,
    AdminAreaLevelFactory,
    create_afghanistan,
)
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.core.utils import encode_id_base64
from hct_mis_api.apps.geo import models as geo_models
from hct_mis_api.apps.geo.fixtures import AreaFactory, AreaTypeFactory
from hct_mis_api.apps.household.fixtures import create_household_and_individuals
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.reporting.models import Report
from hct_mis_api.apps.reporting.fixtures import ReportFactory
from hct_mis_api.apps.reporting.validators import ReportValidator


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
    def setUpTestData(cls):
        cls.user = UserFactory()
        create_afghanistan()
        cls.business_area_slug = "afghanistan"
        cls.business_area = BusinessArea.objects.get(slug=cls.business_area_slug)
        family_sizes_list = (2, 4, 5, 1, 3, 11, 14)
        last_registration_dates = ("2020-01-01", "2021-01-01")

        area_type = AdminAreaLevelFactory(
            name="Admin type one",
            admin_level=2,
            business_area=cls.business_area,
        )
        AdminAreaFactory(title="Adminarea Test", admin_area_level=area_type, p_code="asdfgfhghkjltr")

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
                    "country_origin": "PL",
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

    @parameterized.expand(
        [
            ("individuals", Report.INDIVIDUALS, "admin_area", "program"),
            ("households", Report.HOUSEHOLD_DEMOGRAPHICS, "admin_area", "program"),
            ("cash_plan_verifications", Report.CASH_PLAN_VERIFICATION, "program", "admin_area"),
            ("payments", Report.PAYMENTS, "admin_area", "program"),
            ("payment_verifications", Report.PAYMENT_VERIFICATION, "program", "admin_area"),
            ("cash_plans", Report.CASH_PLAN, "program", "admin_area"),
            ("programs", Report.PROGRAM, None, "admin_area"),
            ("programs", Report.PROGRAM, None, "program"),
            ("individuals_payments", Report.INDIVIDUALS_AND_PAYMENT, "admin_area", None),
            ("individuals_payments", Report.INDIVIDUALS_AND_PAYMENT, "program", None),
        ]
    )
    def test_create_report_validator(self, _, report_type, should_exist_field, should_not_exist_field):

        report_data = {
            "report_type": report_type,
            "business_area_slug": self.business_area_slug,
            "date_from": "2019-01-01",
            "date_to": "2021-01-01",
            "admin_area": [encode_id_base64(self.admin_area_1, "Area")],
            "program": encode_id_base64(self.program_1, "Program"),
        }
        ReportValidator.validate_report_type_filters(report_data=report_data)

        if should_exist_field:
            self.assertTrue(should_exist_field in report_data)
        if should_not_exist_field:
            self.assertFalse(should_not_exist_field in report_data)

    @parameterized.expand(
        [
            ("with_permission", [Permissions.REPORTING_EXPORT]),
            ("without_permission", []),
        ]
    )
    def test_restart_create_report(self, _, permissions):
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)
        self.snapshot_graphql_request(
            request_string=self.RESTART_CREATE_REPORT,
            context={"user": self.user},
            variables={
                "reportData": {
                    "businessAreaSlug": self.business_area_slug,
                    "reportId": encode_id_base64(self.report.id, Report),
                }
            },
        )

    def test_restart_create_report_invalid_status_update_time(self):
        self.create_user_role_with_permissions(self.user, [Permissions.REPORTING_EXPORT], self.business_area)
        self.report.status = Report.COMPLETED
        self.report.save()
        self.snapshot_graphql_request(
            request_string=self.RESTART_CREATE_REPORT,
            context={"user": self.user},
            variables={
                "reportData": {
                    "businessAreaSlug": self.business_area_slug,
                    "reportId": encode_id_base64(self.report.id, Report),
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
                    "reportId": encode_id_base64(self.report.id, Report),
                }
            },
        )
