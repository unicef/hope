from parameterized import parameterized

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.communication.models import Message
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.household.fixtures import create_household
from hct_mis_api.apps.targeting.fixtures import TargetPopulationFactory
from hct_mis_api.apps.targeting.models import HouseholdSelection


class TestActionMessageMutation(APITestCase):
    MUTATION = """
    mutation CreateCommunicationMessage($businessArea: String!, $inputs: CreateCommunicationMessageInput!) {
      createCommunicationMessage(businessAreaSlug: $businessArea, inputs: $inputs) {
        message {
          title
          unicefId
          body
          createdBy {
            firstName
          }
          numberOfRecipients
        }
      }
    }
    """

    @classmethod
    def setUpTestData(cls):
        create_afghanistan()
        cls.user = UserFactory(first_name="John", last_name="Wick")
        cls.business_area = BusinessArea.objects.get(slug="afghanistan")

        cls.tp = TargetPopulationFactory(business_area=cls.business_area)
        cls.households = [create_household()[0] for _ in range(4)]
        HouseholdSelection.objects.bulk_create(
            [HouseholdSelection(household=household, target_population=cls.tp) for household in cls.households]
        )

        for household in cls.households:
            print("HoH DOB: ", household.head_of_household.birth_date)

        cls.sampling_data = {
            Message.SamplingChoices.FULL_LIST: {
                "fullListArguments": {
                    "excludedAdminAreas": [],
                },
            },
            Message.SamplingChoices.RANDOM: {
                "randomSamplingArguments": {
                    "age": {"min": 20, "max": 80},
                    # "sex": MALE,
                    "confidenceInterval": 0.8,
                    "marginOfError": 80,
                    "excludedAdminAreas": [],
                },
            },
        }

    @parameterized.expand(
        (
            (
                "with_permission_and_full_list_tp",
                [Permissions.COMMUNICATION_MESSAGE_VIEW_CREATE],
                Message.SamplingChoices.FULL_LIST,
                "targetPopulation",
            ),
            (
                "with_permission_and_random_tp",
                [Permissions.COMMUNICATION_MESSAGE_VIEW_CREATE],
                Message.SamplingChoices.RANDOM,
                "targetPopulation",
            ),
            (
                "with_permission_and_full_list_households",
                [Permissions.COMMUNICATION_MESSAGE_VIEW_CREATE],
                Message.SamplingChoices.FULL_LIST,
                "households",
            ),
            (
                "with_permission_and_random_households",
                [Permissions.COMMUNICATION_MESSAGE_VIEW_CREATE],
                Message.SamplingChoices.RANDOM,
                "households",
            ),
            (
                "with_permission_and_full_list_rdi",
                [Permissions.COMMUNICATION_MESSAGE_VIEW_CREATE],
                Message.SamplingChoices.FULL_LIST,
                "registration_data_import",
            ),
            (
                "with_permission_and_random_rdi",
                [Permissions.COMMUNICATION_MESSAGE_VIEW_CREATE],
                Message.SamplingChoices.RANDOM,
                "registration_data_import",
            ),
            ("without_permission_full_list_tp", [], Message.SamplingChoices.FULL_LIST, "targetPopulation"),
            ("without_permission_random_tp", [], Message.SamplingChoices.RANDOM, "targetPopulation"),
        )
    )
    def test_create_communication_message(
        self, name: str, permissions: list[str], sampling_type: str, look_up_with: str
    ) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        data = {
            "businessArea": self.business_area.slug,
            "inputs": {
                "title": f"{sampling_type} message title",
                "body": f"{sampling_type} message body",
                look_up_with: self.tp.id
                if look_up_with == "targetPopulation"
                else [household.id for household in self.households],
                "samplingType": sampling_type,
                **self.sampling_data[sampling_type],
            },
        }

        self.snapshot_graphql_request(
            request_string=self.MUTATION,
            context={"user": self.user},
            variables=data,
        )
