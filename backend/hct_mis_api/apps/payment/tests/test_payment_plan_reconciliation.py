# scenario:
# targeting is there
# payment plan is created
# locked
# entitlements calculated
# FSPs set
# FSP locked
# payments have FSPs assigned
# we receive reconciliations from FSPs
# once we have all, the payment plan is reconciliated
# once this is done, FSP (with limit) may be used in another payment plan


from unittest.mock import patch
from hct_mis_api.apps.payment.fixtures import FinancialServiceProviderFactory
from hct_mis_api.apps.payment.celery_tasks import payment_plan_apply_steficon
from hct_mis_api.apps.core.utils import encode_id_base64
from hct_mis_api.apps.steficon.fixtures import RuleFactory, RuleCommitFactory
from hct_mis_api.apps.core.utils import decode_id_string
from hct_mis_api.apps.targeting.celery_tasks import target_population_apply_steficon
from hct_mis_api.apps.household.fixtures import IndividualRoleInHouseholdFactory
from hct_mis_api.apps.household.models import ROLE_PRIMARY
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.registration_data.fixtures import RegistrationDataImportFactory
from hct_mis_api.apps.household.fixtures import create_household_and_individuals
from hct_mis_api.apps.targeting.fixtures import TargetPopulationFactory, TargetingCriteriaFactory, TargetPopulation
from hct_mis_api.apps.payment.fixtures import PaymentPlanFactory, PaymentPlan, PaymentFactory, PaymentChannelFactory
from hct_mis_api.apps.payment.models import GenericPayment


CREATE_PROGRAMME_MUTATION = """
mutation CreateProgram($programData: CreateProgramInput!) {
  createProgram(programData: $programData) {
    program {
      id
    }
  }
}
"""

UPDATE_PROGRAM_MUTATION = """
mutation UpdateProgram($programData: UpdateProgramInput!) {
  updateProgram(programData: $programData) {
    program {
      id
    }
  }
}
"""


CREATE_TARGET_POPULATION_MUTATION = """
mutation CreateTP($input: CreateTargetPopulationInput!) {
  createTargetPopulation(input: $input) {
    targetPopulation {
      id
      status
    }
  }
}
"""


CREATE_PAYMENT_PLAN_MUTATION = """
mutation CreatePaymentPlan($input: CreatePaymentPlanInput!) {
    createPaymentPlan(input: $input) {
        paymentPlan {
            id
        }
    }
}
"""

APPROVE_TARGET_POPULATION_MUTATION = """
mutation ApproveTP($id: ID!) {
    approveTargetPopulation(id: $id) {
        targetPopulation {
            id
        }
    }
}
"""

FINALIZE_TARGET_POPULATION_MUTATION = """
mutation FinalizeTP($id: ID!) {
    finalizeTargetPopulation(id: $id) {
        targetPopulation {
            id
        }
    }
}
"""

SET_STEFICON_RULE_MUTATION = """
mutation SetSteficonRuleOnPaymentPlanPaymentList($paymentPlanId: ID!, $steficonRuleId: ID!) {
    setSteficonRuleOnPaymentPlanPaymentList(paymentPlanId: $paymentPlanId, steficonRuleId: $steficonRuleId) {
        paymentPlan {
            id
        }
    }
}
"""


PAYMENT_PLAN_ACTION_MUTATION = """
mutation ActionPaymentPlanMutation($input: ActionPaymentPlanInput!) {
    actionPaymentPlanMutation(input: $input) {
        paymentPlan {
            status
            id
        }
    }
}"""

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

