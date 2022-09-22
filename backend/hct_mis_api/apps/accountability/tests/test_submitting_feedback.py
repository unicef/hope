from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.accountability.models import Feedback
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea

# the scenario goes like this:
# - "save" button (mutation - create)
# - "edit" button and then save (mutation - update)

# all_feedbacks_query
# - filters
# - columns and sorting

# create feedback message - txt, timestamp, user


class TestFeedback(APITestCase):
    CREATE_NEW_FEEDBACK_MUTATION = """
mutation createFeedback($input: CreateFeedbackInput!) {
    createFeedback(input: $input) {
        feedback {
            id
        }
    }
}
"""

    ALL_FEEDBACKS_QUERY = """
query allFeedbacks($businessAreaSlug: String!) {
    allFeedbacks(businessAreaSlug: $businessAreaSlug) {
        edges {
            node {
                id
            }
        }
    }
}
"""

    @classmethod
    def setUpTestData(cls):
        create_afghanistan()
        cls.business_area = BusinessArea.objects.get(slug="afghanistan")
        cls.user = UserFactory.create()
        cls.create_user_role_with_permissions(
            cls.user,
            [
                Permissions.ACCOUNTABILITY_FEEDBACK_VIEW_CREATE,
                Permissions.ACCOUNTABILITY_FEEDBACK_VIEW_LIST,
            ],
            cls.business_area,
        )

    def create_dummy_correct_input(self):
        return {
            "businessAreaSlug": self.business_area.slug,
            "issueType": Feedback.POSITIVE_FEEDBACK,
        }

    def create_new_feedback(self):
        current_amount = Feedback.objects.count()
        response = self.graphql_request(
            request_string=self.CREATE_NEW_FEEDBACK_MUTATION,
            context={"user": self.user},
            variables={"input": self.create_dummy_correct_input()},
        )
        assert "errors" not in response, response["errors"]
        self.assertEqual(Feedback.objects.count(), current_amount + 1)

    def test_creating_new_feedback(self):
        self.create_new_feedback()

    def test_getting_all_feedbacks(self):
        self.create_new_feedback()
        # TODO
        # response = self.graphql_request(
        #     request_string=self.ALL_FEEDBACKS_QUERY,
        #     context={"user": self.user},
        #     variables={
        #         "businessArea": self.business_area,
        #     },
        # )
        # assert "errors" not in response, response["errors"]
        # self.assertEqual(len(response["data"]["allFeedbacks"]["edges"]), 1)

    def test_filtering_feedbacks(self):
        pass  # TODO

    def test_failing_to_create_new_feedback(self):
        def expect_failure(data):
            current_amount = Feedback.objects.count()
            response = self.graphql_request(
                request_string=self.CREATE_NEW_FEEDBACK_MUTATION,
                context={"user": self.user},
                variables={"input": data},
            )
            assert "errors" in response, response
            self.assertEqual(Feedback.objects.count(), current_amount)

        # missing business area slug
        expect_failure(
            {
                "issueType": Feedback.POSITIVE_FEEDBACK,
            }
        )

        # missing issue type
        expect_failure(
            {
                "businessAreaSlug": self.business_area.slug,
            }
        )
