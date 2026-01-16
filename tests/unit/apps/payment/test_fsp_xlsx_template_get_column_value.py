from parameterized import parameterized

from extras.test_utils.factories.account import UserFactory
from extras.test_utils.factories.core import create_afghanistan
from extras.test_utils.factories.household import (
    DocumentFactory,
    DocumentTypeFactory,
    create_household,
)
from extras.test_utils.factories.payment import (
    FinancialServiceProviderFactory,
    PaymentFactory,
    PaymentPlanFactory,
    generate_delivery_mechanisms,
)
from extras.test_utils.factories.program import ProgramFactory
from hope.apps.core.base_test_case import BaseTestCase
from hope.apps.household.const import ROLE_PRIMARY
from hope.apps.payment.services.payment_household_snapshot_service import (
    create_payment_plan_snapshot_data,
)
from hope.models import (
    DeliveryMechanism,
    FinancialServiceProvider,
    FinancialServiceProviderXlsxTemplate,
    IndividualRoleInHousehold,
    Payment,
    PaymentPlan,
)


class FinancialServiceProviderXlsxTemplateTest(BaseTestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.business_area = create_afghanistan()
        cls.program = ProgramFactory(business_area=cls.business_area)
        cls.user = UserFactory()
        generate_delivery_mechanisms()
        cls.dm_cash = DeliveryMechanism.objects.get(code="cash")
        cls.fsp = FinancialServiceProviderFactory(
            name="Test FSP 1",
            communication_channel=FinancialServiceProvider.COMMUNICATION_CHANNEL_XLSX,
            vision_vendor_number=123456789,
        )
        cls.admin_areas_dict = FinancialServiceProviderXlsxTemplate.get_areas_dict()

    def test_get_column_value_registration_token_empty(self) -> None:
        household, individuals = create_household(household_args={"size": 1, "business_area": self.business_area})
        individual = individuals[0]
        payment_plan = PaymentPlanFactory(
            program_cycle=self.program.cycles.first(),
            status=PaymentPlan.Status.ACCEPTED,
            business_area=self.business_area,
            created_by=self.user,
        )
        DocumentTypeFactory(key="registration_token")
        payment = PaymentFactory(
            parent=payment_plan,
            household=household,
            collector=individual,
            currency="PLN",
            financial_service_provider=self.fsp,
            delivery_type=self.dm_cash,
        )
        create_payment_plan_snapshot_data(payment_plan)
        payment.refresh_from_db()

        result = FinancialServiceProviderXlsxTemplate.get_column_value_from_payment(
            payment, "registration_token", self.admin_areas_dict
        )
        # return empty string if no document
        assert result == ""

    @parameterized.expand(
        [
            ("field_payment_id", "payment_id", Payment.STATUS_PENDING),
            ("field_household_id", "household_id", Payment.STATUS_PENDING),
            ("field_household_size", "household_size", Payment.STATUS_PENDING),
            ("field_collector_name", "collector_name", Payment.STATUS_PENDING),
            ("field_currency", "currency", Payment.STATUS_PENDING),
            ("field_registration_token", "registration_token", Payment.STATUS_PENDING),
            ("test_wrong_column_name", "invalid_column_name", Payment.STATUS_PENDING),
            ("field_delivered_quantity", "delivered_quantity", Payment.STATUS_PENDING),
            ("field_delivered_quantity_error", "delivered_quantity", Payment.STATUS_ERROR),
        ]
    )
    def test_get_column_value_from_payment(self, helper: str, field_name: str, payment_status: str) -> None:
        household, individuals = create_household(
            household_args={"size": 1, "business_area": self.business_area},
            individual_args={
                "full_name": "John Wilson",
                "given_name": "John",
                "family_name": "Wilson",
            },
        )
        individual = individuals[0]

        payment_plan = PaymentPlanFactory(
            program_cycle=self.program.cycles.first(),
            status=PaymentPlan.Status.ACCEPTED,
            business_area=self.business_area,
            created_by=self.user,
        )
        payment = PaymentFactory(
            parent=payment_plan,
            household=household,
            collector=individual,
            currency="PLN",
            financial_service_provider=self.fsp,
            delivery_type=self.dm_cash,
            status=payment_status,
        )
        primary = IndividualRoleInHousehold.objects.filter(role=ROLE_PRIMARY).first().individual
        document_type = DocumentTypeFactory(key="registration_token")
        document = DocumentFactory(individual=primary, type=document_type)

        create_payment_plan_snapshot_data(payment_plan)
        payment.refresh_from_db()

        result = FinancialServiceProviderXlsxTemplate.get_column_value_from_payment(
            payment, field_name, self.admin_areas_dict
        )

        accepted_results = {
            "field_payment_id": payment.unicef_id,
            "field_household_id": household.unicef_id,
            "field_household_size": 1,
            "field_collector_name": primary.full_name,
            "field_currency": "PLN",
            "field_registration_token": document.document_number,
            "test_wrong_column_name": "wrong_column_name",
            "field_delivered_quantity": payment.delivered_quantity,
            "field_delivered_quantity_error": float(-1),
        }
        assert accepted_results.get(helper) == result
