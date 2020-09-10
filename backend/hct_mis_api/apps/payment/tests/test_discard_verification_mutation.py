import base64

from django.core.management import call_command
from django.test import TestCase

from account.fixtures import UserFactory
from core.base_test_case import APITestCase
from core.models import BusinessArea, AdminArea
from household.fixtures import (
    create_household,
    EntitlementCardFactory,
)
from payment.fixtures import (
    PaymentRecordFactory,
    CashPlanPaymentVerificationFactory,
    PaymentVerificationFactory,
)
from payment.models import PaymentVerification, CashPlanPaymentVerification
from program.fixtures import ProgramFactory, CashPlanFactory
from registration_data.fixtures import RegistrationDataImportFactory
from targeting.fixtures import TargetingCriteriaFactory, TargetPopulationFactory


class TestDiscardVerificationMutation(APITestCase):

    # verification = None

    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory.create()
        call_command("loadbusinessareas")
        payment_record_amount = 10

        user = UserFactory()

        program = ProgramFactory(business_area=BusinessArea.objects.first())
        program.admin_areas.set(AdminArea.objects.order_by("?")[:3])
        targeting_criteria = TargetingCriteriaFactory()

        target_population = TargetPopulationFactory(
            created_by=user,
            candidate_list_targeting_criteria=targeting_criteria,
            business_area=BusinessArea.objects.first(),
        )
        cash_plan = CashPlanFactory.build(program=program, business_area=BusinessArea.objects.first(),)
        cash_plan.save()
        cash_plan_payment_verification = CashPlanPaymentVerificationFactory(cash_plan=cash_plan)
        cash_plan_payment_verification.status = CashPlanPaymentVerification.STATUS_ACTIVE
        cash_plan_payment_verification.save()
        for _ in range(payment_record_amount):
            registration_data_import = RegistrationDataImportFactory(
                imported_by=user, business_area=BusinessArea.objects.first()
            )
            household, individuals = create_household(
                {
                    "registration_data_import": registration_data_import,
                    "admin_area": AdminArea.objects.order_by("?").first(),
                },
                {"registration_data_import": registration_data_import,},
            )

            household.programs.add(program)

            payment_record = PaymentRecordFactory(
                cash_plan=cash_plan, household=household, target_population=target_population,
            )

            PaymentVerificationFactory(
                cash_plan_payment_verification=cash_plan_payment_verification,
                payment_record=payment_record,
                status=PaymentVerification.STATUS_PENDING,
            )
            EntitlementCardFactory(household=household)
        cls.cash_plan = cash_plan
        cls.verification = cash_plan.verifications.first()

    def test_discard_active(self):
        encoded_id = base64.b64encode(f"CashPlanPaymentVerificationNode:{self.verification.id}".encode("ascii")).decode(
            "ascii"
        )

        DISCARD_MUTATION_GQL = f"""
        mutation DiscardVerification{{
          discardCashPlanPaymentVerification(cashPlanVerificationId:"{encoded_id}") {{
            cashPlan{{
                id
            }}
          }}
        }}
        """
        self.snapshot_graphql_request(
            request_string=DISCARD_MUTATION_GQL, context={"user": self.user},
        )
