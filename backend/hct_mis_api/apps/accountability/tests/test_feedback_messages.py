from parameterized import parameterized

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.accountability.factories import (
    FeedbackFactory,
    FeedbackMessageFactory,
)
from hct_mis_api.apps.accountability.models import Feedback
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.geo import models as geo_models
from hct_mis_api.apps.geo.fixtures import AreaFactory, AreaTypeFactory


class TestFeedbackMessages(APITestCase):
    fixtures = ("hct_mis_api/apps/geo/fixtures/data.json",)

    CREATE_FEEDBACK_MESSAGE_MUTATION = """
    mutation CreateFeedbackMessage($input: CreateFeedbackMessageInput!) {
      createFeedbackMessage(input: $input) {
        feedbackMessage {
          description
          createdBy {
            firstName
            lastName
          }
        }
      }
    }
    """

    FEEDBACK_QUERY = """
    query Feedback($id: ID!) {
      feedback(id: $id) {
        id
        issueType
        feedbackMessages {
          edges {
            node {
              id
              description
            }
          }
        }
      }
    }
    """

    @classmethod
    def setUpTestData(cls):
        cls.business_area = create_afghanistan()

        country = geo_models.Country.objects.get(name="Afghanistan")
        area_type = AreaTypeFactory(
            name="Admin type one",
            country=country,
            area_level=2,
        )
        AreaFactory(name="City Test", area_type=area_type, p_code="asdfgfhghkjltr")

        cls.user = UserFactory.create(first_name="John", last_name="Doe")
        cls.feedback = FeedbackFactory(id="1761d020-ead2-489f-95a8-61853fbe568e", issue_type=Feedback.NEGATIVE_FEEDBACK)

    @parameterized.expand(
        [
            (
                "with_permission",
                [Permissions.ACCOUNTABILITY_FEEDBACK_MESSAGE_VIEW_CREATE],
            ),
            ("without_permission", []),
        ]
    )
    def test_create_feedback_message(self, _, permissions):
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)
        self.snapshot_graphql_request(
            request_string=self.CREATE_FEEDBACK_MESSAGE_MUTATION,
            context={"user": self.user},
            variables={
                "input": {
                    "feedback": self.id_to_base64(self.feedback.id, "FeedbackNode"),
                    "description": "You should see this message in snapshot",
                }
            },
        )

    @parameterized.expand(
        [
            (
                "with_permission",
                [Permissions.ACCOUNTABILITY_FEEDBACK_VIEW_DETAILS],
            ),
            ("without_permission", []),
        ]
    )
    def test_feedback_query_shows_feedback_messages(self, _, permissions):
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        FeedbackMessageFactory(
            id="c86d8a58-c4b8-4066-9821-98e236b17742",
            feedback=self.feedback,
            description="Feedback message you see",
            created_by=self.user,
        )

        self.snapshot_graphql_request(
            request_string=self.FEEDBACK_QUERY,
            context={"user": self.user},
            variables={"id": self.id_to_base64(self.feedback.id, "FeedbackNode")},
        )
