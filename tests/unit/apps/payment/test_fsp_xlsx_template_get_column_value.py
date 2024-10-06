from typing import Any

from parameterized import parameterized

from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.household.fixtures import (
    DocumentFactory,
    DocumentTypeFactory,
    create_household,
)
from hct_mis_api.apps.household.models import ROLE_PRIMARY, IndividualRoleInHousehold
from hct_mis_api.apps.payment.fixtures import PaymentFactory, PaymentPlanFactory
from hct_mis_api.apps.payment.models import (
    FinancialServiceProviderXlsxTemplate,
    PaymentPlan,
)
from hct_mis_api.apps.payment.services.payment_household_snapshot_service import (
    create_payment_plan_snapshot_data,
)
from hct_mis_api.apps.program.fixtures import ProgramFactory


class FinancialServiceProviderXlsxTemplateTest(APITestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        create_afghanistan()
        cls.business_area = BusinessArea.objects.get(slug="afghanistan")
        cls.program = ProgramFactory(business_area=cls.business_area)

    def test_get_column_value_registration_token_empty(self) -> None:
        household, individuals = create_household(household_args={"size": 1, "business_area": self.business_area})
        individual = individuals[0]
        payment_plan = PaymentPlanFactory(
            program=self.program, status=PaymentPlan.Status.ACCEPTED, business_area=self.business_area
        )
        payment = PaymentFactory(parent=payment_plan, household=household, collector=individual, currency="PLN")
        create_payment_plan_snapshot_data(payment_plan)

        result = FinancialServiceProviderXlsxTemplate.get_column_value_from_payment(payment, "registration_token")
        # return empty string if no document
        self.assertEqual(result, "")

    @parameterized.expand(
        [
            ("field_payment_id", "payment_id"),
            ("field_household_id", "household_id"),
            ("field_household_size", "household_size"),
            ("field_collector_name", "collector_name"),
            ("field_currency", "currency"),
            ("field_registration_token", "registration_token"),
            ("test_wrong_column_name", "invalid_column_name"),
        ]
    )
    def test_get_column_value_from_payment(self, _: Any, field_name: str) -> None:
        household, individuals = create_household(
            household_args={"size": 1, "business_area": self.business_area},
            individual_args={"full_name": "John Wilson", "given_name": "John", "family_name": "Wilson"},
        )
        individual = individuals[0]

        payment_plan = PaymentPlanFactory(
            program=self.program, status=PaymentPlan.Status.ACCEPTED, business_area=self.business_area
        )
        payment = PaymentFactory(parent=payment_plan, household=household, collector=individual, currency="PLN")
        primary = IndividualRoleInHousehold.objects.filter(role=ROLE_PRIMARY).first().individual
        document_type = DocumentTypeFactory(key="registration_token")
        document = DocumentFactory(individual=primary, type=document_type)

        create_payment_plan_snapshot_data(payment_plan)

        result = FinancialServiceProviderXlsxTemplate.get_column_value_from_payment(payment, field_name)

        accepted_results = {
            "payment_id": payment.unicef_id,
            "household_id": household.unicef_id,
            "household_size": 1,
            "collector_name": primary.full_name,
            "currency": "PLN",
            "registration_token": document.document_number,
            "invalid_column_name": "wrong_column_name",
        }
        self.assertEqual(accepted_results.get(field_name), result)
