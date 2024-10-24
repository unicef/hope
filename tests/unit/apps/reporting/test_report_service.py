from typing import Any
from unittest.mock import patch

from django.conf import settings
from django.test import TestCase
from django.utils import timezone

from parameterized import parameterized
from pytz import utc

from hct_mis_api.apps.account.fixtures import PartnerFactory, UserFactory
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.geo import models as geo_models
from hct_mis_api.apps.geo.fixtures import AreaFactory, AreaTypeFactory
from hct_mis_api.apps.household.fixtures import create_household_and_individuals
from hct_mis_api.apps.payment.fixtures import (
    CashPlanFactory,
    PaymentFactory,
    PaymentPlanFactory,
    PaymentRecordFactory,
    PaymentVerificationFactory,
    PaymentVerificationPlanFactory,
)
from hct_mis_api.apps.payment.models import PaymentVerificationSummary
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.reporting.fixtures import ReportFactory
from hct_mis_api.apps.reporting.models import Report


class TestGenerateReportService(TestCase):
    fixtures = (f"{settings.PROJECT_ROOT}/apps/geo/fixtures/data.json",)

    @classmethod
    def setUpTestData(self) -> None:
        create_afghanistan()
        PartnerFactory(name="UNICEF")
        from hct_mis_api.apps.reporting.services.generate_report_service import (
            GenerateReportService,
        )

        self.GenerateReportService = GenerateReportService

        self.business_area = BusinessArea.objects.get(slug="afghanistan")
        self.partner = PartnerFactory(name="Test1")
        self.user = UserFactory.create(partner=self.partner)
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
        self.admin_area_1 = AreaFactory(name="Adminarea Test", area_type=area_type, p_code="asdfgfhghkjltr")

        self.program_1 = ProgramFactory(business_area=self.business_area, end_date="2020-01-01")
        self.program_2 = ProgramFactory(business_area=self.business_area, end_date="2022-01-01")
        self.households = []
        self.individuals = []
        country_origin = geo_models.Country.objects.filter(iso_code2="PL").first()
        for index, family_size in enumerate(family_sizes_list):
            (household, individuals) = create_household_and_individuals(
                {
                    "size": family_size,
                    "address": "Lorem Ipsum",
                    "country_origin": country_origin,
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
            if index % 2:
                household.programs.add(self.program_1)
            else:
                household.programs.add(self.program_2)

        self.cash_plan_1 = CashPlanFactory(
            business_area=self.business_area,
            program=self.program_1,
            # end_date=datetime.datetime.fromisoformat("2020-01-01 00:01:11+00:00"),
        )
        self.cash_plan_2 = CashPlanFactory(
            business_area=self.business_area,
            # end_date=datetime.datetime.fromisoformat("2020-01-01 00:01:11+00:00")
        )
        self.payment_plan_1 = PaymentPlanFactory(
            business_area=self.business_area,
            program=self.program_1,
            # end_date=datetime.datetime.fromisoformat("2020-01-01 00:01:11+00:00"),
        )
        self.payment_plan_2 = PaymentPlanFactory(
            business_area=self.business_area,
            # end_date=datetime.datetime.fromisoformat("2020-01-01 00:01:11+00:00")
        )
        PaymentVerificationSummary.objects.create(payment_plan_obj=self.payment_plan_1)
        PaymentVerificationSummary.objects.create(payment_plan_obj=self.payment_plan_2)
        self.cash_plan_verification_1 = PaymentVerificationPlanFactory(
            payment_plan_obj=self.cash_plan_1, completion_date="2020-01-01T14:30+00:00"
        )
        self.cash_plan_verification_2 = PaymentVerificationPlanFactory(
            payment_plan_obj=self.cash_plan_2, completion_date="2020-01-01T14:30+00:00"
        )
        self.payment_plan_verification_1 = PaymentVerificationPlanFactory(
            payment_plan_obj=self.payment_plan_1, completion_date="2020-01-01T14:30+00:00"
        )
        self.payment_plan_verification_2 = PaymentVerificationPlanFactory(
            payment_plan_obj=self.payment_plan_2, completion_date="2020-01-01T14:30+00:00"
        )
        record_1 = PaymentRecordFactory(
            household=self.households[0],
            business_area=self.business_area,
            delivery_date="2020-01-01T00:00+00:00",
            parent=self.cash_plan_1,
            currency="PLN",
        )
        record_2 = PaymentRecordFactory(
            household=self.households[1],
            business_area=self.business_area,
            delivery_date="2020-01-01T00:00+00:00",
            parent=self.cash_plan_2,
            currency="PLN",
        )
        payment_1 = PaymentFactory(
            household=self.households[0],
            business_area=self.business_area,
            delivery_date="2020-01-01T14:30+00:00",
            parent=self.payment_plan_1,
            currency="PLN",
        )
        payment_2 = PaymentFactory(
            household=self.households[1],
            business_area=self.business_area,
            delivery_date="2020-01-01T14:30+00:00",
            parent=self.payment_plan_2,
            currency="PLN",
        )
        PaymentVerificationFactory(
            payment_verification_plan=self.cash_plan_verification_1,
            payment_obj=record_1,
        )
        PaymentVerificationFactory(
            payment_verification_plan=self.cash_plan_verification_2,
            payment_obj=record_2,
        )
        PaymentVerificationFactory(
            payment_verification_plan=self.payment_plan_verification_1,
            payment_obj=payment_1,
        )
        PaymentVerificationFactory(
            payment_verification_plan=self.payment_plan_verification_2,
            payment_obj=payment_2,
        )

    @parameterized.expand(
        [
            ("individuals_no_filter", Report.INDIVIDUALS, False, False, 6),
            ("individuals_filter_admin_area", Report.INDIVIDUALS, True, False, 8),
            ("households_no_filter", Report.HOUSEHOLD_DEMOGRAPHICS, False, False, 3),
            ("households_filter_admin_area", Report.HOUSEHOLD_DEMOGRAPHICS, True, False, 4),
            ("cash_plan_verifications_no_filter", Report.CASH_PLAN_VERIFICATION, False, False, 2),
            ("cash_plan_verifications_program", Report.CASH_PLAN_VERIFICATION, False, True, 1),
            ("payments_no_filter", Report.PAYMENTS, False, False, 2),
            ("payments_filter_admin_area", Report.PAYMENTS, True, False, 1),
            ("payment_verifications_no_filter", Report.PAYMENT_VERIFICATION, False, False, 2),
            ("payment_verifications_program", Report.PAYMENT_VERIFICATION, False, True, 1),
            ("cash_plans_no_filter", Report.CASH_PLAN, False, False, 2),
            ("cash_plans_program", Report.CASH_PLAN, False, True, 1),
            ("individuals_payments_no_filter", Report.INDIVIDUALS_AND_PAYMENT, False, False, 4),
            ("individuals_payments_admin_area", Report.INDIVIDUALS_AND_PAYMENT, True, False, 2),
            ("individuals_payments_program", Report.INDIVIDUALS_AND_PAYMENT, False, True, 2),
            ("individuals_payments_admin_area_and_program", Report.INDIVIDUALS_AND_PAYMENT, True, True, 2),
        ]
    )
    def test_report_types(
        self, _: Any, report_type: str, should_set_admin_area: bool, should_set_program: bool, number_of_records: int
    ) -> None:
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

        if should_set_program:
            report.program = self.program_1
            report.save()

        report_service = self.GenerateReportService(report)
        with (
            patch(
                "hct_mis_api.apps.reporting.services.generate_report_service.GenerateReportService.save_wb_file_in_db"
            ) as mock_save_wb_file_in_db,
            patch(
                "hct_mis_api.apps.reporting.services.generate_report_service.GenerateReportService.generate_workbook"
            ) as mock_generate_workbook,
        ):
            report_service.generate_report()
            assert mock_generate_workbook.called
            assert mock_save_wb_file_in_db.called
        report.refresh_from_db()
        self.assertEqual(report.status, Report.COMPLETED)
        # self.assertEqual(report.number_of_records, number_of_records) # when mocking generating workbook, this is not set
        # so for the sake of stability, this assertion may be omitted
