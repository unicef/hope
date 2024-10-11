from typing import Sequence

from parameterized import parameterized

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.accountability.models import Message
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.household.fixtures import create_household
from hct_mis_api.apps.registration_data.models import RegistrationDataImport
from hct_mis_api.apps.targeting.fixtures import TargetPopulationFactory
from hct_mis_api.apps.targeting.models import HouseholdSelection, TargetPopulation


class TestSampleSizeQuery(APITestCase):
    QUERY_SAMPLE_SIZE = """
    query AccountabilityCommunicationMessageSampleSize($input: GetAccountabilityCommunicationMessageSampleSizeInput!) {
      accountabilityCommunicationMessageSampleSize(input: $input) {
        numberOfRecipients
        sampleSize
      }
    }
    """

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.user = UserFactory(first_name="John", last_name="Wick")
        cls.business_area = create_afghanistan()

        cls.tp = TargetPopulationFactory(business_area=cls.business_area, status=TargetPopulation.STATUS_PROCESSING)
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
        self, _: str, permissions: Sequence[str], sampling_type: Message.SamplingChoices
    ) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        data = {
            "input": {
                "targetPopulation": self.id_to_base64(self.tp.id, "TargetPopulationNode"),
                "samplingType": sampling_type,
                **self.sampling_data[sampling_type],
            },
        }

        self.snapshot_graphql_request(
            request_string=self.QUERY_SAMPLE_SIZE,
            context={"user": self.user, "headers": {"Business-Area": self.business_area.slug}},
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
        self, _: str, permissions: Sequence[str], sampling_type: Message.SamplingChoices
    ) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        data = {
            "input": {
                "households": [self.id_to_base64(household.id, "HouseholdNode") for household in self.households],
                "samplingType": sampling_type,
                **self.sampling_data[sampling_type],
            },
        }
        self.maxDiff = None

        self.snapshot_graphql_request(
            request_string=self.QUERY_SAMPLE_SIZE,
            context={"user": self.user, "headers": {"Business-Area": self.business_area.slug}},
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
        self, _: str, permissions: Sequence[str], sampling_type: Message.SamplingChoices
    ) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        data = {
            "input": {
                "registrationDataImport": self.id_to_base64(self.rdi_id, "RegistrationDataImportNode"),
                "samplingType": sampling_type,
                **self.sampling_data[sampling_type],
            },
        }

        self.snapshot_graphql_request(
            request_string=self.QUERY_SAMPLE_SIZE,
            context={"user": self.user, "headers": {"Business-Area": self.business_area.slug}},
            variables=data,
        )
