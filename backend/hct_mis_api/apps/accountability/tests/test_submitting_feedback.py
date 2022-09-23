from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.registration_data.fixtures import RegistrationDataImportFactory
from hct_mis_api.apps.household.fixtures import create_household_and_individuals
from hct_mis_api.apps.core.utils import encode_id_base64
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.accountability.models import Feedback
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.geo import models as geo_models
from hct_mis_api.apps.geo.fixtures import CountryFactory


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
query allFeedbacks(
    $businessAreaSlug: String!,
    $issueType: String,
    $createdBy: String,
    $feedbackId: String,
) {
    allFeedbacks(
        businessAreaSlug: $businessAreaSlug,
        issueType: $issueType,
        createdBy: $createdBy,
        feedbackId: $feedbackId,
    ) {
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
        cls.program = ProgramFactory(
            business_area=cls.business_area,
            name="Test Program",
        )

    def create_dummy_correct_input(self):
        return {
            "businessAreaSlug": self.business_area.slug,
            "issueType": Feedback.POSITIVE_FEEDBACK,
            "description": "Test description",
            "createdBy": encode_id_base64(self.user.pk, "User"),
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
        response = self.graphql_request(
            request_string=self.ALL_FEEDBACKS_QUERY,
            context={"user": self.user},
            variables={
                "businessAreaSlug": self.business_area.slug,
            },
        )
        assert "errors" not in response, response["errors"]
        self.assertEqual(len(response["data"]["allFeedbacks"]["edges"]), 1)

    def test_filtering_feedbacks(self):
        self.create_new_feedback(
            data=self.create_dummy_correct_input()
            | {
                "householdLookup": encode_id_base64(self.household.pk, "Household"),
                "individualLookup": encode_id_base64(self.individuals[0].pk, "Individual"),
                "program": encode_id_base64(self.program.pk, "Program"),
            }
        )

        def filter_it(variables):
            vars = {"businessAreaSlug": self.business_area.slug} | variables
            response = self.graphql_request(
                request_string=self.ALL_FEEDBACKS_QUERY,
                context={"user": self.user},
                variables=vars,
            )
            assert "errors" not in response, response["errors"]
            return response["data"]["allFeedbacks"]["edges"]

        assert len(filter_it({"businessAreaSlug": "non-existent"})) == 0
        assert len(filter_it({"businessAreaSlug": self.business_area.slug})) == 1

        assert len(filter_it({"issueType": Feedback.NEGATIVE_FEEDBACK})) == 0
        assert len(filter_it({"issueType": Feedback.POSITIVE_FEEDBACK})) == 1

        assert len(filter_it({"createdBy": encode_id_base64(self.program.pk, "Program")})) == 0
        assert len(filter_it({"createdBy": encode_id_base64(self.user.pk, "User")})) == 1

        assert len(filter_it({"feedbackId": encode_id_base64(self.program.pk, "Program")})) == 0
        assert len(filter_it({"feedbackId": encode_id_base64(Feedback.objects.first().unicef_id, "Feedback")})) == 1

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
                "description": "Test description",
            }
        )

        # missing issue type
        expect_failure(
            {
                "businessAreaSlug": self.business_area.slug,
                "description": "Test description",
            }
        )

        # missing description
        expect_failure(
            {
                "businessAreaSlug": self.business_area.slug,
                "issueType": Feedback.POSITIVE_FEEDBACK,
            }
        )

    def submit_feedback(self, data):
        amount = Feedback.objects.count()
        response = self.graphql_request(
            request_string=self.CREATE_NEW_FEEDBACK_MUTATION,
            context={"user": self.user},
            variables={"input": data},
        )
        assert "errors" not in response, response
        self.assertEqual(Feedback.objects.count(), amount + 1)

    def test_optional_household_lookup(self):
        data = self.create_dummy_correct_input() | {
            "householdLookup": encode_id_base64(self.household.pk, "Household"),
        }
        self.submit_feedback(data)
        feedback = Feedback.objects.first()
        self.assertEqual(feedback.household_lookup, self.household)

    def test_optional_individual_lookup(self):
        data = self.create_dummy_correct_input() | {
            "individualLookup": encode_id_base64(self.individuals[0].pk, "Individual"),
        }
        self.submit_feedback(data)
        self.assertEqual(Feedback.objects.count(), 1)
        feedback = Feedback.objects.first()
        self.assertEqual(feedback.individual_lookup, self.individuals[0])

    def test_optional_comments(self):
        data = self.create_dummy_correct_input() | {
            "comments": "Test comments",
        }
        self.submit_feedback(data)
        feedback = Feedback.objects.first()
        self.assertEqual(feedback.comments, "Test comments")

    # TODO
    # def test_optional_linked_grievance(self):
    #     pass

    def test_optional_program(self):
        data = self.create_dummy_correct_input() | {
            "program": encode_id_base64(self.program.pk, "Program"),
        }
        self.submit_feedback(data)
        feedback = Feedback.objects.first()
        self.assertEqual(feedback.program, self.program)

    def test_optional_language(self):
        data = self.create_dummy_correct_input() | {
            "language": "en",
        }
        self.submit_feedback(data)
        feedback = Feedback.objects.first()
        self.assertEqual(feedback.language, "en")

    def test_optional_area(self):
        data = self.create_dummy_correct_input() | {
            "area": "Test area",
        }
        self.submit_feedback(data)
        feedback = Feedback.objects.first()
        self.assertEqual(feedback.area, "Test area")

    def test_optional_admin2(self):
        country = CountryFactory()
        area_type = geo_models.AreaType.objects.create(name="X", area_level=1, country=country)
        admin2 = geo_models.Area.objects.create(p_code="SO25", name="SO25", area_type=area_type)
        data = self.create_dummy_correct_input() | {
            "admin2": encode_id_base64(admin2.pk, "Area"),
        }
        self.submit_feedback(data)
        feedback = Feedback.objects.first()
        self.assertEqual(feedback.admin2, admin2)
