import json

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


class TestFSPSetup(APITestCase):
    CHOOSE_DELIVERY_MECHANISMS_MUTATION = """
mutation ChooseDeliveryMechanismsForPaymentPlan($input: ChooseDeliveryMechanismsForPaymentPlanInput!) {
  chooseDeliveryMechanismsForPaymentPlan(input: $input) {
    paymentPlan {
      id
      deliveryMechanisms
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
            cls.user, [Permissions.PAYMENT_MODULE_CREATE], BusinessArea.objects.get(slug="afghanistan")
        )

    def test_choosing_delivery_mechanism_order(self):
        payment_plan = PaymentPlanFactory(total_households_count=1)
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
        # TODO: make it not play with stringified jsons
        self.assertEqual(
            json.loads(payment_plan_with_delivery_mechanisms["deliveryMechanisms"][0]),
            {"name": GenericPayment.DELIVERY_TYPE_TRANSFER, "order": 1},
        )
        self.assertEqual(
            json.loads(payment_plan_with_delivery_mechanisms["deliveryMechanisms"][1]),
            {"name": GenericPayment.DELIVERY_TYPE_VOUCHER, "order": 2},
        )

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
            id="6FFB6BB7-3D43-4ECE-BB0E-21FDE209AFAF",
            created_by=self.user,
            candidate_list_targeting_criteria=(TargetingCriteriaFactory()),
            business_area=self.business_area,
        )
        target_population.apply_criteria_query()  # simulate having TP households calculated
        payment_plan = PaymentPlanFactory(total_households_count=3, target_population=target_population)

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

    def test_providing_non_unique_delivery_mechanisms(self):
        payment_plan = PaymentPlanFactory(total_households_count=1)
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


# TODO:
# test getting delivery mechanisms on FE by query
