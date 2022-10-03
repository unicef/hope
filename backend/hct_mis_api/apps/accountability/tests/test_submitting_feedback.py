from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.accountability.models import Feedback
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.core.utils import decode_id_string, encode_id_base64
from hct_mis_api.apps.geo import models as geo_models
from hct_mis_api.apps.geo.fixtures import AreaFactory, AreaTypeFactory, CountryFactory
from hct_mis_api.apps.grievance.models import GrievanceTicket
from hct_mis_api.apps.household.fixtures import create_household_and_individuals
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.registration_data.fixtures import RegistrationDataImportFactory


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
    $feedbackId: String,
    $createdBy: String,
) {
    allFeedbacks(
        businessAreaSlug: $businessAreaSlug,
        issueType: $issueType,
        feedbackId: $feedbackId,
        createdBy: $createdBy,
    ) {
        edges {
            node {
                id
            }
        }
    }
}
"""

    UPDATE_FEEDBACK_MUTATION = """
mutation updateFeedback($input: UpdateFeedbackInput!) {
    updateFeedback(input: $input) {
        feedback {
            id
        }
    }
}
"""

    SINGLE_FEEDBACK_QUERY = """
query feedback($id: ID!) {
    feedback(id: $id) {
        id
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
                Permissions.ACCOUNTABILITY_FEEDBACK_VIEW_UPDATE,
                Permissions.GRIEVANCES_CREATE,
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

        country = geo_models.Country.objects.create(name="Afghanistan")
        cls.area_type = AreaTypeFactory(
            name="Test Area Type",
            country=country,
            area_level=2,
        )
        cls.admin_area = AreaFactory(name="City Test", area_type=cls.area_type, p_code="asdfgfhghkjltr")

    def create_dummy_correct_input(self):
        return {
            "businessAreaSlug": self.business_area.slug,
            "issueType": Feedback.POSITIVE_FEEDBACK,
            "description": "Test description",
        }

    def submit_feedback(self, data):
        amount = Feedback.objects.count()
        response = self.graphql_request(
            request_string=self.CREATE_NEW_FEEDBACK_MUTATION,
            context={"user": self.user},
            variables={"input": data},
        )
        assert "errors" not in response, response
        self.assertEqual(Feedback.objects.count(), amount + 1)
        return decode_id_string(response["data"]["createFeedback"]["feedback"]["id"])

    def create_new_feedback(self, data=None):
        return self.submit_feedback(data or self.create_dummy_correct_input())

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

        assert len(filter_it({"feedbackId": self.program.pk})) == 0
        assert len(filter_it({"feedbackId": Feedback.objects.first().unicef_id})) == 1

        assert len(filter_it({"createdBy": str(self.user.pk)})) == 1
        assert len(filter_it({"createdBy": str(self.program.pk)})) == 0

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

    def test_updating_feedback(self):
        feedback_id = self.create_new_feedback()
        feedback = Feedback.objects.get(id=feedback_id)
        self.assertEqual(feedback.issue_type, Feedback.POSITIVE_FEEDBACK)
        response = self.graphql_request(
            request_string=self.UPDATE_FEEDBACK_MUTATION,
            context={"user": self.user},
            variables={
                "input": {
                    "feedbackId": encode_id_base64(feedback.pk, "Feedback"),
                    "issueType": Feedback.NEGATIVE_FEEDBACK,
                }
            },
        )
        assert "errors" not in response, response["errors"]
        feedback.refresh_from_db()
        self.assertEqual(feedback.issue_type, Feedback.NEGATIVE_FEEDBACK)

    def test_getting_single_feedback(self):
        feedback_id = self.create_new_feedback()
        response = self.graphql_request(
            request_string=self.SINGLE_FEEDBACK_QUERY,
            context={"user": self.user},
            variables={"id": encode_id_base64(feedback_id, "Feedback")},
        )
        assert "errors" not in response, response["errors"]
        self.assertEqual(response["data"]["feedback"]["id"], encode_id_base64(feedback_id, "Feedback"))

    def test_linking_feedback_to_grievance_ticket(self):
        feedback_id = self.create_new_feedback()

        create_grievance_mutation = """
mutation CreateGrievanceTicket($input: CreateGrievanceTicketInput!) {
    createGrievanceTicket(input: $input) {
        grievanceTickets {
            id
            feedback {
                id
            }
        }
    }
}
"""
        create_grievance_response = self.graphql_request(
            request_string=create_grievance_mutation,
            context={"user": self.user},
            variables={
                "input": {
                    "description": "Test Feedback",
                    "assignedTo": self.id_to_base64(self.user.id, "UserNode"),
                    "category": GrievanceTicket.CATEGORY_SYSTEM_FLAGGING,
                    "admin": self.admin_area.p_code,
                    "language": "Polish, English",
                    "consent": True,
                    "businessArea": "afghanistan",
                    "linkedFeedbackId": feedback_id,
                }
            },
        )
        assert "errors" not in create_grievance_response, create_grievance_response["errors"]
        grievance_data = create_grievance_response["data"]["createGrievanceTicket"]["grievanceTickets"][0]
        received_grievance_id = decode_id_string(grievance_data["id"])
        received_feedback_id = decode_id_string(grievance_data["feedback"]["id"])
        feedback = Feedback.objects.get(id=feedback_id)
        self.assertEqual(
            str(
                feedback.linked_grievance.id,
            ),
            received_grievance_id,
        )
        self.assertEqual(str(feedback.id), received_feedback_id)

    def test_individuals_lookup_household_matching_household_lookup(self):
        self.other_household, self.other_individuals = create_household_and_individuals(
            household_data={
                "registration_data_import": self.registration_data_import,
                "business_area": self.business_area,
            },
            individuals_data=[{}],
        )

        amount = Feedback.objects.count()
        response = self.graphql_request(
            request_string=self.CREATE_NEW_FEEDBACK_MUTATION,
            context={"user": self.user},
            variables={
                "input": self.create_dummy_correct_input()
                | {
                    "householdLookup": encode_id_base64(self.household.pk, "Household"),
                    "individualLookup": encode_id_base64(self.other_individuals[0].pk, "Individual"),
                }
            },
        )
        assert "errors" in response, response
        self.assertEqual(Feedback.objects.count(), amount)
