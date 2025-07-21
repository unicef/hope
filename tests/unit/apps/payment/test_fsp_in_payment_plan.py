from typing import Any

from tests.extras.test_utils.factories.account import UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from tests.extras.test_utils.factories.core import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.core.utils import encode_id_base64
from tests.extras.test_utils.factories.household import (
    IndividualRoleInHouseholdFactory,
    create_household_and_individuals,
)
from hct_mis_api.apps.household.models import ROLE_PRIMARY
from hct_mis_api.apps.payment.delivery_mechanisms import DeliveryMechanismChoices
from tests.extras.test_utils.factories.payment import (
    FinancialServiceProviderFactory,
    FspXlsxTemplatePerDeliveryMechanismFactory,
    PaymentFactory,
    PaymentPlanFactory,
    generate_delivery_mechanisms,
)
from hct_mis_api.apps.payment.models import DeliveryMechanism, Payment, PaymentPlan
from tests.extras.test_utils.factories.program import ProgramFactory
from tests.extras.test_utils.factories.registration_data import RegistrationDataImportFactory


def base_setup(cls: Any) -> None:
    create_afghanistan()
    cls.business_area = BusinessArea.objects.get(slug="afghanistan")
    cls.program = ProgramFactory(business_area=cls.business_area)
    cls.user = UserFactory.create()
    cls.create_user_role_with_permissions(
        cls.user,
        [Permissions.PM_CREATE, Permissions.PM_VIEW_DETAILS],
        BusinessArea.objects.get(slug="afghanistan"),
    )

    cls.registration_data_import = RegistrationDataImportFactory(business_area=cls.business_area)

    cls.household_1, cls.individuals_1 = create_household_and_individuals(
        household_data={
            "registration_data_import": cls.registration_data_import,
            "business_area": cls.business_area,
            "program": cls.program,
        },
        individuals_data=[{}],
    )
    IndividualRoleInHouseholdFactory(
        individual=cls.individuals_1[0],
        household=cls.household_1,
        role=ROLE_PRIMARY,
    )

    cls.household_2, cls.individuals_2 = create_household_and_individuals(
        household_data={
            "registration_data_import": cls.registration_data_import,
            "business_area": cls.business_area,
            "program": cls.program,
        },
        individuals_data=[{}],
    )
    IndividualRoleInHouseholdFactory(
        individual=cls.individuals_2[0],
        household=cls.household_2,
        role=ROLE_PRIMARY,
    )

    cls.household_3, cls.individuals_3 = create_household_and_individuals(
        household_data={
            "registration_data_import": cls.registration_data_import,
            "business_area": cls.business_area,
            "program": cls.program,
        },
        individuals_data=[{}],
    )
    IndividualRoleInHouseholdFactory(
        individual=cls.individuals_3[0],
        household=cls.household_3,
        role=ROLE_PRIMARY,
    )
    cls.context = {
        "user": cls.user,
        "headers": {
            "Business-Area": cls.business_area.slug,
            "Program": encode_id_base64(cls.program.id, "Program"),
        },
    }
    generate_delivery_mechanisms()
    cls.dm_cash = DeliveryMechanism.objects.get(code="cash")
    cls.dm_transfer = DeliveryMechanism.objects.get(code="transfer")
    cls.dm_transfer_to_digital_wallet = DeliveryMechanism.objects.get(code="transfer_to_digital_wallet")
    cls.dm_voucher = DeliveryMechanism.objects.get(code="voucher")
    cls.dm_mobile_money = DeliveryMechanism.objects.get(code="mobile_money")


def payment_plan_setup(cls: Any) -> None:
    cls.santander_fsp = FinancialServiceProviderFactory(
        name="Santander",
        distribution_limit=None,
        data_transfer_configuration=[
            {"key": "config_1", "label": "Config 1", "id": "1"},
            {"key": "config_11", "label": "Config 11", "id": "11"},
        ],
    )

    cls.santander_fsp.delivery_mechanisms.set([cls.dm_transfer, cls.dm_cash, cls.dm_transfer_to_digital_wallet])
    cls.santander_fsp.allowed_business_areas.add(cls.business_area)
    cls.encoded_santander_fsp_id = encode_id_base64(cls.santander_fsp.id, "FinancialServiceProvider")

    cls.payment_plan = PaymentPlanFactory(
        total_households_count=4,
        status=PaymentPlan.Status.LOCKED,
        program_cycle=cls.program.cycles.first(),
        created_by=cls.user,
        delivery_mechanism=cls.dm_transfer,
        financial_service_provider=cls.santander_fsp,
    )

    cls.encoded_payment_plan_id = encode_id_base64(cls.payment_plan.id, "PaymentPlan")

    cls.bank_of_america_fsp = FinancialServiceProviderFactory(
        name="Bank of America",
        distribution_limit=1000,
        data_transfer_configuration=[{"key": "config_2", "label": "Config 2", "id": "2"}],
    )
    cls.bank_of_america_fsp.delivery_mechanisms.set([cls.dm_voucher, cls.dm_cash, cls.dm_transfer_to_digital_wallet])
    cls.bank_of_america_fsp.allowed_business_areas.add(cls.business_area)
    cls.encoded_bank_of_america_fsp_id = encode_id_base64(cls.bank_of_america_fsp.id, "FinancialServiceProvider")

    cls.bank_of_europe_fsp = FinancialServiceProviderFactory(
        name="Bank of Europe",
        distribution_limit=50000,
        data_transfer_configuration=[{"key": "config_3", "label": "Config 3", "id": "3"}],
    )
    cls.bank_of_europe_fsp.delivery_mechanisms.set([cls.dm_voucher, cls.dm_transfer, cls.dm_cash])
    cls.bank_of_europe_fsp.allowed_business_areas.add(cls.business_area)
    cls.encoded_bank_of_europe_fsp_id = encode_id_base64(cls.bank_of_europe_fsp.id, "FinancialServiceProvider")

    FspXlsxTemplatePerDeliveryMechanismFactory(
        financial_service_provider=cls.santander_fsp, delivery_mechanism=cls.dm_transfer
    )
    FspXlsxTemplatePerDeliveryMechanismFactory(
        financial_service_provider=cls.santander_fsp, delivery_mechanism=cls.dm_voucher
    )
    FspXlsxTemplatePerDeliveryMechanismFactory(
        financial_service_provider=cls.bank_of_europe_fsp,
        delivery_mechanism=cls.dm_transfer,
    )
    FspXlsxTemplatePerDeliveryMechanismFactory(
        financial_service_provider=cls.bank_of_europe_fsp,
        delivery_mechanism=cls.dm_voucher,
    )
    FspXlsxTemplatePerDeliveryMechanismFactory(
        financial_service_provider=cls.bank_of_america_fsp,
        delivery_mechanism=cls.dm_voucher,
    )


