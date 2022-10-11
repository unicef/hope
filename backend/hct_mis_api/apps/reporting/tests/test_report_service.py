import datetime

from django.contrib.contenttypes.models import ContentType
from django.test import TestCase

from parameterized import parameterized

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.geo import models as geo_models
from hct_mis_api.apps.geo.fixtures import AreaFactory, AreaTypeFactory
from hct_mis_api.apps.household.fixtures import create_household_and_individuals
from hct_mis_api.apps.payment.fixtures import (
    PaymentRecordFactory,
    PaymentVerificationFactory,
    PaymentVerificationPlanFactory,
    CashPlanFactory,
    PaymentFactory,
    PaymentPlanFactory,
)
from hct_mis_api.apps.payment.models import PaymentVerificationSummary
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.reporting.fixtures import ReportFactory
from hct_mis_api.apps.reporting.models import Report


class TestGenerateReportService(TestCase):
    fixtures = ("hct_mis_api/apps/geo/fixtures/data.json",)

    @classmethod
    def setUpTestData(self):
        create_afghanistan()
        from hct_mis_api.apps.reporting.services.generate_report_service import (
            GenerateReportService,
        )

        self.GenerateReportService = GenerateReportService

        self.business_area = BusinessArea.objects.get(slug="afghanistan")
        self.user = UserFactory.create()
        family_sizes_list = (2, 4, 5, 1, 3, 11, 14)
        last_registration_dates = ("2020-01-01", "2021-01-01")

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
            end_date=datetime.datetime.fromisoformat('2020-01-01 00:01:11+00:00')

        )
        self.cash_plan_2 = CashPlanFactory(
            business_area=self.business_area,
            end_date=datetime.datetime.fromisoformat('2020-01-01 00:01:11+00:00')
        )
        self.payment_plan_1 = PaymentPlanFactory(
            business_area=self.business_area,
            program=self.program_1,
            end_date=datetime.datetime.fromisoformat('2020-01-01 00:01:11+00:00')

        )
        self.payment_plan_2 = PaymentPlanFactory(
            business_area=self.business_area,
            end_date=datetime.datetime.fromisoformat('2020-01-01 00:01:11+00:00')

        )
        PaymentVerificationSummary.objects.create(payment_plan=self.payment_plan_1)
        PaymentVerificationSummary.objects.create(payment_plan=self.payment_plan_2)
        ct_cash_plan = ContentType.objects.get(app_label="payment", model="cashplan")
        ct_payment_plan = ContentType.objects.get(app_label="payment", model="paymentplan")
        self.cash_plan_verification_1 = PaymentVerificationPlanFactory(
            payment_plan_object_id=self.cash_plan_1.pk,
            payment_plan_content_type=ct_cash_plan,
            completion_date="2020-01-01T14:30+00:00"
        )
        self.cash_plan_verification_2 = PaymentVerificationPlanFactory(
            payment_plan_object_id=self.cash_plan_2.pk,
            payment_plan_content_type=ct_cash_plan,
            completion_date="2020-01-01T14:30+00:00"
        )
        self.payment_plan_verification_1 = PaymentVerificationPlanFactory(
            payment_plan_object_id=self.payment_plan_1.pk,
            payment_plan_content_type=ct_payment_plan,
            completion_date="2020-01-01T14:30+00:00"
        )
        self.payment_plan_verification_2 = PaymentVerificationPlanFactory(
            payment_plan_object_id=self.payment_plan_2.pk,
            payment_plan_content_type=ct_payment_plan,
            completion_date="2020-01-01T14:30+00:00"
        )
        PaymentRecordFactory(
            household=self.households[0],
            business_area=self.business_area,
            delivery_date="2020-01-01",
            parent=self.cash_plan_1,
        )
        PaymentRecordFactory(
            household=self.households[1],
            business_area=self.business_area,
            delivery_date="2020-01-01",
            parent=self.cash_plan_2,
        )
        payment_1 = PaymentFactory(
            household=self.households[0],
            business_area=self.business_area,
            delivery_date="2020-01-01T14:30+00:00",
            parent=self.payment_plan_1,
        )
        payment_2 = PaymentFactory(
            household=self.households[1],
            business_area=self.business_area,
            delivery_date="2020-01-01T14:30+00:00",
            parent=self.payment_plan_2,
        )
        PaymentVerificationFactory(payment_verification_plan=self.cash_plan_verification_1)
        PaymentVerificationFactory(payment_verification_plan=self.cash_plan_verification_2)
        PaymentVerificationFactory(
            payment_verification_plan=self.payment_plan_verification_1,
            payment_object_id = payment_1.pk,
            payment_content_type = "",
        )
        PaymentVerificationFactory(
            payment_verification_plan=self.payment_plan_verification_2,
            payment_object_id=payment_2.pk,
            payment_content_type="",
        )

    # TODO: FIX tests
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
            ("programs_no_filter", Report.PROGRAM, False, False, 1),
            ("individuals_payments_no_filter", Report.INDIVIDUALS_AND_PAYMENT, False, False, 4),
            ("individuals_payments_admin_area", Report.INDIVIDUALS_AND_PAYMENT, True, False, 2),
            ("individuals_payments_program", Report.INDIVIDUALS_AND_PAYMENT, False, True, 2),
            ("individuals_payments_admin_area_and_program", Report.INDIVIDUALS_AND_PAYMENT, True, True, 2),
        ]
    )
    def test_report_types(self, _, report_type, should_set_admin_area, should_set_program, number_of_records):
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
        report_service.generate_report()
        report.refresh_from_db()
        self.assertEqual(report.status, Report.COMPLETED)
        self.assertEqual(report.number_of_records, number_of_records)
