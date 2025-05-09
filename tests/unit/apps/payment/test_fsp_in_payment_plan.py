from typing import Any

from graphql import GraphQLError

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.currencies import USDC
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.core.utils import encode_id_base64
from hct_mis_api.apps.household.fixtures import (
    IndividualRoleInHouseholdFactory,
    create_household_and_individuals,
)
from hct_mis_api.apps.household.models import ROLE_PRIMARY
from hct_mis_api.apps.payment.delivery_mechanisms import DeliveryMechanismChoices
from hct_mis_api.apps.payment.fixtures import (
    DeliveryMechanismPerPaymentPlanFactory,
    FinancialServiceProviderFactory,
    FspXlsxTemplatePerDeliveryMechanismFactory,
    PaymentFactory,
    PaymentPlanFactory,
    generate_delivery_mechanisms,
)
from hct_mis_api.apps.payment.models import (
    DeliveryMechanism,
    DeliveryMechanismPerPaymentPlan,
    Payment,
    PaymentPlan,
)
from hct_mis_api.apps.payment.services.payment_plan_services import PaymentPlanService
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.registration_data.fixtures import RegistrationDataImportFactory
from hct_mis_api.apps.targeting.fixtures import TargetingCriteriaFactory


def base_setup(cls: Any) -> None:
    create_afghanistan()
    cls.business_area = BusinessArea.objects.get(slug="afghanistan")
    cls.program = ProgramFactory(business_area=cls.business_area)
    cls.user = UserFactory.create()
    cls.create_user_role_with_permissions(
        cls.user,
        [Permissions.PM_CREATE, Permissions.PM_VIEW_DETAILS],
        BusinessArea.objects.get(slug="afghanistan"),
        whole_business_area_access=True,
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
    targeting_criteria = TargetingCriteriaFactory()
    cls.payment_plan = PaymentPlanFactory(
        total_households_count=4,
        targeting_criteria=targeting_criteria,
        status=PaymentPlan.Status.LOCKED,
        program_cycle=cls.program.cycles.first(),
        created_by=cls.user,
    )
    cls.encoded_payment_plan_id = encode_id_base64(cls.payment_plan.id, "PaymentPlan")

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


ASSIGN_FSPS_MUTATION = """
mutation AssignFspToDeliveryMechanism($paymentPlanId: ID!, $mappings: [FSPToDeliveryMechanismMappingInput!]!) {
    assignFspToDeliveryMechanism(input: {
        paymentPlanId: $paymentPlanId,
        mappings: $mappings
    }) {
        paymentPlan {
            id
            deliveryMechanisms {
                name
                order
                fsp {
                    id
                }
                chosenConfiguration
            }
        }
    }
}
"""

CHOOSE_DELIVERY_MECHANISMS_MUTATION = """
mutation ChooseDeliveryMechanismsForPaymentPlan($input: ChooseDeliveryMechanismsForPaymentPlanInput!) {
  chooseDeliveryMechanismsForPaymentPlan(input: $input) {
    paymentPlan {
      id
      deliveryMechanisms {
        order
        name
      }
    }
  }
}
"""

CURRENT_PAYMENT_PLAN_QUERY = """
query PaymentPlan($id: ID!) {
    paymentPlan(id: $id) {
        id
        deliveryMechanisms {
            name
            order
            fsp {
                id
            }
            chosenConfiguration
        }
    }
}
"""

AVAILABLE_FSPS_FOR_DELIVERY_MECHANISMS_QUERY = """
query AvailableFspsForDeliveryMechanisms($input: AvailableFspsForDeliveryMechanismsInput!) {
    availableFspsForDeliveryMechanisms(input: $input) {
        deliveryMechanism
        fsps {
            id
            name
            configurations {
                id
                key
                label
            }
        }
    }
}
"""


class TestFSPSetup(APITestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        base_setup(cls)

    def test_choosing_delivery_mechanism_order(self) -> None:
        payment_plan = PaymentPlanFactory(
            total_households_count=1,
            status=PaymentPlan.Status.LOCKED,
            program_cycle=self.program.cycles.first(),
            created_by=self.user,
        )
        encoded_payment_plan_id = encode_id_base64(payment_plan.id, "PaymentPlan")
        choose_dms_mutation_variables_mutation_variables_without_delivery_mechanisms = {
            "input": {
                "paymentPlanId": encoded_payment_plan_id,
                "deliveryMechanisms": [],
            }
        }
        response_without_mechanisms = self.graphql_request(
            request_string=CHOOSE_DELIVERY_MECHANISMS_MUTATION,
            context=self.context,
            variables=choose_dms_mutation_variables_mutation_variables_without_delivery_mechanisms,
        )
        assert response_without_mechanisms is not None and "data" in response_without_mechanisms
        payment_plan_without_delivery_mechanisms = response_without_mechanisms["data"][
            "chooseDeliveryMechanismsForPaymentPlan"
        ]["paymentPlan"]
        self.assertEqual(payment_plan_without_delivery_mechanisms["id"], encoded_payment_plan_id)
        self.assertEqual(payment_plan_without_delivery_mechanisms["deliveryMechanisms"], [])

        response_with_wrong_mechanism = self.graphql_request(
            request_string=CHOOSE_DELIVERY_MECHANISMS_MUTATION,
            context=self.context,
            variables={
                "input": {
                    "paymentPlanId": encoded_payment_plan_id,
                    "deliveryMechanisms": [""],  # empty string is invalid
                }
            },
        )
        assert "errors" in response_with_wrong_mechanism, response_with_wrong_mechanism
        self.assertEqual(
            response_with_wrong_mechanism["errors"][0]["message"],
            "Delivery mechanism '' is not active/valid.",
        )

        choose_dms_mutation_variables_mutation_variables_with_delivery_mechanisms = {
            "input": {
                "paymentPlanId": encoded_payment_plan_id,
                "deliveryMechanisms": [
                    self.dm_transfer.code,
                    self.dm_voucher.code,
                ],
            }
        }
        response_with_mechanisms = self.graphql_request(
            request_string=CHOOSE_DELIVERY_MECHANISMS_MUTATION,
            context=self.context,
            variables=choose_dms_mutation_variables_mutation_variables_with_delivery_mechanisms,
        )
        assert response_with_mechanisms is not None and "data" in response_with_mechanisms
        payment_plan_with_delivery_mechanisms = response_with_mechanisms["data"][
            "chooseDeliveryMechanismsForPaymentPlan"
        ]["paymentPlan"]
        self.assertEqual(payment_plan_with_delivery_mechanisms["id"], encoded_payment_plan_id)
        self.assertEqual(
            payment_plan_with_delivery_mechanisms["deliveryMechanisms"][0],
            {"name": DeliveryMechanismChoices.DELIVERY_TYPE_TRANSFER, "order": 1},
        )
        self.assertEqual(
            payment_plan_with_delivery_mechanisms["deliveryMechanisms"][1],
            {"name": DeliveryMechanismChoices.DELIVERY_TYPE_VOUCHER, "order": 2},
        )

    def test_error_when_choosing_delivery_mechanism_with_usdc_currency(self) -> None:
        payment_plan = PaymentPlanFactory(
            total_households_count=1,
            status=PaymentPlan.Status.LOCKED,
            program_cycle=self.program.cycles.first(),
            currency=USDC,
            created_by=self.user,
        )
        assert payment_plan.currency == USDC
        encoded_payment_plan_id = encode_id_base64(payment_plan.id, "PaymentPlan")
        variables = {
            "input": {
                "paymentPlanId": encoded_payment_plan_id,
                "deliveryMechanisms": [
                    self.dm_transfer.code,
                    self.dm_voucher.code,
                ],
            }
        }
        response_with_error = self.graphql_request(
            request_string=CHOOSE_DELIVERY_MECHANISMS_MUTATION,
            context=self.context,
            variables=variables,
        )

        assert "errors" in response_with_error, response_with_error
        assert (
            response_with_error["errors"][0]["message"]
            == "For currency USDC can be assigned only delivery mechanism Transfer to Digital Wallet"
        )

    def test_being_able_to_get_possible_delivery_mechanisms(self) -> None:
        query = """
            query AllDeliveryMechanisms {
                allDeliveryMechanisms {
                    name
                    value
                }
            }
        """
        response = self.graphql_request(request_string=query, context=self.context)
        assert response is not None and "data" in response
        all_delivery_mechanisms = response["data"]["allDeliveryMechanisms"]
        assert all_delivery_mechanisms is not None, response
        assert all(key in entry for entry in all_delivery_mechanisms for key in ["name", "value"]), (
            all_delivery_mechanisms
        )

    def test_providing_non_unique_delivery_mechanisms(self) -> None:
        payment_plan = PaymentPlanFactory(
            total_households_count=1,
            status=PaymentPlan.Status.LOCKED,
            program_cycle=self.program.cycles.first(),
            created_by=self.user,
        )
        encoded_payment_plan_id = encode_id_base64(payment_plan.id, "PaymentPlan")
        choose_dms_mutation_variables_mutation_variables = {
            "input": {
                "paymentPlanId": encoded_payment_plan_id,
                "deliveryMechanisms": [
                    self.dm_transfer.code,
                    self.dm_transfer.code,
                ],
            }
        }
        response = self.graphql_request(
            request_string=CHOOSE_DELIVERY_MECHANISMS_MUTATION,
            context=self.context,
            variables=choose_dms_mutation_variables_mutation_variables,
        )
        assert "errors" not in response, response

        current_payment_plan_response = self.graphql_request(
            request_string=CURRENT_PAYMENT_PLAN_QUERY,
            context=self.context,
            variables={"id": encoded_payment_plan_id},
        )
        assert "errors" not in current_payment_plan_response, current_payment_plan_response
        data = current_payment_plan_response["data"]["paymentPlan"]
        assert len(data["deliveryMechanisms"]) == 2
        assert data["deliveryMechanisms"][0]["name"] == DeliveryMechanismChoices.DELIVERY_TYPE_TRANSFER
        assert data["deliveryMechanisms"][1]["name"] == DeliveryMechanismChoices.DELIVERY_TYPE_TRANSFER


class TestFSPAssignment(APITestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        base_setup(cls)
        payment_plan_setup(cls)

    def test_assigning_fsps_to_delivery_mechanism(self) -> None:
        choose_dms_mutation_variables_mutation_variables = {
            "input": {
                "paymentPlanId": self.encoded_payment_plan_id,
                "deliveryMechanisms": [
                    self.dm_transfer.code,
                    self.dm_voucher.code,
                ],
            }
        }
        response = self.graphql_request(
            request_string=CHOOSE_DELIVERY_MECHANISMS_MUTATION,
            context=self.context,
            variables=choose_dms_mutation_variables_mutation_variables,
        )
        assert "errors" not in response, response

        query_response = self.graphql_request(
            request_string=AVAILABLE_FSPS_FOR_DELIVERY_MECHANISMS_QUERY,
            context=self.context,
            variables={
                "input": {
                    "paymentPlanId": self.encoded_payment_plan_id,
                }
            },
        )
        assert "errors" not in query_response, query_response
        available_mechs_data = query_response["data"]["availableFspsForDeliveryMechanisms"]
        assert available_mechs_data is not None, query_response
        assert len(available_mechs_data) == 2
        assert available_mechs_data[0]["deliveryMechanism"] == self.dm_transfer.name
        transfer_fsps_names = [x["name"] for x in available_mechs_data[0]["fsps"]]
        assert "Santander" in transfer_fsps_names
        assert "Bank of Europe" in transfer_fsps_names
        assert available_mechs_data[1]["deliveryMechanism"] == self.dm_voucher.name
        voucher_fsp_names = [f["name"] for f in available_mechs_data[1]["fsps"]]
        assert "Bank of America" in voucher_fsp_names
        assert "Bank of Europe" in voucher_fsp_names

        bad_mutation_response = self.graphql_request(
            request_string=ASSIGN_FSPS_MUTATION,
            context=self.context,
            variables={
                "paymentPlanId": self.encoded_payment_plan_id,
                "mappings": [
                    {
                        "deliveryMechanism": self.dm_transfer.code,
                        "fspId": self.encoded_santander_fsp_id,
                        "order": 1,
                    }
                ],
            },
        )
        assert "errors" in bad_mutation_response, bad_mutation_response
        assert (
            bad_mutation_response["errors"][0]["message"]
            == "Please assign FSP to all delivery mechanisms before moving to next step"
        )

        current_payment_plan_response = self.graphql_request(
            request_string=CURRENT_PAYMENT_PLAN_QUERY,
            context=self.context,
            variables={"id": self.encoded_payment_plan_id},
        )
        data = current_payment_plan_response["data"]["paymentPlan"]
        assert len(data["deliveryMechanisms"]) == 2
        assert data["deliveryMechanisms"][0]["fsp"] is None
        assert data["deliveryMechanisms"][1]["fsp"] is None

        complete_mutation_response = self.graphql_request(
            request_string=ASSIGN_FSPS_MUTATION,
            context=self.context,
            variables={
                "paymentPlanId": self.encoded_payment_plan_id,
                "mappings": [
                    {
                        "deliveryMechanism": self.dm_transfer.code,
                        "fspId": self.encoded_santander_fsp_id,
                        "order": 1,
                        "chosenConfiguration": "config_1",
                    },
                    {
                        "deliveryMechanism": self.dm_voucher.code,
                        "fspId": self.encoded_bank_of_america_fsp_id,
                        "order": 2,
                        "chosenConfiguration": "config_2",
                    },
                ],
            },
        )
        assert "errors" not in complete_mutation_response, complete_mutation_response
        complete_payment_plan_data = complete_mutation_response["data"]["assignFspToDeliveryMechanism"]["paymentPlan"]
        assert complete_payment_plan_data["deliveryMechanisms"][0]["fsp"]["id"] == self.encoded_santander_fsp_id
        assert complete_payment_plan_data["deliveryMechanisms"][1]["fsp"]["id"] == self.encoded_bank_of_america_fsp_id
        assert complete_payment_plan_data["deliveryMechanisms"][0]["chosenConfiguration"] == "config_1"
        assert complete_payment_plan_data["deliveryMechanisms"][1]["chosenConfiguration"] == "config_2"

        new_payment_plan_response = self.graphql_request(
            request_string=CURRENT_PAYMENT_PLAN_QUERY,
            context=self.context,
            variables={"id": self.encoded_payment_plan_id},
        )
        new_data = new_payment_plan_response["data"]["paymentPlan"]
        assert len(new_data["deliveryMechanisms"]) == 2
        assert new_data["deliveryMechanisms"][0]["fsp"]["id"] == self.encoded_santander_fsp_id
        assert new_data["deliveryMechanisms"][1]["fsp"]["id"] == self.encoded_bank_of_america_fsp_id

    def test_editing_fsps_assignments(self) -> None:
        choose_dms_mutation_variables = {
            "input": {
                "paymentPlanId": self.encoded_payment_plan_id,
                "deliveryMechanisms": [
                    self.dm_transfer.code,
                    self.dm_voucher.code,
                ],
            }
        }
        response = self.graphql_request(
            request_string=CHOOSE_DELIVERY_MECHANISMS_MUTATION,
            context=self.context,
            variables=choose_dms_mutation_variables,
        )
        assert "errors" not in response, response

        complete_mutation_response = self.graphql_request(
            request_string=ASSIGN_FSPS_MUTATION,
            context=self.context,
            variables={
                "paymentPlanId": self.encoded_payment_plan_id,
                "mappings": [
                    {
                        "deliveryMechanism": self.dm_transfer.code,
                        "fspId": self.encoded_santander_fsp_id,
                        "order": 1,
                        "chosenConfiguration": "config_1",
                    },
                    {
                        "deliveryMechanism": self.dm_voucher.code,
                        "fspId": self.encoded_bank_of_america_fsp_id,
                        "order": 2,
                        "chosenConfiguration": "config_2",
                    },
                ],
            },
        )
        assert "errors" not in complete_mutation_response, complete_mutation_response
        complete_payment_plan_data = complete_mutation_response["data"]["assignFspToDeliveryMechanism"]["paymentPlan"]
        assert complete_payment_plan_data["deliveryMechanisms"][0]["fsp"]["id"] == self.encoded_santander_fsp_id
        assert complete_payment_plan_data["deliveryMechanisms"][1]["fsp"]["id"] == self.encoded_bank_of_america_fsp_id
        assert complete_payment_plan_data["deliveryMechanisms"][0]["chosenConfiguration"] == "config_1"
        assert complete_payment_plan_data["deliveryMechanisms"][1]["chosenConfiguration"] == "config_2"

        payment_plan_response = self.graphql_request(
            request_string=CURRENT_PAYMENT_PLAN_QUERY,
            context=self.context,
            variables={"id": self.encoded_payment_plan_id},
        )
        new_data = payment_plan_response["data"]["paymentPlan"]
        assert len(new_data["deliveryMechanisms"]) == 2
        assert new_data["deliveryMechanisms"][0]["fsp"] is not None
        assert new_data["deliveryMechanisms"][1]["fsp"] is not None

        for fsp in [self.santander_fsp, self.bank_of_america_fsp, self.bank_of_europe_fsp]:
            fsp.delivery_mechanisms.add(self.dm_mobile_money)
        new_program_mutation_variables = {
            "input": {
                "paymentPlanId": self.encoded_payment_plan_id,
                "deliveryMechanisms": [
                    self.dm_mobile_money.code,
                ],
            }
        }
        new_response = self.graphql_request(
            request_string=CHOOSE_DELIVERY_MECHANISMS_MUTATION,
            context=self.context,
            variables=new_program_mutation_variables,
        )
        assert "errors" not in new_response

        edited_payment_plan_response = self.graphql_request(
            request_string=CURRENT_PAYMENT_PLAN_QUERY,
            context=self.context,
            variables={"id": self.encoded_payment_plan_id},
        )
        edited_payment_plan_data = edited_payment_plan_response["data"]["paymentPlan"]
        assert len(edited_payment_plan_data["deliveryMechanisms"]) == 1

    def test_editing_fsps_assignments_when_fsp_was_already_set_up(self) -> None:
        choose_dms_response = self.graphql_request(
            request_string=CHOOSE_DELIVERY_MECHANISMS_MUTATION,
            context=self.context,
            variables={
                "input": {
                    "paymentPlanId": self.encoded_payment_plan_id,
                    "deliveryMechanisms": [
                        self.dm_transfer.code,
                        self.dm_voucher.code,
                    ],
                }
            },
        )
        assert "errors" not in choose_dms_response, choose_dms_response

        assign_fsps_mutation_response = self.graphql_request(
            request_string=ASSIGN_FSPS_MUTATION,
            context=self.context,
            variables={
                "paymentPlanId": self.encoded_payment_plan_id,
                "mappings": [
                    {
                        "deliveryMechanism": self.dm_transfer.code,
                        "fspId": self.encoded_santander_fsp_id,
                        "order": 1,
                        "chosenConfiguration": "config_1",
                    },
                    {
                        "deliveryMechanism": self.dm_voucher.code,
                        "fspId": self.encoded_bank_of_america_fsp_id,
                        "order": 2,
                        "chosenConfiguration": "config_2",
                    },
                ],
            },
        )
        assert "errors" not in assign_fsps_mutation_response, assign_fsps_mutation_response

        current_payment_plan_response = self.graphql_request(
            request_string=CURRENT_PAYMENT_PLAN_QUERY,
            context=self.context,
            variables={"id": self.encoded_payment_plan_id},
        )
        current_data = current_payment_plan_response["data"]["paymentPlan"]
        assert len(current_data["deliveryMechanisms"]) == 2
        assert current_data["deliveryMechanisms"][0]["fsp"] is not None
        assert current_data["deliveryMechanisms"][1]["fsp"] is not None
        assert current_data["deliveryMechanisms"][0]["chosenConfiguration"] == "config_1"
        assert current_data["deliveryMechanisms"][1]["chosenConfiguration"] == "config_2"

        new_choose_dms_response = self.graphql_request(
            request_string=CHOOSE_DELIVERY_MECHANISMS_MUTATION,
            context=self.context,
            variables={
                "input": {
                    "paymentPlanId": self.encoded_payment_plan_id,
                    "deliveryMechanisms": [
                        self.dm_transfer.code,
                        self.dm_voucher.code,
                    ],  # different order
                }
            },
        )
        assert "errors" not in new_choose_dms_response, new_choose_dms_response

        new_payment_plan_response = self.graphql_request(
            request_string=CURRENT_PAYMENT_PLAN_QUERY,
            context=self.context,
            variables={"id": self.encoded_payment_plan_id},
        )
        new_data = new_payment_plan_response["data"]["paymentPlan"]
        assert len(new_data["deliveryMechanisms"]) == 2
        assert new_data["deliveryMechanisms"][0]["fsp"] is None
        assert new_data["deliveryMechanisms"][1]["fsp"] is None
        assert new_data["deliveryMechanisms"][1]["chosenConfiguration"] is None
        assert new_data["deliveryMechanisms"][0]["chosenConfiguration"] is None

    def test_choosing_different_fsps_for_the_same_delivery_mechanism(self) -> None:
        choose_dms_response = self.graphql_request(
            request_string=CHOOSE_DELIVERY_MECHANISMS_MUTATION,
            context=self.context,
            variables={
                "input": {
                    "paymentPlanId": self.encoded_payment_plan_id,
                    "deliveryMechanisms": [
                        self.dm_transfer.code,
                        self.dm_transfer.code,
                        self.dm_voucher.code,
                    ],
                }
            },
        )
        assert "errors" not in choose_dms_response, choose_dms_response

        bad_assign_fsps_mutation_response = self.graphql_request(
            request_string=ASSIGN_FSPS_MUTATION,
            context=self.context,
            variables={
                "paymentPlanId": self.encoded_payment_plan_id,
                "mappings": [
                    {
                        "deliveryMechanism": self.dm_transfer.code,
                        "fspId": self.encoded_santander_fsp_id,
                        "order": 1,
                    },
                    {
                        "deliveryMechanism": self.dm_transfer.code,
                        "fspId": self.encoded_bank_of_america_fsp_id,  # doesn't support transfer
                        "order": 2,
                    },
                    {
                        "deliveryMechanism": self.dm_voucher.code,
                        "fspId": self.encoded_bank_of_america_fsp_id,
                        "order": 3,
                    },
                ],
            },
        )
        assert "errors" in bad_assign_fsps_mutation_response, bad_assign_fsps_mutation_response

        another_bad_assign_fsps_mutation_response = self.graphql_request(
            request_string=ASSIGN_FSPS_MUTATION,
            context=self.context,
            variables={
                "paymentPlanId": self.encoded_payment_plan_id,
                "mappings": [
                    {
                        "deliveryMechanism": self.dm_transfer.code,
                        "fspId": self.encoded_santander_fsp_id,
                        "order": 1,
                    },
                    {
                        "deliveryMechanism": self.dm_transfer.code,
                        "fspId": self.encoded_santander_fsp_id,  # already chosen
                        "order": 2,
                    },
                    {
                        "deliveryMechanism": self.dm_voucher.code,
                        "fspId": self.encoded_bank_of_america_fsp_id,
                        "order": 3,
                    },
                ],
            },
        )
        assert "errors" in another_bad_assign_fsps_mutation_response, another_bad_assign_fsps_mutation_response
        assert (
            another_bad_assign_fsps_mutation_response["errors"][0]["message"]
            == "You can't assign the same FSP to the same delivery mechanism more than once"
        )

        assign_fsps_mutation_response = self.graphql_request(
            request_string=ASSIGN_FSPS_MUTATION,
            context=self.context,
            variables={
                "paymentPlanId": self.encoded_payment_plan_id,
                "mappings": [
                    {
                        "deliveryMechanism": self.dm_transfer.code,
                        "fspId": self.encoded_santander_fsp_id,
                        "order": 1,
                    },
                    {
                        "deliveryMechanism": self.dm_transfer.code,
                        "fspId": self.encoded_bank_of_europe_fsp_id,  # supports transfer
                        "order": 2,
                    },
                    {
                        "deliveryMechanism": self.dm_voucher.code,
                        "fspId": self.encoded_bank_of_america_fsp_id,
                        "order": 3,
                    },
                ],
            },
        )
        assert "errors" not in assign_fsps_mutation_response, assign_fsps_mutation_response

    def test_successful_fsp_assigment_with_no_limit(self) -> None:
        # Simulate applying steficon formula
        payment1 = PaymentFactory(
            parent=self.payment_plan,
            collector=self.individuals_2[0],
            entitlement_quantity=1000000,  # a lot
            entitlement_quantity_usd=200000,  # a lot
            status=Payment.STATUS_NOT_DISTRIBUTED,
            household=self.household_2,
            delivery_type=None,
            financial_service_provider=None,
            currency="PLN",
        )
        choose_dms_response = self.graphql_request(
            request_string=CHOOSE_DELIVERY_MECHANISMS_MUTATION,
            context=self.context,
            variables={
                "input": {
                    "paymentPlanId": self.encoded_payment_plan_id,
                    "deliveryMechanisms": [
                        self.dm_transfer.code,
                    ],
                }
            },
        )
        assert "errors" not in choose_dms_response, choose_dms_response

        assign_fsps_mutation_response = self.graphql_request(
            request_string=ASSIGN_FSPS_MUTATION,
            context=self.context,
            variables={
                "paymentPlanId": self.encoded_payment_plan_id,
                "mappings": [
                    {
                        "deliveryMechanism": self.dm_transfer.code,
                        "fspId": self.encoded_santander_fsp_id,  # no limit
                        "order": 1,
                    },
                ],
            },
        )
        assert "errors" not in assign_fsps_mutation_response, assign_fsps_mutation_response
        self.payment_plan.refresh_from_db()
        assert self.payment_plan.delivery_mechanisms.filter(financial_service_provider=self.santander_fsp).count() == 1
        payment1.refresh_from_db()
        assert payment1.financial_service_provider == self.santander_fsp
        assert payment1.delivery_type == self.dm_transfer


class TestVolumeByDeliveryMechanism(APITestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        base_setup(cls)
        payment_plan_setup(cls)

    def test_getting_volume_by_delivery_mechanism(self) -> None:
        choose_dms_response = self.graphql_request(
            request_string=CHOOSE_DELIVERY_MECHANISMS_MUTATION,
            context=self.context,
            variables={
                "input": {
                    "paymentPlanId": self.encoded_payment_plan_id,
                    "deliveryMechanisms": [
                        self.dm_transfer.code,
                        self.dm_voucher.code,
                        self.dm_cash.code,
                    ],
                }
            },
        )
        assert "errors" not in choose_dms_response, choose_dms_response

        GET_VOLUME_BY_DELIVERY_MECHANISM_QUERY = """
            query PaymentPlan($paymentPlanId: ID!) {
                paymentPlan(id: $paymentPlanId) {
                    volumeByDeliveryMechanism {
                        deliveryMechanism {
                            name
                            order
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

        too_early_get_volume_by_delivery_mechanism_response = self.graphql_request(
            request_string=GET_VOLUME_BY_DELIVERY_MECHANISM_QUERY,
            context=self.context,
            variables={
                "paymentPlanId": self.encoded_payment_plan_id,
            },
        )
        assert "errors" not in too_early_get_volume_by_delivery_mechanism_response
        assert all(
            vdm["deliveryMechanism"]["fsp"] is None
            for vdm in too_early_get_volume_by_delivery_mechanism_response["data"]["paymentPlan"][
                "volumeByDeliveryMechanism"
            ]
        )

        assign_fsps_mutation_response = self.graphql_request(
            request_string=ASSIGN_FSPS_MUTATION,
            context=self.context,
            variables={
                "paymentPlanId": self.encoded_payment_plan_id,
                "mappings": [
                    {
                        "deliveryMechanism": self.dm_transfer.code,
                        "fspId": self.encoded_santander_fsp_id,
                        "order": 1,
                    },
                    {
                        "deliveryMechanism": self.dm_voucher.code,
                        "fspId": self.encoded_bank_of_europe_fsp_id,
                        "order": 2,
                    },
                    {
                        "deliveryMechanism": self.dm_cash.code,
                        "fspId": self.encoded_bank_of_america_fsp_id,
                        "order": 3,
                    },
                ],
            },
        )
        assert "errors" not in assign_fsps_mutation_response, assign_fsps_mutation_response

        get_volume_by_delivery_mechanism_response = self.graphql_request(
            request_string=GET_VOLUME_BY_DELIVERY_MECHANISM_QUERY,
            context=self.context,
            variables={
                "paymentPlanId": self.encoded_payment_plan_id,
            },
        )
        assert "errors" not in get_volume_by_delivery_mechanism_response, get_volume_by_delivery_mechanism_response

        data = get_volume_by_delivery_mechanism_response["data"]["paymentPlan"]["volumeByDeliveryMechanism"]
        assert len(data) == 3
        assert data[0]["deliveryMechanism"]["name"] == DeliveryMechanismChoices.DELIVERY_TYPE_TRANSFER
        assert data[0]["deliveryMechanism"]["order"] == 1
        assert data[0]["deliveryMechanism"]["fsp"]["id"] == self.encoded_santander_fsp_id
        assert data[0]["volume"] == 0
        assert data[0]["volumeUsd"] == 0
        assert data[1]["deliveryMechanism"]["name"] == DeliveryMechanismChoices.DELIVERY_TYPE_VOUCHER
        assert data[1]["deliveryMechanism"]["order"] == 2
        assert data[1]["deliveryMechanism"]["fsp"]["id"] == self.encoded_bank_of_europe_fsp_id
        assert data[1]["volume"] == 0
        assert data[1]["volumeUsd"] == 0
        assert data[2]["deliveryMechanism"]["name"] == DeliveryMechanismChoices.DELIVERY_TYPE_CASH
        assert data[2]["deliveryMechanism"]["order"] == 3
        assert data[2]["deliveryMechanism"]["fsp"]["id"] == self.encoded_bank_of_america_fsp_id
        assert data[2]["volume"] == 0
        assert data[2]["volumeUsd"] == 0

        # Simulate applying steficon formula
        payment_1 = PaymentFactory(
            parent=self.payment_plan,
            financial_service_provider=self.bank_of_america_fsp,
            collector=self.individuals_2[0],
            entitlement_quantity=500,
            entitlement_quantity_usd=100,
            delivery_type=self.dm_cash,
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
        assert "errors" not in new_get_volume_by_delivery_mechanism_response, (
            new_get_volume_by_delivery_mechanism_response
        )

        new_data = new_get_volume_by_delivery_mechanism_response["data"]["paymentPlan"]["volumeByDeliveryMechanism"]
        assert len(new_data) == 3
        self.assertEqual(new_data[0]["volume"], 1000)
        self.assertEqual(new_data[0]["volumeUsd"], 200)
        self.assertEqual(new_data[1]["volume"], 0)
        self.assertEqual(new_data[1]["volumeUsd"], 0)
        self.assertEqual(new_data[2]["volume"], 500)
        self.assertEqual(new_data[2]["volumeUsd"], 100)

    def test_delivery_mechanism_validation_for_usdc(self) -> None:
        DeliveryMechanismPerPaymentPlanFactory(
            payment_plan=self.payment_plan,
            financial_service_provider=self.santander_fsp,
            delivery_mechanism=self.dm_cash,
            delivery_mechanism_order=1,
        )

        DeliveryMechanismPerPaymentPlanFactory(
            payment_plan=self.payment_plan,
            financial_service_provider=self.bank_of_america_fsp,
            delivery_mechanism=self.dm_cash,
            delivery_mechanism_order=2,
        )

        self.payment_plan.currency = USDC
        self.payment_plan.save()

        self.payment_plan.refresh_from_db(fields=["currency"])
        assert self.payment_plan.currency == USDC

        assign_fsps_mutation_response_with_error = self.graphql_request(
            request_string=ASSIGN_FSPS_MUTATION,
            context={"user": self.user},
            variables={
                "paymentPlanId": self.encoded_payment_plan_id,
                "mappings": [
                    {
                        "deliveryMechanism": self.dm_cash.code,
                        "fspId": self.encoded_santander_fsp_id,
                        "order": 1,
                    },
                    {
                        "deliveryMechanism": self.dm_transfer_to_digital_wallet.code,
                        "fspId": self.encoded_bank_of_america_fsp_id,
                        "order": 2,
                    },
                ],
            },
        )
        assert "errors" in assign_fsps_mutation_response_with_error, assign_fsps_mutation_response_with_error
        assert (
            assign_fsps_mutation_response_with_error["errors"][0]["message"]
            == "For currency USDC can be assigned only delivery mechanism Transfer to Digital Wallet"
        )
        # remove unused objects
        DeliveryMechanismPerPaymentPlan.objects.all().delete()
        # and create new
        DeliveryMechanismPerPaymentPlanFactory(
            payment_plan=self.payment_plan,
            financial_service_provider=self.santander_fsp,
            delivery_mechanism=self.dm_transfer_to_digital_wallet,
            delivery_mechanism_order=1,
        )
        DeliveryMechanismPerPaymentPlanFactory(
            payment_plan=self.payment_plan,
            financial_service_provider=self.bank_of_america_fsp,
            delivery_mechanism=self.dm_transfer_to_digital_wallet,
            delivery_mechanism_order=2,
        )
        mutation_response = self.graphql_request(
            request_string=ASSIGN_FSPS_MUTATION,
            context={"user": self.user},
            variables={
                "paymentPlanId": self.encoded_payment_plan_id,
                "mappings": [
                    {
                        "deliveryMechanism": self.dm_transfer_to_digital_wallet.code,
                        "fspId": self.encoded_santander_fsp_id,
                        "order": 1,
                    },
                    {
                        "deliveryMechanism": self.dm_transfer_to_digital_wallet.code,
                        "fspId": self.encoded_bank_of_america_fsp_id,
                        "order": 2,
                    },
                ],
            },
        )
        assert "errors" not in mutation_response, mutation_response


class TestValidateFSPPerDeliveryMechanism(APITestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        base_setup(cls)
        payment_plan_setup(cls)

    def test_chosen_delivery_mechanism_not_supported_by_fsp(self) -> None:
        dm1 = DeliveryMechanismPerPaymentPlanFactory(
            payment_plan=self.payment_plan,
            delivery_mechanism=self.dm_voucher,
            financial_service_provider=self.santander_fsp,
            delivery_mechanism_order=1,
        )
        dm_to_fsp_mapping = [
            {
                "fsp": self.santander_fsp,
                "delivery_mechanism_per_payment_plan": dm1,
            }
        ]
        with self.assertRaisesMessage(
            GraphQLError,
            f"Delivery mechanism 'Voucher' is not supported by FSP '{self.santander_fsp}'",
        ):
            PaymentPlanService(self.payment_plan).validate_fsps_per_delivery_mechanisms(
                dm_to_fsp_mapping=dm_to_fsp_mapping, update_payments=True
            )

    def test_fsp_cannot_accept_any_volume(self) -> None:
        dm1 = DeliveryMechanismPerPaymentPlanFactory(
            payment_plan=self.payment_plan,
            delivery_mechanism=self.dm_voucher,
            financial_service_provider=self.bank_of_america_fsp,
            delivery_mechanism_order=1,
        )
        dm_to_fsp_mapping = [
            {
                "fsp": self.bank_of_america_fsp,
                "delivery_mechanism_per_payment_plan": dm1,
            }
        ]
        # DM distribution limit is 0.0
        self.bank_of_america_fsp.distribution_limit = 0
        self.bank_of_america_fsp.save()

        with self.assertRaisesMessage(
            GraphQLError,
            f"{self.bank_of_america_fsp} cannot accept any volume",
        ):
            PaymentPlanService(self.payment_plan).validate_fsps_per_delivery_mechanisms(
                dm_to_fsp_mapping=dm_to_fsp_mapping, update_payments=True
            )

        # FSP with limit is used in other conflicting PP
        self.bank_of_america_fsp.distribution_limit = 1000
        self.bank_of_america_fsp.save()
        new_payment_plan = PaymentPlanFactory(
            status=PaymentPlan.Status.LOCKED_FSP,
            program_cycle=self.program.cycles.first(),
            created_by=self.user,
        )
        DeliveryMechanismPerPaymentPlanFactory(
            payment_plan=new_payment_plan,
            delivery_mechanism=self.dm_voucher,
            financial_service_provider=self.bank_of_america_fsp,
            delivery_mechanism_order=1,
        )
        with self.assertRaisesMessage(
            GraphQLError,
            f"{self.bank_of_america_fsp} cannot accept any volume",
        ):
            PaymentPlanService(self.payment_plan).validate_fsps_per_delivery_mechanisms(
                dm_to_fsp_mapping=dm_to_fsp_mapping, update_payments=True
            )

    def test_all_payments_covered_with_fsp_limit(self) -> None:
        payment2 = PaymentFactory(
            parent=self.payment_plan,
            collector=self.individuals_2[0],  # DELIVERY_TYPE_TRANSFER
            entitlement_quantity=100,
            entitlement_quantity_usd=500,
            status=Payment.STATUS_NOT_DISTRIBUTED,
            household=self.household_2,
            delivery_type=None,
            financial_service_provider=None,
            currency="PLN",
        )
        payment3 = PaymentFactory(
            parent=self.payment_plan,
            collector=self.individuals_3[0],  # DELIVERY_TYPE_TRANSFER
            entitlement_quantity=100,
            entitlement_quantity_usd=500,
            status=Payment.STATUS_NOT_DISTRIBUTED,
            household=self.household_3,
            delivery_type=None,
            financial_service_provider=None,
            currency="PLN",
        )
        payment1 = PaymentFactory(
            parent=self.payment_plan,
            collector=self.individuals_1[0],  # DELIVERY_TYPE_VOUCHER
            entitlement_quantity=100,
            entitlement_quantity_usd=1000,
            status=Payment.STATUS_NOT_DISTRIBUTED,
            household=self.household_1,
            delivery_type=None,
            financial_service_provider=None,
            currency="PLN",
        )

        self.santander_fsp.distribution_limit = 501
        self.santander_fsp.save()

        dm1 = DeliveryMechanismPerPaymentPlanFactory(
            payment_plan=self.payment_plan,
            delivery_mechanism=self.dm_transfer,
            financial_service_provider=self.santander_fsp,
            delivery_mechanism_order=1,
        )
        dm2 = DeliveryMechanismPerPaymentPlanFactory(
            payment_plan=self.payment_plan,
            delivery_mechanism=self.dm_transfer,
            financial_service_provider=self.bank_of_europe_fsp,
            delivery_mechanism_order=2,
        )

        dm_to_fsp_mapping = [
            {
                "fsp": self.santander_fsp,
                "delivery_mechanism_per_payment_plan": dm1,
            },
            {
                "fsp": self.bank_of_europe_fsp,
                "delivery_mechanism_per_payment_plan": dm2,
            },
        ]

        PaymentPlanService(self.payment_plan).validate_fsps_per_delivery_mechanisms(
            dm_to_fsp_mapping=dm_to_fsp_mapping, update_payments=True
        )

        payment2.refresh_from_db()
        # santander_fsp has a limited value, so it could take only one transfer payment
        assert payment2.financial_service_provider == self.santander_fsp
        assert payment2.delivery_type == self.dm_transfer
        payment3.refresh_from_db()
        # second transfer payment is covered by bank_of_europe_fsp
        assert payment3.financial_service_provider == self.bank_of_europe_fsp
        assert payment3.delivery_type == self.dm_transfer
        payment1.refresh_from_db()
        # voucher payment is covered by bank_of_america_fsp
        assert payment1.financial_service_provider == self.bank_of_europe_fsp
        assert payment1.delivery_type == self.dm_transfer

    def test_not_all_payments_covered_because_of_fsp_limit(self) -> None:
        PaymentFactory(
            parent=self.payment_plan,
            collector=self.individuals_2[0],  # DELIVERY_TYPE_TRANSFER
            entitlement_quantity=100,
            entitlement_quantity_usd=1000,
            status=Payment.STATUS_NOT_DISTRIBUTED,
            household=self.household_2,
            delivery_type=None,
            financial_service_provider=None,
            currency="PLN",
        )
        PaymentFactory(
            parent=self.payment_plan,
            collector=self.individuals_3[0],  # DELIVERY_TYPE_TRANSFER
            entitlement_quantity=100,
            entitlement_quantity_usd=1000,
            status=Payment.STATUS_NOT_DISTRIBUTED,
            household=self.household_3,
            delivery_type=None,
            financial_service_provider=None,
            currency="PLN",
        )
        self.bank_of_europe_fsp.distribution_limit = 1001
        self.bank_of_europe_fsp.save()

        dm1 = DeliveryMechanismPerPaymentPlanFactory(
            payment_plan=self.payment_plan,
            delivery_mechanism=self.dm_transfer,
            financial_service_provider=self.bank_of_europe_fsp,
            delivery_mechanism_order=1,
        )
        dm_to_fsp_mapping = [
            {
                "fsp": self.bank_of_europe_fsp,
                "delivery_mechanism_per_payment_plan": dm1,
            }
        ]

        with self.assertRaisesMessage(
            GraphQLError,
            "Some Payments were not assigned to selected DeliveryMechanisms/FSPs",
        ):
            PaymentPlanService(self.payment_plan).validate_fsps_per_delivery_mechanisms(
                dm_to_fsp_mapping=dm_to_fsp_mapping, update_payments=True
            )