CURRENT_PAYMENT_PLAN_QUERY = """
query PaymentPlan($id: ID!) {
    paymentPlan(id: $id) {
        id
        deliveryMechanisms {
            name
            fsp {
                id
            }
        }
    }
}
"""


class TestVolumeByDeliveryMechanism(APITestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        base_setup(cls)
        payment_plan_setup(cls)

    def test_getting_volume_by_delivery_mechanism(self) -> None:
        GET_VOLUME_BY_DELIVERY_MECHANISM_QUERY = """
            query PaymentPlan($paymentPlanId: ID!) {
                paymentPlan(id: $paymentPlanId) {
                    volumeByDeliveryMechanism {
                        deliveryMechanism {
                            name
                            fsp {
                                id
                            }
                        }
                        volume
                        volumeUsd
                    }
                }
            }
        """
        get_volume_by_delivery_mechanism_response = self.graphql_request(
            request_string=GET_VOLUME_BY_DELIVERY_MECHANISM_QUERY,
            context=self.context,
            variables={
                "paymentPlanId": self.encoded_payment_plan_id,
            },
        )
        assert "errors" not in get_volume_by_delivery_mechanism_response, get_volume_by_delivery_mechanism_response

        data = get_volume_by_delivery_mechanism_response["data"]["paymentPlan"]["volumeByDeliveryMechanism"]
        assert len(data) == 1
        assert data[0]["deliveryMechanism"]["name"] == DeliveryMechanismChoices.DELIVERY_TYPE_TRANSFER
        assert data[0]["deliveryMechanism"]["fsp"]["id"] == self.encoded_santander_fsp_id
        assert data[0]["volume"] == 0
        assert data[0]["volumeUsd"] == 0

        # Simulate applying steficon formula
        payment_1 = PaymentFactory(
            parent=self.payment_plan,
            financial_service_provider=self.santander_fsp,
            collector=self.individuals_2[0],
            entitlement_quantity=500,
            entitlement_quantity_usd=100,
            delivery_type=self.dm_transfer,
            status=Payment.STATUS_NOT_DISTRIBUTED,
            household=self.household_2,
            currency="PLN",
        )
        payment_2 = PaymentFactory(
            parent=self.payment_plan,
            financial_service_provider=self.santander_fsp,
            collector=self.individuals_3[0],
            entitlement_quantity=1000,
            entitlement_quantity_usd=200,
            delivery_type=self.dm_transfer,
            status=Payment.STATUS_NOT_DISTRIBUTED,
            household=self.household_3,
            currency="PLN",
        )

        # check created payments
        payment_1.refresh_from_db()
        payment_2.refresh_from_db()
        assert payment_1.entitlement_quantity == 500
        assert payment_1.entitlement_quantity_usd == 100
        assert payment_2.entitlement_quantity == 1000
        assert payment_2.entitlement_quantity_usd == 200

        new_get_volume_by_delivery_mechanism_response = self.graphql_request(
            request_string=GET_VOLUME_BY_DELIVERY_MECHANISM_QUERY,
            context=self.context,
            variables={
                "paymentPlanId": self.encoded_payment_plan_id,
            },
        )
        assert (
            "errors" not in new_get_volume_by_delivery_mechanism_response
        ), new_get_volume_by_delivery_mechanism_response

        new_data = new_get_volume_by_delivery_mechanism_response["data"]["paymentPlan"]["volumeByDeliveryMechanism"]
        assert len(new_data) == 1
        self.assertEqual(new_data[0]["volume"], 1500)
        self.assertEqual(new_data[0]["volumeUsd"], 300)
