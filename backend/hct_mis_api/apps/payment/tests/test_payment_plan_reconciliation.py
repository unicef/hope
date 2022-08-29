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
from hct_mis_api.apps.core.utils import encode_id_base64
from hct_mis_api.apps.steficon.fixtures import RuleFactory
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
      name
      status
      startDate
      endDate
      caId
      budget
      description
      frequencyOfPayments
      sector
      scope
      cashPlus
      populationGoal
      individualDataNeeded
      __typename
    }
    validationErrors
    __typename
  }
}
"""

UPDATE_PROGRAM_MUTATION = """
mutation UpdateProgram($programData: UpdateProgramInput!) {
  updateProgram(programData: $programData) {
    program {
      id
      name
      startDate
      endDate
      status
      caId
      description
      budget
      frequencyOfPayments
      cashPlus
      populationGoal
      scope
      sector
      totalNumberOfHouseholds
      administrativeAreasOfImplementation
      individualDataNeeded
      __typename
    }
    validationErrors
    __typename
  }
}
"""


CREATE_TARGET_POPULATION_MUTATION = """
mutation CreateTP($input: CreateTargetPopulationInput!) {
  createTargetPopulation(input: $input) {
    targetPopulation {
      id
      status
      candidateListTotalHouseholds
      candidateListTotalIndividuals
      finalListTotalHouseholds
      finalListTotalIndividuals
      __typename
    }
    validationErrors
    __typename
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


# UPDATE_PAYMENT_PLAN_MUTATION = """
# mutation UpdatePaymentPlan($input: UpdatePaymentPlanInput!) {
#     updatePaymentPlan(input: $input) {
#         paymentPlan {
#             id
#         }
#     }
# }
# """


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

    def test_receiving_reconciliations_from_fsp(self):
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
        payment_plan_id = create_payment_plan_response["data"]["createPaymentPlan"]["paymentPlan"]["id"]

        rule = RuleFactory(definition="result.value=Decimal('1.3')", name="Rule")

        # patch calling payment_plan_apply_steficon.delay
        print("STEFICON", payment_plan_id, rule.id)
        with patch("hct_mis_api.apps.payment.celery_tasks.payment_plan_apply_steficon") as mock:
            response = self.graphql_request(
                request_string=SET_STEFICON_RULE_MUTATION,
                context={"user": self.user},
                variables={
                    "paymentPlanId": payment_plan_id,
                    "steficonRuleId": encode_id_base64(rule.id, "Rule"),
                },
            )
            print("R", response)
            print(mock)
            print(mock.delay)
            pass

        print("FSP")
        # set fsp

        # lock fsp

        # ...

        # receive reconciliation info

        # observe that payments have received amounts set