# TODO: make this in payment plan scope
AVAILABLE_FSPS_FOR_DELIVERY_MECHANISMS_QUERY = """
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


class TestPaymentPlanReconciliation(APITestCase):
    @classmethod
    def create_household_and_individual(cls):
        household, individuals = create_household_and_individuals(
            household_data={
                "registration_data_import": cls.registration_data_import,
                "business_area": cls.business_area,
            },
            individuals_data=[{}],
        )
        IndividualRoleInHouseholdFactory(household=household, individual=individuals[0], role=ROLE_PRIMARY)
        return household, individuals[0]

    @classmethod
    def setUpTestData(cls):
        create_afghanistan(is_payment_plan_applicable=True)
        cls.business_area = BusinessArea.objects.get(slug="afghanistan")
        cls.user = UserFactory.create()
        cls.create_user_role_with_permissions(
            cls.user,
            [
                Permissions.PAYMENT_MODULE_CREATE,
                Permissions.PAYMENT_MODULE_VIEW_DETAILS,
                Permissions.PAYMENT_MODULE_VIEW_LIST,
                Permissions.PROGRAMME_CREATE,
                Permissions.PROGRAMME_ACTIVATE,
                Permissions.TARGETING_CREATE,
                Permissions.TARGETING_LOCK,
                Permissions.TARGETING_SEND,
            ],
            cls.business_area,
        )

        cls.registration_data_import = RegistrationDataImportFactory(business_area=cls.business_area)

        cls.household_1, cls.individual_1 = cls.create_household_and_individual()
        cls.payment_channel_1_cash = PaymentChannelFactory(
            individual=cls.individual_1,
            delivery_mechanism=GenericPayment.DELIVERY_TYPE_CASH,
        )

        cls.household_2, cls.individual_2 = cls.create_household_and_individual()
        cls.payment_channel_2_cash = PaymentChannelFactory(
            individual=cls.individual_2,
            delivery_mechanism=GenericPayment.DELIVERY_TYPE_CASH,
        )

        cls.household_3, cls.individual_3 = cls.create_household_and_individual()
        cls.payment_channel_3_cash = PaymentChannelFactory(
            individual=cls.individual_3,
            delivery_mechanism=GenericPayment.DELIVERY_TYPE_CASH,
        )

    @patch("hct_mis_api.apps.payment.models.PaymentPlan.get_exchange_rate", return_value=2.0)
    def test_receiving_reconciliations_from_fsp(self, mock_get_exchange_rate):
        create_programme_response = self.graphql_request(
            request_string=CREATE_PROGRAMME_MUTATION,
            context={"user": self.user},
            variables={
                "programData": {
                    "name": "NName",
                    "scope": "UNICEF",
                    "startDate": "2022-08-24",
                    "endDate": "2022-08-31",
                    "description": "desc",
                    "budget": "0.00",
                    "administrativeAreasOfImplementation": "",
                    "populationGoal": 0,
                    "frequencyOfPayments": "REGULAR",
                    "sector": "MULTI_PURPOSE",
                    "cashPlus": True,
                    "individualDataNeeded": False,
                    "businessAreaSlug": self.business_area.slug,
                }
            },
        )
        program_id = create_programme_response["data"]["createProgram"]["program"]["id"]

        self.graphql_request(
            request_string=UPDATE_PROGRAM_MUTATION,
            context={"user": self.user},
            variables={
                "programData": {
                    "id": program_id,
                    "status": "ACTIVE",
                },
            },
        )

        create_target_population_response = self.graphql_request(
            request_string=CREATE_TARGET_POPULATION_MUTATION,
            context={"user": self.user},
            variables={
                "input": {
                    "programId": program_id,
                    "name": "TargP",
                    "excludedIds": "",
                    "exclusionReason": "",
                    "businessAreaSlug": self.business_area.slug,
                    "targetingCriteria": {
                        "rules": [
                            {
                                "filters": [
                                    {
                                        "comparisionMethod": "EQUALS",
                                        "arguments": ["True"],
                                        "fieldName": "consent",
                                        "isFlexField": False,
                                    }
                                ],
                                "individualsFiltersBlocks": [],
                            }
                        ]
                    },
                }
            },
        )
        target_population_id = create_target_population_response["data"]["createTargetPopulation"]["targetPopulation"][
            "id"
        ]

        self.graphql_request(
            request_string=APPROVE_TARGET_POPULATION_MUTATION,
            context={"user": self.user},
            variables={
                "id": target_population_id,
            },
        )

        self.graphql_request(
            request_string=FINALIZE_TARGET_POPULATION_MUTATION,
            context={"user": self.user},
            variables={
                "id": target_population_id,
            },
        )
        # TODO: check status in response - READY_FOR_PAYMENT_PLAN

        # TODO: naive datetime
        create_payment_plan_response = self.graphql_request(
            request_string=CREATE_PAYMENT_PLAN_MUTATION,
            context={"user": self.user},
            variables={
                "input": {
                    "businessAreaSlug": self.business_area.slug,
                    "targetingId": target_population_id,
                    "startDate": "2022-08-24",
                    "endDate": "2022-08-31",
                    "dispersionStartDate": "2022-08-24",
                    "dispersionEndDate": "2022-08-31",
                    "currency": "USD",
                }
            },
        )

        assert "errors" not in create_payment_plan_response, create_payment_plan_response
        encoded_payment_plan_id = create_payment_plan_response["data"]["createPaymentPlan"]["paymentPlan"]["id"]

        lock_payment_plan_response = self.graphql_request(
            request_string=PAYMENT_PLAN_ACTION_MUTATION,
            context={"user": self.user},
            variables={
                "input": {
                    "paymentPlanId": encoded_payment_plan_id,
                    "action": "LOCK",
                }
            },
        )
        assert "errors" not in lock_payment_plan_response, lock_payment_plan_response

        rule = RuleFactory(definition="result.value=Decimal('1.3')", name="Rule")
        RuleCommitFactory(rule=rule)

        with patch("hct_mis_api.apps.payment.mutations.payment_plan_apply_steficon") as mock:
            set_steficon_response = self.graphql_request(
                request_string=SET_STEFICON_RULE_MUTATION,
                context={"user": self.user},
                variables={
                    "paymentPlanId": encoded_payment_plan_id,
                    "steficonRuleId": encode_id_base64(rule.id, "Rule"),
                },
            )
            assert "errors" not in set_steficon_response, set_steficon_response
            assert mock.delay.call_count == 1
            call_args = mock.delay.call_args[0]
            payment_plan_apply_steficon(*call_args)

        santander_fsp = FinancialServiceProviderFactory(
            name="Santander",
            delivery_mechanisms=[GenericPayment.DELIVERY_TYPE_CASH, GenericPayment.DELIVERY_TYPE_TRANSFER],
        )
        encoded_santander_fsp_id = encode_id_base64(santander_fsp.id, "FinancialServiceProvider")

        choose_dms_response = self.graphql_request(
            request_string=CHOOSE_DELIVERY_MECHANISMS_MUTATION,
            context={"user": self.user},
            variables=dict(
                input=dict(
                    paymentPlanId=encoded_payment_plan_id,
                    deliveryMechanisms=[
                        GenericPayment.DELIVERY_TYPE_CASH,
                    ],
                )
            ),
        )
        assert "errors" not in choose_dms_response, choose_dms_response

        available_fsps_query_response = self.graphql_request(
            request_string=AVAILABLE_FSPS_FOR_DELIVERY_MECHANISMS_QUERY,
            context={"user": self.user},
            variables={"deliveryMechanisms": [GenericPayment.DELIVERY_TYPE_CASH]},
        )
        assert "errors" not in available_fsps_query_response, available_fsps_query_response
        available_fsps_data = available_fsps_query_response["data"]["availableFspsForDeliveryMechanisms"]
        assert len(available_fsps_data) == 1
        fsps = available_fsps_data[0]["fsps"]
        assert len(fsps) > 0
        assert fsps[0]["name"] == santander_fsp.name

        assign_fsp_mutation_response = self.graphql_request(
            request_string=ASSIGN_FSPS_MUTATION,
            context={"user": self.user},
            variables={
                "paymentPlanId": encoded_payment_plan_id,
                "mappings": [
                    {
                        "deliveryMechanism": GenericPayment.DELIVERY_TYPE_CASH,
                        "fspId": encoded_santander_fsp_id,
                        "order": 1,
                    }
                ],
            },
        )
        assert "errors" not in assign_fsp_mutation_response, assign_fsp_mutation_response

        # set fsp

        # lock fsp

        # ...

        # receive reconciliation info

        # observe that payments have received amounts set
