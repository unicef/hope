import json

from hct_mis_api.apps.payment.fixtures import FinancialServiceProviderFactory
from hct_mis_api.apps.payment.models import PaymentPlan
from hct_mis_api.apps.household.models import ROLE_PRIMARY
from hct_mis_api.apps.household.fixtures import IndividualRoleInHouseholdFactory
from hct_mis_api.apps.targeting.fixtures import TargetPopulationFactory, TargetingCriteriaFactory
from hct_mis_api.apps.payment.fixtures import PaymentChannelFactory
from hct_mis_api.apps.payment.models import GenericPayment
from hct_mis_api.apps.core.utils import encode_id_base64
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.payment.fixtures import PaymentPlanFactory
from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.household.fixtures import create_household_and_individuals
from hct_mis_api.apps.household.models import HEAD, MALE
from hct_mis_api.apps.registration_data.fixtures import RegistrationDataImportFactory
from hct_mis_api.apps.targeting.models import TargetPopulation


class TestFSPSetup(APITestCase):
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

    @classmethod
    def setUpTestData(cls):
        create_afghanistan()
        cls.business_area = BusinessArea.objects.get(slug="afghanistan")
        cls.user = UserFactory.create()
        cls.create_user_role_with_permissions(
            cls.user,
            [Permissions.PAYMENT_MODULE_CREATE, Permissions.PAYMENT_MODULE_VIEW_DETAILS],
            BusinessArea.objects.get(slug="afghanistan"),
        )

    def test_choosing_delivery_mechanism_order(self):
        payment_plan = PaymentPlanFactory(total_households_count=1, status=PaymentPlan.Status.LOCKED)
        encoded_payment_plan_id = encode_id_base64(payment_plan.id, "PaymentPlan")
        create_program_mutation_variables_without_delivery_mechanisms = dict(
            input=dict(
                paymentPlanId=encoded_payment_plan_id,
                deliveryMechanisms=[],
            )
        )
        response_without_mechanisms = self.graphql_request(
            request_string=self.CHOOSE_DELIVERY_MECHANISMS_MUTATION,
            context={"user": self.user},
            variables=create_program_mutation_variables_without_delivery_mechanisms,
        )
        assert response_without_mechanisms is not None and "data" in response_without_mechanisms
        payment_plan_without_delivery_mechanisms = response_without_mechanisms["data"][
            "chooseDeliveryMechanismsForPaymentPlan"
        ]["paymentPlan"]
        self.assertEqual(payment_plan_without_delivery_mechanisms["id"], encoded_payment_plan_id)
        self.assertEqual(payment_plan_without_delivery_mechanisms["deliveryMechanisms"], [])

        create_program_mutation_variables_with_delivery_mechanisms = dict(
            input=dict(
                paymentPlanId=encoded_payment_plan_id,
                deliveryMechanisms=[GenericPayment.DELIVERY_TYPE_TRANSFER, GenericPayment.DELIVERY_TYPE_VOUCHER],
            )
        )
        response_with_mechanisms = self.graphql_request(
            request_string=self.CHOOSE_DELIVERY_MECHANISMS_MUTATION,
            context={"user": self.user},
            variables=create_program_mutation_variables_with_delivery_mechanisms,
        )
        assert response_with_mechanisms is not None and "data" in response_with_mechanisms
        payment_plan_with_delivery_mechanisms = response_with_mechanisms["data"][
            "chooseDeliveryMechanismsForPaymentPlan"
        ]["paymentPlan"]
        self.assertEqual(payment_plan_with_delivery_mechanisms["id"], encoded_payment_plan_id)
        self.assertEqual(
            payment_plan_with_delivery_mechanisms["deliveryMechanisms"][0],
            {"name": GenericPayment.DELIVERY_TYPE_TRANSFER, "order": 1},
        )
        self.assertEqual(
            payment_plan_with_delivery_mechanisms["deliveryMechanisms"][1],
            {"name": GenericPayment.DELIVERY_TYPE_VOUCHER, "order": 2},
        )

    def test_being_able_to_get_possible_delivery_mechanisms(self):
        query = """
query AllDeliveryMechanisms {
    allDeliveryMechanisms {
        name
        value
    }
}
"""
        response = self.graphql_request(request_string=query, context={"user": self.user})
        assert response is not None and "data" in response
        all_delivery_mechanisms = response["data"]["allDeliveryMechanisms"]
        assert all(key in entry for entry in all_delivery_mechanisms for key in ["name", "value"])

    def test_lacking_delivery_mechanisms(self):
        registration_data_import = RegistrationDataImportFactory(business_area=self.business_area)

        self.household_1, self.individuals_1 = create_household_and_individuals(
            household_data={
                "registration_data_import": registration_data_import,
                "business_area": self.business_area,
            },
            individuals_data=[{}],
        )
        PaymentChannelFactory(
            individual=self.individuals_1[0],
            delivery_mechanism=GenericPayment.DELIVERY_TYPE_VOUCHER,
        )
        IndividualRoleInHouseholdFactory(
            individual=self.individuals_1[0],
            household=self.household_1,
            role=ROLE_PRIMARY,
        )

        self.household_2, self.individuals_2 = create_household_and_individuals(
            household_data={
                "registration_data_import": registration_data_import,
                "business_area": self.business_area,
            },
            individuals_data=[{}],
        )
        PaymentChannelFactory(
            individual=self.individuals_2[0],
            delivery_mechanism=GenericPayment.DELIVERY_TYPE_TRANSFER,
        )
        IndividualRoleInHouseholdFactory(
            individual=self.individuals_2[0],
            household=self.household_2,
            role=ROLE_PRIMARY,
        )

        self.household_3, self.individuals_3 = create_household_and_individuals(
            household_data={
                "registration_data_import": registration_data_import,
                "business_area": self.business_area,
            },
            individuals_data=[{}],
        )
        IndividualRoleInHouseholdFactory(
            individual=self.individuals_3[0],
            household=self.household_3,
            role=ROLE_PRIMARY,
        )
        # no payment channel for 3rd household

        target_population = TargetPopulationFactory(
            created_by=self.user,
            candidate_list_targeting_criteria=(TargetingCriteriaFactory()),
            business_area=self.business_area,
            status=TargetPopulation.STATUS_LOCKED,
        )
        target_population.apply_criteria_query()  # simulate having TP households calculated
        payment_plan = PaymentPlanFactory(
            total_households_count=3, target_population=target_population, status=PaymentPlan.Status.LOCKED
        )

        encoded_payment_plan_id = encode_id_base64(payment_plan.id, "PaymentPlan")
        create_program_mutation_variables = dict(
            input=dict(
                paymentPlanId=encoded_payment_plan_id,
                deliveryMechanisms=[GenericPayment.DELIVERY_TYPE_TRANSFER],
            )
        )
        response = self.graphql_request(
            request_string=self.CHOOSE_DELIVERY_MECHANISMS_MUTATION,
            context={"user": self.user},
            variables=create_program_mutation_variables,
        )
        assert "errors" in response
        assert (
            "Selected delivery mechanisms are not sufficient to serve all beneficiaries"
            in response["errors"][0]["message"]
        )
        # TODO: once it's clear what info to show here, add assertions like
        # "Please add X, Y and Z to move to next step"

    def test_providing_non_unique_delivery_mechanisms(self):
        payment_plan = PaymentPlanFactory(total_households_count=1, status=PaymentPlan.Status.LOCKED)
        encoded_payment_plan_id = encode_id_base64(payment_plan.id, "PaymentPlan")
        create_program_mutation_variables = dict(
            input=dict(
                paymentPlanId=encoded_payment_plan_id,
                deliveryMechanisms=[GenericPayment.DELIVERY_TYPE_TRANSFER, GenericPayment.DELIVERY_TYPE_TRANSFER],
            )
        )
        response = self.graphql_request(
            request_string=self.CHOOSE_DELIVERY_MECHANISMS_MUTATION,
            context={"user": self.user},
            variables=create_program_mutation_variables,
        )
        assert response["errors"][0]["message"] == "Delivery mechanisms must be unique"


