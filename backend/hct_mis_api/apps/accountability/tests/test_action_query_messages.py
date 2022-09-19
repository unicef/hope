from typing import Callable, Union

from parameterized import parameterized

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.account.models import User
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.accountability.fixtures import CommunicationMessageFactory
from hct_mis_api.apps.accountability.models import Message
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.core.utils import encode_id_base64
from hct_mis_api.apps.household.fixtures import create_household
from hct_mis_api.apps.targeting.fixtures import TargetPopulationFactory
from hct_mis_api.apps.targeting.models import HouseholdSelection


class TestActionMessageMutation(APITestCase):
    QUERY = """
    query AllCommunicationMessages($businessArea: String! $title: String, $body: String, $samplingType: String, $createdBy: String, $numberOfRecipients: Int, $numberOfRecipients_Gte: Int, $numberOfRecipients_Lte: Int, $orderBy: String,) {
      allCommunicationMessages (businessArea: $businessArea, title: $title, body: $body, samplingType: $samplingType, createdBy: $createdBy, numberOfRecipients: $numberOfRecipients, numberOfRecipients_Gte: $numberOfRecipients_Gte, numberOfRecipients_Lte: $numberOfRecipients_Lte, orderBy: $orderBy) {
        edges {
          node {
            id
            title
            unicefId
            body
            createdBy {
              firstName
              lastName
            }
            numberOfRecipients
          }
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
        households = [create_household()[0] for _ in range(14)]
        HouseholdSelection.objects.bulk_create(
            [HouseholdSelection(household=household, target_population=cls.tp) for household in households]
        )

        CommunicationMessageFactory.create_batch(
            10, business_area=cls.business_area, target_population=cls.tp, created_by=cls.user
        )
        CommunicationMessageFactory(
            title="You got credit of USD 400",
            body="Greetings, we have sent you USD 400 in your registered account on 2022-09-19 20:00:00 UTC",
            business_area=cls.business_area,
            target_population=cls.tp,
            created_by=cls.user,
        )

    @parameterized.expand(
        (
            (
                "with_list_permission_full_sampling",
                [Permissions.ACCOUNTABILITY_COMMUNICATION_MESSAGE_VIEW_LIST],
                {
                    "samplingType": Message.SamplingChoices.FULL_LIST,
                },
            ),
            (
                "with_list_permission_random_sampling",
                [Permissions.ACCOUNTABILITY_COMMUNICATION_MESSAGE_VIEW_LIST],
                {
                    "samplingType": Message.SamplingChoices.RANDOM,
                },
            ),
            (
                "with_list_permission_title",
                [Permissions.ACCOUNTABILITY_COMMUNICATION_MESSAGE_VIEW_LIST],
                {
                    "title": "got credit",
                },
            ),
            (
                "with_list_permission_title",
                [Permissions.ACCOUNTABILITY_COMMUNICATION_MESSAGE_VIEW_LIST],
                {
                    "body": "we have sent you USD",
                },
            ),
            (
                "with_list_permission_numberOfRecipients",
                [Permissions.ACCOUNTABILITY_COMMUNICATION_MESSAGE_VIEW_LIST],
                {
                    "numberOfRecipients_Gte": 2,
                },
            ),
            (
                "with_list_permission_createdBy",
                [Permissions.ACCOUNTABILITY_COMMUNICATION_MESSAGE_VIEW_LIST],
                lambda u: {
                    "createdBy": encode_id_base64(u.id, "User"),
                },
            ),
            ("with_view_details_permission", [Permissions.ACCOUNTABILITY_COMMUNICATION_MESSAGE_VIEW_DETAILS], {}),
            (
                "with_view_details_as_creator_permission",
                [Permissions.ACCOUNTABILITY_COMMUNICATION_MESSAGE_VIEW_DETAILS_AS_CREATOR],
                {},
            ),
            ("without_permission", [], {}),
        )
    )
    def test_list_communication_messages(
        self, _: str, permissions: list[str], extra_filters: Union[Callable[[User], dict], dict]
    ) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        self.snapshot_graphql_request(
            request_string=self.QUERY,
            context={"user": self.user},
            variables={
                "businessArea": self.business_area.slug,
                **(extra_filters(self.user) if callable(extra_filters) else extra_filters),
            },
        )
