from hct_mis_api.apps.account.fixtures import BusinessAreaFactory, UserFactory
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.hope_redirect import HopeRedirect, get_hope_redirect
from hct_mis_api.apps.household.fixtures import create_household_and_individuals
from hct_mis_api.apps.payment.fixtures import (
    PaymentVerificationPlanFactory,
    PaymentRecordFactory,
    PaymentVerificationFactory,
)
from hct_mis_api.apps.payment.models import (
    PaymentVerificationPlan,
    PaymentVerification,
)
from hct_mis_api.apps.payment.fixtures import CashPlanFactory
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.targeting.fixtures import (
    TargetingCriteriaFactory,
    TargetPopulationFactory,
)


class TestHopeRedirect(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory.create()
        business_area = BusinessAreaFactory(
            code="0060",
            name="Afghanistan",
            long_name="THE ISLAMIC REPUBLIC OF AFGHANISTAN",
            region_code="64",
            region_name="SAR",
            slug="afghanistan",
            has_data_sharing_agreement=True,
        )
        program = ProgramFactory(id="e6537f1e-27b5-4179-a443-d42498fb0478")
        CashPlanFactory(
            id="0272dd2d-c41e-435d-9587-6ba280678c54",
            ca_id="B4M-21-CSH-00004",
            business_area=business_area,
            program=program,
        )

        household, _ = create_household_and_individuals(
            {
                "id": "01780fad-9fa9-4e27-b3cd-7187c13452e5",
                "unicef_id": "HH-21-0000.8129",
                "business_area": business_area,
            },
            [
                {
                    "full_name": "Jenna Franklin",
                    "given_name": "Jenna",
                    "family_name": "Franklin",
                    "phone_no": "001-296-358-5428-607",
                    "birth_date": "1969-11-29",
                    "id": "001A2C2D-22CA-4538-A36F-D454AF5EDD3E",
                    "unicef_id": "IND-21-0002.2658",
                },
            ],
        )

        cash_plan = CashPlanFactory(
            name="TEST",
            program=program,
            business_area=business_area,
        )
        payment_verification_plan = PaymentVerificationPlanFactory(
            cash_plan=cash_plan, status=PaymentVerificationPlan.STATUS_ACTIVE
        )

        target_population = TargetPopulationFactory(
            id="6FFB6BB7-3D43-4ECE-BB0E-21FDE209AFAF",
            created_by=cls.user,
            targeting_criteria=(TargetingCriteriaFactory()),
            business_area=business_area,
        )
        payment_record = PaymentRecordFactory(
            parent=cash_plan,
            household=household,
            target_population=target_population,
            ca_id="P8F-21-CSH-00031-0000006",
        )
        PaymentVerificationFactory(
            id="a76bfe6f-c767-4b7f-9671-6df10b8095cc",
            payment_verification_plan=payment_verification_plan,
            payment=payment_record,
            status=PaymentVerification.STATUS_PENDING,
        )

        cls.create_user_role_with_permissions(cls.user, [], business_area)

    def test_redirect_to_household_list(self):
        hope_redirect: HopeRedirect = get_hope_redirect(self.user, "progres_registrationgroup")

        expected_url = "/afghanistan/population/household"
        self.assertEqual(expected_url, hope_redirect.url())

    def test_redirect_to_household_details(self):
        hope_redirect: HopeRedirect = get_hope_redirect(
            self.user,
            "progres_registrationgroup",
            "HH-21-0000.8129",
            "01780fad-9fa9-4e27-b3cd-7187c13452e5",
        )

        expected_url = (
            "/afghanistan/population/household/SG91c2Vob2xkTm9kZTowMTc4MGZhZC05ZmE5LTRlMjctYjNjZC03MTg3YzEzNDUyZTU="
        )
        self.assertEqual(expected_url, hope_redirect.url())

    def test_redirect_to_individual_list(self):
        hope_redirect: HopeRedirect = get_hope_redirect(self.user, "progres_individual")

        expected_url = "/afghanistan/population/individuals"
        self.assertEqual(expected_url, hope_redirect.url())

    def test_redirect_to_individual_details(self):
        hope_redirect: HopeRedirect = get_hope_redirect(
            self.user,
            "progres_individual",
            "IND-21-0002.2658",
            "001A2C2D-22CA-4538-A36F-D454AF5EDD3E",
        )

        expected_url = (
            "/afghanistan/population/individuals/SW5kaXZpZHVhbE5vZGU6MDAxYTJjMmQtMjJjYS00NTM4LWEzNmYtZDQ1NGFmNWVkZDNl"
        )
        self.assertEqual(expected_url, hope_redirect.url())

    def test_redirect_to_program_list(self):
        hope_redirect: HopeRedirect = get_hope_redirect(self.user, "progres_program")

        expected_url = "/afghanistan/programs"
        self.assertEqual(expected_url, hope_redirect.url())

    def test_redirect_to_program_details(self):
        hope_redirect: HopeRedirect = get_hope_redirect(
            self.user,
            "progres_program",
            "e6537f1e-27b5-4179-a443-d42498fb0478",
            "e6537f1e-27b5-4179-a443-d42498fb0478",
        )

        expected_url = "/afghanistan/programs/UHJvZ3JhbU5vZGU6ZTY1MzdmMWUtMjdiNS00MTc5LWE0NDMtZDQyNDk4ZmIwNDc4"
        self.assertEqual(expected_url, hope_redirect.url())

    def test_redirect_to_cash_plan_list(self):
        hope_redirect: HopeRedirect = get_hope_redirect(self.user, "progres_cashplan")

        expected_url = "/afghanistan/payment-verification"
        self.assertEqual(expected_url, hope_redirect.url())

    def test_redirect_to_cash_plan_details(self):
        hope_redirect: HopeRedirect = get_hope_redirect(
            self.user,
            "progres_cashplan",
            "B4M-21-CSH-00004",
            "",
            "e6537f1e-27b5-4179-a443-d42498fb0478",
        )

        expected_url = "/afghanistan/cashplans/Q2FzaFBsYW5Ob2RlOjAyNzJkZDJkLWM0MWUtNDM1ZC05NTg3LTZiYTI4MDY3OGM1NA=="
        self.assertEqual(expected_url, hope_redirect.url())

    def test_redirect_to_payment_list(self):
        hope_redirect: HopeRedirect = get_hope_redirect(self.user, "progres_payment")

        expected_url = "/afghanistan/payment-verification"
        self.assertEqual(expected_url, hope_redirect.url())

    def test_redirect_to_payment_details(self):
        hope_redirect: HopeRedirect = get_hope_redirect(
            self.user,
            "progres_payment",
            "P8F-21-CSH-00031-0000006",
            "",
            "d442576f-2664-430d-81f9-38a1be362053",
        )

        expected_url = "/afghanistan/verification-records/UGF5bWVudFZlcmlmaWNhdGlvbk5vZGU6YTc2YmZlNmYtYzc2Ny00YjdmLTk2NzEtNmRmMTBiODA5NWNj"
        self.assertEqual(expected_url, hope_redirect.url())

    def test_redirect_to_target_population_list(self):
        hope_redirect: HopeRedirect = get_hope_redirect(self.user, "progres_targetpopulation")

        expected_url = "/afghanistan/target-population"
        self.assertEqual(expected_url, hope_redirect.url())

    def test_redirect_to_target_population_details(self):
        hope_redirect: HopeRedirect = get_hope_redirect(
            self.user,
            "progres_targetpopulation",
            "Brazil%20Demo-CAR",
            "6FFB6BB7-3D43-4ECE-BB0E-21FDE209AFAF",
        )

        expected_url = "/afghanistan/target-population/VGFyZ2V0UG9wdWxhdGlvbk5vZGU6NmZmYjZiYjctM2Q0My00ZWNlLWJiMGUtMjFmZGUyMDlhZmFm"
        self.assertEqual(expected_url, hope_redirect.url())