class TestFSPAssignment(TestFSPSetup):

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
        }
    }
}
"""

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
            }
        }
    }
}
"""

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        registration_data_import = RegistrationDataImportFactory(business_area=cls.business_area)

        cls.household_1, cls.individuals_1 = create_household_and_individuals(
            household_data={
                "registration_data_import": registration_data_import,
                "business_area": cls.business_area,
            },
            individuals_data=[{}],
        )
        PaymentChannelFactory(
            individual=cls.individuals_1[0],
            delivery_mechanism=GenericPayment.DELIVERY_TYPE_VOUCHER,
        )
        IndividualRoleInHouseholdFactory(
            individual=cls.individuals_1[0],
            household=cls.household_1,
            role=ROLE_PRIMARY,
        )

        cls.household_2, cls.individuals_2 = create_household_and_individuals(
            household_data={
                "registration_data_import": registration_data_import,
                "business_area": cls.business_area,
            },
            individuals_data=[{}],
        )
        PaymentChannelFactory(
            individual=cls.individuals_2[0],
            delivery_mechanism=GenericPayment.DELIVERY_TYPE_TRANSFER,
        )
        IndividualRoleInHouseholdFactory(
            individual=cls.individuals_2[0],
            household=cls.household_2,
            role=ROLE_PRIMARY,
        )

        target_population = TargetPopulationFactory(
            id="6FFB6BB7-3D43-4ECE-BB0E-21FDE209AFAF",
            created_by=cls.user,
            candidate_list_targeting_criteria=(TargetingCriteriaFactory()),
            business_area=cls.business_area,
            status=TargetPopulation.STATUS_LOCKED,
        )
        target_population.apply_criteria_query()  # simulate having TP households calculated
        cls.payment_plan = PaymentPlanFactory(
            total_households_count=3, target_population=target_population, status=PaymentPlan.Status.LOCKED
        )
        cls.encoded_payment_plan_id = encode_id_base64(cls.payment_plan.id, "PaymentPlan")

        cls.santander_fsp = FinancialServiceProviderFactory(
            name="Santander",
            delivery_mechanisms=[GenericPayment.DELIVERY_TYPE_TRANSFER],
        )
        cls.encoded_santander_fsp_id = encode_id_base64(cls.santander_fsp.id, "FinancialServiceProvider")

        cls.bank_of_america_fsp = FinancialServiceProviderFactory(
            name="Bank of America",
            delivery_mechanisms=[GenericPayment.DELIVERY_TYPE_VOUCHER],
        )
        cls.encoded_bank_of_america_fsp_id = encode_id_base64(cls.bank_of_america_fsp.id, "FinancialServiceProvider")

        FinancialServiceProviderFactory(
            name="Bank of Europe",
            delivery_mechanisms=[GenericPayment.DELIVERY_TYPE_VOUCHER],
        )

    def test_assigning_fsps_to_delivery_mechanism(self):
        create_program_mutation_variables = dict(
            input=dict(
                paymentPlanId=self.encoded_payment_plan_id,
                deliveryMechanisms=[GenericPayment.DELIVERY_TYPE_TRANSFER, GenericPayment.DELIVERY_TYPE_VOUCHER],
            )
        )
        response = self.graphql_request(
            request_string=self.CHOOSE_DELIVERY_MECHANISMS_MUTATION,
            context={"user": self.user},
            variables=create_program_mutation_variables,
        )
        assert "errors" not in response

        available_mechanisms_query = """
query AvailableFspsForDeliveryMechanisms($deliveryMechanisms: [String!]!) {
    availableFspsForDeliveryMechanisms(deliveryMechanisms: $deliveryMechanisms) {
        deliveryMechanism
        fsps {
            id
            name
        }
    }
}
"""
        query_response = self.graphql_request(
            request_string=available_mechanisms_query,
            context={"user": self.user},
            variables={
                "deliveryMechanisms": [GenericPayment.DELIVERY_TYPE_TRANSFER, GenericPayment.DELIVERY_TYPE_VOUCHER]
            },
        )
        available_mechs_data = query_response["data"]["availableFspsForDeliveryMechanisms"]
        assert len(available_mechs_data) == 2
        assert available_mechs_data[0]["deliveryMechanism"] == GenericPayment.DELIVERY_TYPE_TRANSFER
        assert available_mechs_data[0]["fsps"][0]["name"] == "Santander"
        assert available_mechs_data[1]["deliveryMechanism"] == GenericPayment.DELIVERY_TYPE_VOUCHER
        voucher_fsp_names = [f["name"] for f in available_mechs_data[1]["fsps"]]
        assert "Bank of America" in voucher_fsp_names
        assert "Bank of Europe" in voucher_fsp_names

        bad_mutation_response = self.graphql_request(
            request_string=self.ASSIGN_FSPS_MUTATION,
            context={"user": self.user},
            variables={
                "paymentPlanId": self.encoded_payment_plan_id,
                "mappings": [
                    {
                        "deliveryMechanism": GenericPayment.DELIVERY_TYPE_TRANSFER,
                        "fspId": self.encoded_santander_fsp_id,
                    }
                ],
            },
        )
        assert "errors" in bad_mutation_response, bad_mutation_response
        assert (
            bad_mutation_response["errors"][0]["message"]
            == "Please assign FSP to all delivery mechanisms before moving to next step"
        )

        another_bad_mutation_response = self.graphql_request(
            request_string=self.ASSIGN_FSPS_MUTATION,
            context={"user": self.user},
            variables={
                "paymentPlanId": self.encoded_payment_plan_id,
                "mappings": [
                    {
                        "deliveryMechanism": GenericPayment.DELIVERY_TYPE_VOUCHER,
                        "fspId": self.encoded_santander_fsp_id,
                    }
                ],
            },
        )
        assert "errors" in another_bad_mutation_response, another_bad_mutation_response
        self.assertEqual(
            another_bad_mutation_response["errors"][0]["message"],
            "Delivery mechanism 'Voucher' is not supported by FSP 'Santander'",
        )

        current_payment_plan_response = self.graphql_request(
            request_string=self.CURRENT_PAYMENT_PLAN_QUERY,
            context={"user": self.user},
            variables={"id": self.encoded_payment_plan_id},
        )
        data = current_payment_plan_response["data"]["paymentPlan"]
        assert len(data["deliveryMechanisms"]) == 2
        assert data["deliveryMechanisms"][0]["fsp"] is None
        assert data["deliveryMechanisms"][1]["fsp"] is None

        complete_mutation_response = self.graphql_request(
            request_string=self.ASSIGN_FSPS_MUTATION,
            context={"user": self.user},
            variables={
                "paymentPlanId": self.encoded_payment_plan_id,
                "mappings": [
                    {
                        "deliveryMechanism": GenericPayment.DELIVERY_TYPE_TRANSFER,
                        "fspId": self.encoded_santander_fsp_id,
                    },
                    {
                        "deliveryMechanism": GenericPayment.DELIVERY_TYPE_VOUCHER,
                        "fspId": self.encoded_bank_of_america_fsp_id,
                    },
                ],
            },
        )
        assert "errors" not in complete_mutation_response, complete_mutation_response
        complete_payment_plan_data = complete_mutation_response["data"]["assignFspToDeliveryMechanism"]["paymentPlan"]
        assert complete_payment_plan_data["deliveryMechanisms"][0]["fsp"]["id"] == self.encoded_santander_fsp_id
        assert complete_payment_plan_data["deliveryMechanisms"][1]["fsp"]["id"] == self.encoded_bank_of_america_fsp_id

        new_payment_plan_response = self.graphql_request(
            request_string=self.CURRENT_PAYMENT_PLAN_QUERY,
            context={"user": self.user},
            variables={"id": self.encoded_payment_plan_id},
        )
        new_data = new_payment_plan_response["data"]["paymentPlan"]
        assert len(new_data["deliveryMechanisms"]) == 2
        assert new_data["deliveryMechanisms"][0]["fsp"] is not None
        assert new_data["deliveryMechanisms"][1]["fsp"] is not None

    def test_editing_fsps_assignments(self):
        create_program_mutation_variables = dict(
            input=dict(
                paymentPlanId=self.encoded_payment_plan_id,
                deliveryMechanisms=[GenericPayment.DELIVERY_TYPE_TRANSFER, GenericPayment.DELIVERY_TYPE_VOUCHER],
            )
        )
        response = self.graphql_request(
            request_string=self.CHOOSE_DELIVERY_MECHANISMS_MUTATION,
            context={"user": self.user},
            variables=create_program_mutation_variables,
        )
        assert "errors" not in response

        complete_mutation_response = self.graphql_request(
            request_string=self.ASSIGN_FSPS_MUTATION,
            context={"user": self.user},
            variables={
                "paymentPlanId": self.encoded_payment_plan_id,
                "mappings": [
                    {
                        "deliveryMechanism": GenericPayment.DELIVERY_TYPE_TRANSFER,
                        "fspId": self.encoded_santander_fsp_id,
                    },
                    {
                        "deliveryMechanism": GenericPayment.DELIVERY_TYPE_VOUCHER,
                        "fspId": self.encoded_bank_of_america_fsp_id,
                    },
                ],
            },
        )
        assert "errors" not in complete_mutation_response, complete_mutation_response
        complete_payment_plan_data = complete_mutation_response["data"]["assignFspToDeliveryMechanism"]["paymentPlan"]
        assert complete_payment_plan_data["deliveryMechanisms"][0]["fsp"]["id"] == self.encoded_santander_fsp_id
        assert complete_payment_plan_data["deliveryMechanisms"][1]["fsp"]["id"] == self.encoded_bank_of_america_fsp_id

        payment_plan_response = self.graphql_request(
            request_string=self.CURRENT_PAYMENT_PLAN_QUERY,
            context={"user": self.user},
            variables={"id": self.encoded_payment_plan_id},
        )
        new_data = payment_plan_response["data"]["paymentPlan"]
        assert len(new_data["deliveryMechanisms"]) == 2
        assert new_data["deliveryMechanisms"][0]["fsp"] is not None
        assert new_data["deliveryMechanisms"][1]["fsp"] is not None

        # TODO: edit
