import uuid
from typing import Any, Dict
from unittest.mock import MagicMock

from django.utils.dateparse import parse_date

import hct_mis_api.apps.cash_assist_datahub.fixtures as ca_fixtures
import hct_mis_api.apps.cash_assist_datahub.models as ca_models
import hct_mis_api.apps.payment.fixtures as payment_fixtures
from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.cash_assist_datahub.tasks.pull_from_datahub import (
    PullFromDatahubTask,
)
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea, DataCollectingType
from hct_mis_api.apps.core.utils import decode_id_string
from hct_mis_api.apps.household.fixtures import create_household
from hct_mis_api.apps.payment.fixtures import CashPlanFactory
from hct_mis_api.apps.program.models import ProgramCycle


class TestRecalculatingCash(APITestCase):
    databases = (
        "default",
        "cash_assist_datahub_ca",
    )

    CREATE_PROGRAM_MUTATION = """
    mutation CreateProgram($programData: CreateProgramInput!) {
      createProgram(programData: $programData) {
        program {
          id
          name
          status
          startDate
          endDate
          budget
          description
          frequencyOfPayments
          sector
          cashPlus
          populationGoal
          administrativeAreasOfImplementation
          cycles {
            edges {
              node {
                id
                status
              }
            }
          }
        }
        validationErrors
      }
    }
    """

    CREATE_TARGET_POPULATION_MUTATION = """
    mutation CreateTargetPopulation($createTargetPopulationInput: CreateTargetPopulationInput!) {
      createTargetPopulation(input: $createTargetPopulationInput) {
        targetPopulation{
          id
          name
          status
        }
      }
    }
    """

    UPDATE_PROGRAM_MUTATION = """
    mutation UpdateProgram($programData: UpdateProgramInput) {
      updateProgram(programData: $programData) {
        program {
          status
        }
      }
    }
    """

    LOCK_TARGET_POPULATION_MUTATION = """
    mutation LockTP($id: ID!) {
        lockTargetPopulation(id: $id) {
            targetPopulation {
                __typename
            }
            __typename
        }
    }
    """

    FINALIZE_TARGET_POPULATION_MUTATION = """
    mutation FinalizeTP($id: ID!) {
        finalizeTargetPopulation(id: $id) {
            targetPopulation {
                __typename
            }
            __typename
        }
    }
    """

    @classmethod
    def setUpTestData(cls) -> None:
        create_afghanistan()
        payment_fixtures.generate_delivery_mechanisms()
        cls.user = UserFactory.create()
        cls.business_area = BusinessArea.objects.get(slug="afghanistan")

        cls.data_collecting_type = DataCollectingType.objects.create(
            code="full", description="Full individual collected", active=True
        )
        cls.data_collecting_type.limit_to.add(cls.business_area)

        cls.create_program_mutation_variables = {
            "programData": {
                "administrativeAreasOfImplementation": "",
                "budget": "10000.00",
                "businessAreaSlug": "afghanistan",
                "cashPlus": True,
                "description": "",
                "endDate": "2022-07-26",
                "frequencyOfPayments": "ONE_OFF",
                "name": "newprogram",
                "populationGoal": 1,
                "sector": "MULTI_PURPOSE",
                "startDate": "2022-07-25",
                "dataCollectingTypeCode": cls.data_collecting_type.code,
            }
        }

        cls.create_target_population_mutation_variables = lambda program_id, program_cycle_id: {
            "createTargetPopulationInput": {
                "programId": program_id,
                "name": "asdasd",
                "excludedIds": "",
                "exclusionReason": "",
                "businessAreaSlug": "afghanistan",
                "programCycleId": program_cycle_id,
                "targetingCriteria": {
                    "rules": [
                        {
                            "filters": [
                                {
                                    "comparisonMethod": "EQUALS",
                                    "fieldName": "consent",
                                    "flexFieldClassification": "NOT_FLEX_FIELD",
                                    "arguments": [True],
                                }
                            ],
                            "individualsFiltersBlocks": [],
                        }
                    ]
                },
            }
        }

        cls.update_program_mutation_variables = lambda program_id: {
            "programData": {
                "id": program_id,
                "status": "ACTIVE",
            }
        }

    def send_successful_graphql_request(self, **kwargs: Any) -> Dict:
        response = self.graphql_request(**kwargs)
        self.assertTrue("data" in response)  # ensures successful response
        return response

    def create_program(self) -> Dict:
        return self.send_successful_graphql_request(
            request_string=self.CREATE_PROGRAM_MUTATION,
            context={"user": self.user},
            variables=self.create_program_mutation_variables,
        )

    def activate_program(self, program_id: str) -> Dict:
        return self.send_successful_graphql_request(
            request_string=self.UPDATE_PROGRAM_MUTATION,
            context={"user": self.user},
            variables=self.update_program_mutation_variables(program_id),
        )

    def create_target_population(self, program_id: str, program_cycle_id: str) -> Dict:
        return self.send_successful_graphql_request(
            request_string=self.CREATE_TARGET_POPULATION_MUTATION,
            context={"user": self.user},
            variables=self.create_target_population_mutation_variables(program_id, program_cycle_id),
        )

    def lock_target_population(self, target_population_id: str) -> Dict:
        return self.send_successful_graphql_request(
            request_string=self.LOCK_TARGET_POPULATION_MUTATION,
            context={"user": self.user},
            variables={"id": target_population_id},
        )

    def finalize_target_population(self, target_population_id: str) -> Dict:
        return self.send_successful_graphql_request(
            request_string=self.FINALIZE_TARGET_POPULATION_MUTATION,
            context={"user": self.user},
            variables={"id": target_population_id},
        )

    def test_household_cash_received_update(self) -> None:
        self.create_user_role_with_permissions(
            self.user,
            [
                Permissions.PROGRAMME_CREATE,
                Permissions.TARGETING_CREATE,
                Permissions.PROGRAMME_ACTIVATE,
                Permissions.TARGETING_LOCK,
                Permissions.TARGETING_SEND,
            ],
            self.business_area,
        )
        household, _ = create_household(
            {
                "size": 1,
                "residence_status": "HOST",
                "business_area": self.business_area,
                "total_cash_received": None,
                "total_cash_received_usd": None,
            },
        )
        self.assertIsNone(household.total_cash_received)
        self.assertIsNone(household.total_cash_received_usd)

        session = ca_models.Session.objects.create(
            business_area=self.business_area.cash_assist_code, status=ca_models.Session.STATUS_READY
        )

        service_provider_ca_id = uuid.uuid4()
        cash_plan_ca_id = uuid.uuid4()
        payment_fixtures.ServiceProviderFactory.create(ca_id=service_provider_ca_id)

        program_response = self.create_program()
        program_id = program_response["data"]["createProgram"]["program"]["id"]
        program_cycle_id = program_response["data"]["createProgram"]["program"]["cycles"]["edges"][0]["node"]["id"]

        ProgramCycle.objects.filter(id=decode_id_string(program_cycle_id)).update(end_date=parse_date("2033-01-01"))

        self.activate_program(program_id)

        target_population_response = self.create_target_population(program_id, program_cycle_id)
        target_population_id = target_population_response["data"]["createTargetPopulation"]["targetPopulation"]["id"]

        self.lock_target_population(target_population_id)

        self.finalize_target_population(target_population_id)

        cash_amount_1 = 123
        ca_fixtures.PaymentRecordFactory.create(
            session=session,
            service_provider_ca_id=service_provider_ca_id,
            cash_plan_ca_id=cash_plan_ca_id,
            household_mis_id=household.id,
            delivered_quantity=cash_amount_1,
            currency="PLN",
        )

        CashPlanFactory.create(ca_id=cash_plan_ca_id)

        self.assertIsNone(household.total_cash_received)
        self.assertIsNone(household.total_cash_received_usd)

        PullFromDatahubTask(exchange_rates_client=MagicMock()).execute()

        household.refresh_from_db()
        previous_value = household.total_cash_received
        self.assertIsNotNone(household.total_cash_received)
        self.assertIsNotNone(household.total_cash_received_usd)

        session_2 = ca_models.Session.objects.create(
            business_area=self.business_area.cash_assist_code, status=ca_models.Session.STATUS_READY
        )
        cash_amount_2 = 234
        ca_fixtures.PaymentRecordFactory.create(
            session=session_2,
            service_provider_ca_id=service_provider_ca_id,
            cash_plan_ca_id=cash_plan_ca_id,
            household_mis_id=household.id,
            delivered_quantity=cash_amount_2,
            currency="PLN",
        )

        PullFromDatahubTask(exchange_rates_client=MagicMock()).execute()

        household.refresh_from_db()
        self.assertNotEqual(previous_value, household.total_cash_received)
        self.assertEqual(household.total_cash_received, cash_amount_1 + cash_amount_2)
