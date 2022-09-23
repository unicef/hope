from hct_mis_api.apps.registration_data.fixtures import RegistrationDataImportFactory
from hct_mis_api.apps.household.fixtures import create_household_and_individuals
from hct_mis_api.apps.core.utils import encode_id_base64
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
        cls.registration_data_import = RegistrationDataImportFactory(business_area=cls.business_area)
        cls.household, cls.individuals = create_household_and_individuals(
            household_data={
                "registration_data_import": cls.registration_data_import,
                "business_area": cls.business_area,
            },
            individuals_data=[{}],
        )

    def create_dummy_correct_input(self):
        return {
            "businessAreaSlug": self.business_area.slug,
            "issueType": Feedback.POSITIVE_FEEDBACK,
        }

    def create_new_feedback(self, data=None):
        current_amount = Feedback.objects.count()
        response = self.graphql_request(
            request_string=self.CREATE_NEW_FEEDBACK_MUTATION,
            context={"user": self.user},
            variables={"input": data if data else self.create_dummy_correct_input()},
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

    def test_optional_household_lookup(self):
        self.assertEqual(Feedback.objects.count(), 0)
        data = self.create_dummy_correct_input() | {
            "householdLookup": encode_id_base64(self.household.pk, "Household"),
        }
        response = self.graphql_request(
            request_string=self.CREATE_NEW_FEEDBACK_MUTATION,
            context={"user": self.user},
            variables={"input": data},
        )
        assert "errors" not in response, response
        self.assertEqual(Feedback.objects.count(), 1)

        feedback = Feedback.objects.first()
        self.assertEqual(feedback.household_lookup, self.household)

    def test_optional_individual_lookup(self):
        self.assertEqual(Feedback.objects.count(), 0)
        data = self.create_dummy_correct_input() | {
            "individualLookup": encode_id_base64(self.individuals[0].pk, "Individual"),
        }
        response = self.graphql_request(
            request_string=self.CREATE_NEW_FEEDBACK_MUTATION,
            context={"user": self.user},
            variables={"input": data},
        )
        assert "errors" not in response, response
        self.assertEqual(Feedback.objects.count(), 1)

        feedback = Feedback.objects.first()
        self.assertEqual(feedback.individual_lookup, self.individuals[0])
