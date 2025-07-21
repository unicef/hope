import uuid
from typing import Dict
from unittest.mock import MagicMock, patch

from django.test import TestCase

import requests

from hct_mis_api.apps.geo.models import Area
from hct_mis_api.apps.payment.models import PaymentVerification, PaymentVerificationPlan
from hct_mis_api.apps.payment.services.verification_plan_status_change_services import (
    VerificationPlanStatusChangeServices,
)
from tests.extras.test_utils.factories.account import UserFactory
from tests.extras.test_utils.factories.core import create_afghanistan
from tests.extras.test_utils.factories.household import (
    EntitlementCardFactory,
    create_household,
)
from tests.extras.test_utils.factories.payment import (
    PaymentFactory,
    PaymentPlanFactory,
    PaymentVerificationFactory,
    PaymentVerificationPlanFactory,
    PaymentVerificationSummaryFactory,
)
from tests.extras.test_utils.factories.program import ProgramFactory
from tests.extras.test_utils.factories.registration_data import (
    RegistrationDataImportFactory,
)


class TestPhoneNumberVerification(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.afghanistan = create_afghanistan()
        cls.payment_record_amount = 110
        user = UserFactory()

        program = ProgramFactory(business_area=cls.afghanistan)
        program.admin_areas.set(Area.objects.order_by("?")[:3])

        payment_plan = PaymentPlanFactory(
            program_cycle=program.cycles.first(),
            business_area=cls.afghanistan,
            created_by=user,
        )
        PaymentVerificationSummaryFactory(payment_plan=payment_plan)
        cash_plan_payment_verification = PaymentVerificationPlanFactory(
            status=PaymentVerificationPlan.STATUS_PENDING,
            verification_channel=PaymentVerificationPlan.VERIFICATION_CHANNEL_RAPIDPRO,
            payment_plan=payment_plan,
        )
        cls.individuals = []
        for i in range(cls.payment_record_amount):
            registration_data_import = RegistrationDataImportFactory(
                imported_by=user, business_area=cls.afghanistan, program=program
            )
            household, individuals = create_household(
                {
                    "registration_data_import": registration_data_import,
                    "admin_area": Area.objects.order_by("?").first(),
                    "program": program,
                },
                {
                    "registration_data_import": registration_data_import,
                    "phone_no": f"+48 609 999 {i:03d}",
                },
            )
            cls.individuals.append(individuals[0])

            payment = PaymentFactory(
                parent=payment_plan,
                household=household,
                head_of_household=household.head_of_household,
                delivered_quantity_usd=200,
                currency="PLN",
            )

            PaymentVerificationFactory(
                payment_verification_plan=cash_plan_payment_verification,
                payment=payment,
                status=PaymentVerification.STATUS_PENDING,
            )
            EntitlementCardFactory(household=household)
        cls.payment_plan = payment_plan
        cls.verification = payment_plan.payment_verification_plans.first()

        ###

        other_program = ProgramFactory(business_area=cls.afghanistan)
        other_program.admin_areas.set(Area.objects.order_by("?")[:3])

        other_payment_plan = PaymentPlanFactory(
            program_cycle=other_program.cycles.first(),
            business_area=cls.afghanistan,
            created_by=user,
        )
        PaymentVerificationSummaryFactory(payment_plan=other_payment_plan)
        other_payment_plan_payment_verification = PaymentVerificationPlanFactory(
            status=PaymentVerificationPlan.STATUS_PENDING,
            verification_channel=PaymentVerificationPlan.VERIFICATION_CHANNEL_RAPIDPRO,
            payment_plan=other_payment_plan,
        )
        cls.other_individuals = []
        for _ in range(cls.payment_record_amount):
            other_registration_data_import = RegistrationDataImportFactory(
                imported_by=user, business_area=cls.afghanistan, program=other_program
            )
            other_household, other_individuals = create_household(
                {
                    "registration_data_import": other_registration_data_import,
                    "admin_area": Area.objects.order_by("?").first(),
                    "program": other_program,
                },
                {"registration_data_import": other_registration_data_import},
            )
            cls.other_individuals.append(other_individuals[0])

            other_payment_record = PaymentFactory(
                parent=other_payment_plan,
                household=other_household,
                head_of_household=other_household.head_of_household,
                delivered_quantity_usd=200,
                currency="PLN",
            )

            PaymentVerificationFactory(
                payment_verification_plan=other_payment_plan_payment_verification,
                payment=other_payment_record,
                status=PaymentVerification.STATUS_PENDING,
            )
            EntitlementCardFactory(household=other_household)
        cls.other_payment_plan = other_payment_plan
        cls.other_verification = other_payment_plan.payment_verification_plans.first()

    def test_failing_rapid_pro_during_cash_plan_payment_verification(self) -> None:
        self.assertEqual(self.verification.status, PaymentVerification.STATUS_PENDING)
        self.assertIsNone(self.verification.error)
        self.assertEqual(self.verification.payment_record_verifications.count(), self.payment_record_amount)

        def create_flow_response() -> Dict:
            return {
                "uuid": str(uuid.uuid4()),
            }

        first_flow = create_flow_response()

        post_request_mock = MagicMock()

        post_request_mock.side_effect = [first_flow, requests.exceptions.HTTPError("TEST")]  # type: ignore
        with (
            patch("hct_mis_api.apps.core.services.rapid_pro.api.RapidProAPI.__init__", MagicMock(return_value=None)),
            patch("hct_mis_api.apps.core.services.rapid_pro.api.RapidProAPI._handle_post_request", post_request_mock),
        ):
            try:
                VerificationPlanStatusChangeServices(self.verification).activate()
            except requests.exceptions.HTTPError:
                pass
            else:
                self.fail("Should have raised HTTPError")

        self.verification.refresh_from_db()
        self.assertEqual(self.verification.status, PaymentVerificationPlan.STATUS_RAPID_PRO_ERROR)
        self.assertIsNotNone(self.verification.error)

        self.assertEqual(
            PaymentVerification.objects.filter(
                payment_verification_plan=self.verification, status=PaymentVerification.STATUS_PENDING
            ).count(),
            self.payment_record_amount,
        )
        self.assertEqual(
            PaymentVerification.objects.filter(
                payment_verification_plan=self.other_verification, status=PaymentVerification.STATUS_PENDING
            ).count(),
            self.payment_record_amount,
        )
        self.assertEqual(
            PaymentVerification.objects.filter(
                payment_verification_plan=self.verification,
                status=PaymentVerification.STATUS_PENDING,
                sent_to_rapid_pro=True,
            ).count(),
            100,
        )
        self.assertEqual(
            PaymentVerification.objects.filter(
                payment_verification_plan=self.other_verification,
                status=PaymentVerification.STATUS_PENDING,
                sent_to_rapid_pro=True,
            ).count(),
            0,
        )
        self.assertEqual(
            PaymentVerification.objects.filter(
                payment_verification_plan=self.verification,
                status=PaymentVerification.STATUS_PENDING,
                sent_to_rapid_pro=False,
            ).count(),
            10,
        )
        self.assertEqual(
            PaymentVerification.objects.filter(
                payment_verification_plan=self.other_verification,
                status=PaymentVerification.STATUS_PENDING,
                sent_to_rapid_pro=False,
            ).count(),
            self.payment_record_amount,
        )

        post_request_mock = MagicMock()
        post_request_mock.side_effect = [first_flow, create_flow_response()]
        with (
            patch("hct_mis_api.apps.core.services.rapid_pro.api.RapidProAPI.__init__", MagicMock(return_value=None)),
            patch("hct_mis_api.apps.core.services.rapid_pro.api.RapidProAPI._handle_post_request", post_request_mock),
        ):
            VerificationPlanStatusChangeServices(self.verification).activate()

        self.verification.refresh_from_db()
        self.assertEqual(self.verification.status, PaymentVerificationPlan.STATUS_ACTIVE)
        self.assertIsNone(self.verification.error)

        self.assertEqual(
            PaymentVerification.objects.filter(
                payment_verification_plan=self.verification, status=PaymentVerification.STATUS_PENDING
            ).count(),
            self.payment_record_amount,
        )
        self.assertEqual(
            PaymentVerification.objects.filter(
                payment_verification_plan=self.other_verification, status=PaymentVerification.STATUS_PENDING
            ).count(),
            self.payment_record_amount,
        )
        self.assertEqual(
            PaymentVerification.objects.filter(
                payment_verification_plan=self.verification,
                status=PaymentVerification.STATUS_PENDING,
                sent_to_rapid_pro=True,
            ).count(),
            self.payment_record_amount,
        )
        self.assertEqual(
            PaymentVerification.objects.filter(
                payment_verification_plan=self.other_verification,
                status=PaymentVerification.STATUS_PENDING,
                sent_to_rapid_pro=True,
            ).count(),
            0,
        )
        self.assertEqual(
            PaymentVerification.objects.filter(
                payment_verification_plan=self.verification,
                status=PaymentVerification.STATUS_PENDING,
                sent_to_rapid_pro=False,
            ).count(),
            0,
        )
        self.assertEqual(
            PaymentVerification.objects.filter(
                payment_verification_plan=self.other_verification,
                status=PaymentVerification.STATUS_PENDING,
                sent_to_rapid_pro=False,
            ).count(),
            self.payment_record_amount,
        )
