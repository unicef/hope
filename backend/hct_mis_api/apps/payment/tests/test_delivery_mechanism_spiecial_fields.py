from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.utils import encode_id_base64
from hct_mis_api.apps.household.fixtures import (
    DocumentFactory,
    DocumentTypeFactory,
    HouseholdFactory,
    IndividualFactory,
    IndividualRoleInHouseholdFactory,
)
from hct_mis_api.apps.household.models import ROLE_ALTERNATE, ROLE_PRIMARY, DocumentType
from hct_mis_api.apps.payment.fixtures import (
    DeliveryMechanismPerPaymentPlanFactory,
    FinancialServiceProviderFactory,
    PaymentFactory,
    PaymentPlanFactory,
    RealProgramFactory,
)
from hct_mis_api.apps.registration_data.fixtures import RegistrationDataImportFactory
from hct_mis_api.apps.targeting.fixtures import TargetPopulationFactory

PAYMENT_QUERY = """
query Payment($id: ID!) {
  payment(id: $id) {
    deliveryMechanism {
      cardNumber
      phoneNo
      bankName
      bankAccountNumber
    }
    documents {
      documentNumber
      type {
        key
      }
    }
  }
}
"""


class TestDeliveryMechanismSpecialFields(APITestCase):
    databases = {"default", "registration_datahub"}

    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = UserFactory()
        cls.business_area = create_afghanistan()

        cls.target_population = TargetPopulationFactory()
        cls.program = RealProgramFactory(status="ACTIVE")

        cls.registration_data_import = RegistrationDataImportFactory(imported_by=cls.user)

        cls.individual_1 = IndividualFactory(household=None)
        cls.individual_2 = IndividualFactory(household=None)
        cls.individual_3 = IndividualFactory(household=None)

        cls.household_1 = HouseholdFactory(
            registration_data_import=cls.registration_data_import, head_of_household=cls.individual_1
        )
        cls.household_2 = HouseholdFactory(
            registration_data_import=cls.registration_data_import, head_of_household=cls.individual_2
        )
        cls.household_3 = HouseholdFactory(
            registration_data_import=cls.registration_data_import, head_of_household=cls.individual_3
        )

        cls.individual_1.household = cls.household_1
        cls.individual_2.household = cls.household_2
        cls.individual_3.household = cls.household_3
        cls.individual_1.save()
        cls.individual_2.save()
        cls.individual_3.save()

        IndividualRoleInHouseholdFactory(role=ROLE_PRIMARY, individual=cls.individual_1, household=cls.household_1)
        IndividualRoleInHouseholdFactory(role=ROLE_ALTERNATE, individual=cls.individual_3, household=cls.household_3)

        DocumentTypeFactory(key="national_id")
        DocumentTypeFactory(key="national_passport")
        DocumentTypeFactory(key="tax_id")

        DocumentFactory(
            document_number="111222333",
            type=DocumentType.objects.get(key="national_id"),
            individual=cls.individual_1,
        )
        DocumentFactory(
            document_number="444555666",
            type=DocumentType.objects.get(key="national_passport"),
            individual=cls.individual_2,
        )
        DocumentFactory(
            document_number="777888999",
            type=DocumentType.objects.get(key="tax_id"),
            individual=cls.individual_3,
        )

        cls.payment_plan_1 = PaymentPlanFactory(
            created_by=cls.user, target_population=cls.target_population, program=cls.program
        )
        cls.payment_plan_2 = PaymentPlanFactory(
            created_by=cls.user, target_population=cls.target_population, program=cls.program
        )
        cls.payment_plan_3 = PaymentPlanFactory(
            created_by=cls.user, target_population=cls.target_population, program=cls.program
        )

        cls.payment_1 = PaymentFactory(parent=cls.payment_plan_1, household=cls.household_1, collector=cls.individual_1)
        cls.payment_2 = PaymentFactory(parent=cls.payment_plan_2, household=cls.household_2, collector=cls.individual_2)
        cls.payment_3 = PaymentFactory(parent=cls.payment_plan_3, household=cls.household_3, collector=cls.individual_3)

        cls.financial_provider_1 = FinancialServiceProviderFactory()
        cls.financial_provider_2 = FinancialServiceProviderFactory()
        cls.financial_provider_3 = FinancialServiceProviderFactory()

        cls.delivery_mechanism_1 = DeliveryMechanismPerPaymentPlanFactory(
            payment_plan=cls.payment_plan_1,
            financial_service_provider=cls.financial_provider_1,
            card_number="1234567890",
        )
        cls.delivery_mechanism_2 = DeliveryMechanismPerPaymentPlanFactory(
            payment_plan=cls.payment_plan_2,
            financial_service_provider=cls.financial_provider_2,
            phone_no="+48654789123",
        )
        cls.delivery_mechanism_3 = DeliveryMechanismPerPaymentPlanFactory(
            payment_plan=cls.payment_plan_3,
            financial_service_provider=cls.financial_provider_3,
            bank_name="ing",
            bank_account_number="12345678900987654",
        )

    def test_delivery_mechanism_contain_card_number(self) -> None:
        self.create_user_role_with_permissions(self.user, [Permissions.PM_VIEW_DETAILS], self.business_area)

        self.snapshot_graphql_request(
            request_string=PAYMENT_QUERY,
            context={"user": self.user},
            variables={"id": encode_id_base64(self.payment_1.id, "Payment")},
        )

    def test_delivery_mechanism_contain_mobile_phone_number(self) -> None:
        self.create_user_role_with_permissions(self.user, [Permissions.PM_VIEW_DETAILS], self.business_area)

        self.snapshot_graphql_request(
            request_string=PAYMENT_QUERY,
            context={"user": self.user},
            variables={"id": encode_id_base64(self.payment_2.id, "Payment")},
        )

    def test_delivery_mechanism_contain_bank_data(self) -> None:
        self.create_user_role_with_permissions(self.user, [Permissions.PM_VIEW_DETAILS], self.business_area)

        self.snapshot_graphql_request(
            request_string=PAYMENT_QUERY,
            context={"user": self.user},
            variables={"id": encode_id_base64(self.payment_3.id, "Payment")},
        )
