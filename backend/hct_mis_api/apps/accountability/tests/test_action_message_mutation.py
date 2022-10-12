from typing import Sequence

from parameterized import parameterized

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.accountability.models import Message
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.household.fixtures import create_household
from hct_mis_api.apps.registration_data.models import RegistrationDataImport
from hct_mis_api.apps.targeting.fixtures import TargetPopulationFactory
from hct_mis_api.apps.targeting.models import HouseholdSelection


class TestActionMessageMutation(APITestCase):
    MUTATION_NEW_MESSAGE = """
    mutation CreateAccountabilityCommunicationMessage($businessArea: String!, $inputs: CreateAccountabilityCommunicationMessageInput!) {
      createAccountabilityCommunicationMessage(businessAreaSlug: $businessArea, inputs: $inputs) {
        message {
          title
          body
          createdBy {
            firstName
          }
          numberOfRecipients
        }
      }
    }
    """

    MUTATION_SAMPLE_SIZE = """
    query AccountabilityCommunicationMessageSampleSize($businessArea: String!, $inputs: GetAccountabilityCommunicationMessageSampleSizeInput!) {
      accountabilityCommunicationMessageSampleSize(businessAreaSlug: $businessArea, inputs: $inputs) {
        numberOfRecipients
        sampleSize
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

        cls.rdi_id = RegistrationDataImport.objects.order_by("?").first().id

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
                [Permissions.ACCOUNTABILITY_COMMUNICATION_MESSAGE_VIEW_CREATE],
                Message.SamplingChoices.FULL_LIST,
            ),
            (
                "with_permission_and_random_tp",
                [Permissions.ACCOUNTABILITY_COMMUNICATION_MESSAGE_VIEW_CREATE],
                Message.SamplingChoices.RANDOM,
            ),
            ("without_permission_full_list_tp", [], Message.SamplingChoices.FULL_LIST),
            ("without_permission_random_tp", [], Message.SamplingChoices.RANDOM),
        )
    )
    def test_get_communication_message_sample_size_for_target_population(
        self, _: str, permissions: Sequence[str], sampling_type: str
    ) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        data = {
            "businessArea": self.business_area.slug,
            "inputs": {
                "targetPopulation": self.tp.id,
                "samplingType": sampling_type,
                **self.sampling_data[sampling_type],
            },
        }

        self.snapshot_graphql_request(
            request_string=self.MUTATION_SAMPLE_SIZE,
            context={"user": self.user},
            variables=data,
        )

    @parameterized.expand(
        (
            (
                "with_permission_and_full_list_households",
                [Permissions.ACCOUNTABILITY_COMMUNICATION_MESSAGE_VIEW_CREATE],
                Message.SamplingChoices.FULL_LIST,
            ),
            (
                "with_permission_and_random_households",
                [Permissions.ACCOUNTABILITY_COMMUNICATION_MESSAGE_VIEW_CREATE],
                Message.SamplingChoices.RANDOM,
            ),
        )
    )
    def test_get_communication_message_sample_size_for_households(
        self, _: str, permissions: Sequence[str], sampling_type: str
    ) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        data = {
            "businessArea": self.business_area.slug,
            "inputs": {
                "households": [household.id for household in self.households],
                "samplingType": sampling_type,
                **self.sampling_data[sampling_type],
            },
        }

        self.snapshot_graphql_request(
            request_string=self.MUTATION_SAMPLE_SIZE,
            context={"user": self.user},
            variables=data,
        )

    @parameterized.expand(
        (
            (
                "with_permission_and_full_list_rdi",
                [Permissions.ACCOUNTABILITY_COMMUNICATION_MESSAGE_VIEW_CREATE],
                Message.SamplingChoices.FULL_LIST,
            ),
            (
                "with_permission_and_random_rdi",
                [Permissions.ACCOUNTABILITY_COMMUNICATION_MESSAGE_VIEW_CREATE],
                Message.SamplingChoices.RANDOM,
            ),
        )
    )
    def test_get_communication_message_sample_size_for_rdi(
        self, _: str, permissions: Sequence[str], sampling_type: str
    ) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        data = {
            "businessArea": self.business_area.slug,
            "inputs": {
                "registration_data_import": self.rdi_id,
                "samplingType": sampling_type,
                **self.sampling_data[sampling_type],
            },
        }

        self.snapshot_graphql_request(
            request_string=self.MUTATION_SAMPLE_SIZE,
            context={"user": self.user},
            variables=data,
        )
