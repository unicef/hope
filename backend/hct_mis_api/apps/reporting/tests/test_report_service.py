from parameterized import parameterized
from django.core.management import call_command
from django.test import TestCase

from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.reporting.fixtures import ReportFactory
from hct_mis_api.apps.reporting.models import Report
from hct_mis_api.apps.household.fixtures import create_household_and_individuals
from hct_mis_api.apps.core.fixtures import AdminAreaTypeFactory, AdminAreaFactory


class TestGenerateReportService(TestCase):
    @classmethod
    def setUpTestData(self):
        call_command("loadbusinessareas")
        from hct_mis_api.apps.reporting.generate_report_service import GenerateReportService

        self.GenerateReportService = GenerateReportService

        self.business_area = BusinessArea.objects.get(slug="afghanistan")
        self.user = UserFactory.create()
        family_sizes_list = (2, 4, 5, 1, 3, 11, 14)
        last_registration_dates = ("2020-01-01", "2021-01-01")
        area_type = AdminAreaTypeFactory(
            name="Admin type one",
            admin_level=2,
            business_area=self.business_area,
        )
        self.admin_area_1 = AdminAreaFactory(title="Adminarea Test", admin_area_type=area_type)
        self.households = []
        self.individuals = []
        for index, family_size in enumerate(family_sizes_list):
            (household, individuals) = create_household_and_individuals(
                {
                    "size": family_size,
                    "address": "Lorem Ipsum",
                    "country_origin": "PL",
                    "business_area": self.business_area,
                    "last_registration_date": last_registration_dates[0] if index % 2 else last_registration_dates[1],
                    "admin_area": None if index % 2 else self.admin_area_1,
                },
                [
                    {"last_registration_date": last_registration_dates[0] if index % 2 else last_registration_dates[1]},
                    {"last_registration_date": last_registration_dates[0] if index % 2 else last_registration_dates[1]},
                ],
            )
            self.households.append(household)
            self.individuals.extend(individuals)

    @parameterized.expand(
        [
            ("individuals_no_filter", Report.INDIVIDUALS, False, 6),
            ("individuals_filter_admin_area", Report.INDIVIDUALS, True, 8),
            ("households_no_filter", Report.HOUSEHOLD_DEMOGRAPHICS, False, 3),
            ("households_filter_admin_area", Report.HOUSEHOLD_DEMOGRAPHICS, True, 4),
        ]
    )
    def test_report_types(self, _, report_type, should_set_admin_area, number_of_records):

        report = ReportFactory.create(
            created_by=self.user,
            business_area=self.business_area,
            report_type=report_type,
            status=Report.IN_PROGRESS,
            date_from="2019-01-01",
            date_to="2020-01-02",
        )
        if should_set_admin_area:
            report.date_to = "2022-01-01"
            report.save()
            report.admin_area.set([self.admin_area_1])

        report_service = self.GenerateReportService(report)
        report_service.generate_report()
        report.refresh_from_db()
        self.assertEqual(report.status, Report.COMPLETED)
        self.assertEqual(report.number_of_records, number_of_records)
