from parameterized import parameterized

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.accountability.models import Survey
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.household.fixtures import create_household
from hct_mis_api.apps.targeting.fixtures import TargetPopulationFactory


class TestCreateCommunicationMessage(APITestCase):
    MUTATION = """
mutation CreateAccountabilityCommunicationMessage (
  $input: CreateAccountabilityCommunicationMessageInput!
) {
  createAccountabilityCommunicationMessage (
    input: $input
  ) {
    message {
      title
      body
      createdBy {
        firstName
        lastName
      }
      households {
        totalCount
      }
      targetPopulation {
        totalFamilySize
      }
      registrationDataImport {
        name
        status
      }
      fullListArguments
      randomSamplingArguments
      sampleSize
    }
  }
}
    """

    @classmethod
    def setUpTestData(cls) -> None:
        cls.business_area = create_afghanistan()
        cls.user = UserFactory(first_name="John", last_name="Wick")
        cls.target_population = TargetPopulationFactory(business_area=cls.business_area)

        cls.households = [create_household()[0] for _ in range(14)]
        cls.target_population.households.set(cls.households)

        cls.sampling_data = {
            Survey.SAMPLING_FULL_LIST: {
                "fullListArguments": {
                    "excludedAdminAreas": [],
                },
            },
            Survey.SAMPLING_RANDOM: {
                "randomSamplingArguments": {
                    "age": {"min": 20, "max": 80},
                    # "sex": MALE,
                    "confidenceInterval": 0.8,
                    "marginOfError": 80,
                    "excludedAdminAreas": [],
                },
            },
        }

    def test_create_accountability_communication_message_without_permission(self) -> None:
        self.create_user_role_with_permissions(self.user, [], self.business_area)

        self.snapshot_graphql_request(
            request_string=self.MUTATION,
            context={"user": self.user, "headers": {"Business-Area": self.business_area.slug}},
            variables={
                "input": {
                    "title": "Test message",
                    "body": "Test body",
                    "targetPopulation": self.id_to_base64(self.target_population.id, "TargetPopulationNode"),
                    "samplingType": Survey.SAMPLING_FULL_LIST,
                    **self.sampling_data[Survey.SAMPLING_FULL_LIST],
                },
            },
        )

    @parameterized.expand(
        [
            (Survey.SAMPLING_FULL_LIST,),
            (Survey.SAMPLING_RANDOM,),
        ]
    )
    def test_create_accountability_communication_message_by_target_population(self, sampling_type: str) -> None:
        self.create_user_role_with_permissions(
            self.user, [Permissions.ACCOUNTABILITY_COMMUNICATION_MESSAGE_VIEW_CREATE], self.business_area
        )

        self.snapshot_graphql_request(
            request_string=self.MUTATION,
            context={"user": self.user, "headers": {"Business-Area": self.business_area.slug}},
            variables={
                "input": {
                    "title": "Test message",
                    "body": "Test body",
                    "targetPopulation": self.id_to_base64(self.target_population.id, "TargetPopulationNode"),
                    "samplingType": sampling_type,
                    **self.sampling_data[sampling_type],
                },
            },
        )

    @parameterized.expand(
        [
            (Survey.SAMPLING_FULL_LIST,),
            (Survey.SAMPLING_RANDOM,),
        ]
    )
    def test_create_accountability_communication_message_by_households(self, sampling_type: str) -> None:
        self.create_user_role_with_permissions(
            self.user, [Permissions.ACCOUNTABILITY_COMMUNICATION_MESSAGE_VIEW_CREATE], self.business_area
        )

        self.snapshot_graphql_request(
            request_string=self.MUTATION,
            context={"user": self.user, "headers": {"Business-Area": self.business_area.slug}},
            variables={
                "input": {
                    "title": "Test message",
                    "body": "Test body",
                    "households": [self.id_to_base64(hh.id, "HouseholdNode") for hh in self.households],
                    "samplingType": sampling_type,
                    **self.sampling_data[sampling_type],
                },
            },
        )
