from typing import Any, List

from django.conf import settings

from parameterized import parameterized

from tests.extras.test_utils.factories.account import PartnerFactory, UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from tests.extras.test_utils.factories.accountability import (
    FeedbackFactory,
    FeedbackMessageFactory,
)
from hct_mis_api.apps.accountability.models import Feedback
from hct_mis_api.apps.core.base_test_case import APITestCase
from tests.extras.test_utils.factories.core import create_afghanistan
from hct_mis_api.apps.geo import models as geo_models
from tests.extras.test_utils.factories.geo import AreaFactory, AreaTypeFactory
from tests.extras.test_utils.factories.program import ProgramFactory
from hct_mis_api.apps.program.models import Program


class TestFeedbackMessages(APITestCase):
    fixtures = (f"{settings.PROJECT_ROOT}/apps/geo/fixtures/data.json",)

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
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.business_area = create_afghanistan()
        cls.program = ProgramFactory(status=Program.ACTIVE, business_area=cls.business_area)

        country = geo_models.Country.objects.get(name="Afghanistan")
        area_type = AreaTypeFactory(
            name="Admin type one",
            country=country,
            area_level=2,
        )
        AreaFactory(name="City Test", area_type=area_type, p_code="asdfgfhghkjltr")
        cls.partner = PartnerFactory(name="TestPartner")
        cls.user = UserFactory.create(first_name="John", last_name="Doe", partner=cls.partner)

        cls.feedback = FeedbackFactory(id="1761d020-ead2-489f-95a8-61853fbe568e", issue_type=Feedback.NEGATIVE_FEEDBACK)
        cls.update_partner_access_to_program(cls.partner, cls.program)

    @parameterized.expand(
        [
            (
                "with_permission",
                [Permissions.GRIEVANCES_FEEDBACK_MESSAGE_VIEW_CREATE],
            ),
            ("without_permission", []),
        ]
    )
    def test_create_feedback_message(self, _: Any, permissions: List[Permissions]) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area, self.program)
        self.snapshot_graphql_request(
            request_string=self.CREATE_FEEDBACK_MESSAGE_MUTATION,
            context={
                "user": self.user,
                "headers": {
                    "Business-Area": self.business_area.slug,
                    "Program": self.id_to_base64(self.program.id, "ProgramNode"),
                },
            },
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
                [Permissions.GRIEVANCES_FEEDBACK_VIEW_DETAILS],
            ),
            ("without_permission", []),
        ]
    )
    def test_feedback_query_shows_feedback_messages(self, _: Any, permissions: List[Permissions]) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area, self.program)

        FeedbackMessageFactory(
            id="c86d8a58-c4b8-4066-9821-98e236b17742",
            feedback=self.feedback,
            description="Feedback message you see",
            created_by=self.user,
        )

        self.snapshot_graphql_request(
            request_string=self.FEEDBACK_QUERY,
            context={
                "user": self.user,
                "headers": {
                    "Business-Area": self.business_area.slug,
                    "Program": self.id_to_base64(self.program.id, "ProgramNode"),
                },
            },
            variables={"id": self.id_to_base64(self.feedback.id, "FeedbackNode")},
        )
