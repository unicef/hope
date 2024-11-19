from typing import Dict, List, Optional

from hct_mis_api.apps.account.fixtures import PartnerFactory, UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.accountability.models import Feedback
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.core.utils import (
    decode_id_string,
    decode_id_string_required,
    encode_id_base64,
)
from hct_mis_api.apps.geo import models as geo_models
from hct_mis_api.apps.geo.fixtures import AreaFactory, AreaTypeFactory, CountryFactory
from hct_mis_api.apps.grievance.models import GrievanceTicket
from hct_mis_api.apps.household.fixtures import create_household_and_individuals
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.program.models import Program
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
    $issueType: String,
    $feedbackId: String,
    $createdBy: String,
    $orderBy: String,
) {
    allFeedbacks(
        issueType: $issueType,
        feedbackId: $feedbackId,
        createdBy: $createdBy,
        orderBy: $orderBy,
    ) {
        edges {
            node {
                id
                issueType
                linkedGrievance {
                    id
                }
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

    CREATE_GRIEVANCE_MUTATION = """
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

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        create_afghanistan()
        cls.business_area = BusinessArea.objects.get(slug="afghanistan")
        partner = PartnerFactory(name="Partner")
        cls.user = UserFactory.create(partner=partner)
        cls.create_user_role_with_permissions(
            cls.user,
            [
                Permissions.GRIEVANCES_FEEDBACK_VIEW_CREATE,
                Permissions.GRIEVANCES_FEEDBACK_VIEW_LIST,
                Permissions.GRIEVANCES_FEEDBACK_VIEW_UPDATE,
                Permissions.GRIEVANCES_CREATE,
            ],
            cls.business_area,
        )
        cls.program = ProgramFactory(business_area=cls.business_area, name="Test Program", status=Program.ACTIVE)
        cls.registration_data_import = RegistrationDataImportFactory(
            business_area=cls.business_area, program=cls.program
        )
        cls.household, cls.individuals = create_household_and_individuals(
            household_data={
                "registration_data_import": cls.registration_data_import,
                "business_area": cls.business_area,
                "program": cls.program,
            },
            individuals_data=[{}],
        )
        cls.update_partner_access_to_program(partner, cls.program)

        country = geo_models.Country.objects.create(name="Afghanistan")
        cls.area_type = AreaTypeFactory(
            name="Test Area Type",
            country=country,
            area_level=2,
        )
        cls.admin_area = AreaFactory(name="City Test", area_type=cls.area_type, p_code="asdfgfhghkjltr")

    def create_dummy_correct_input(self) -> Dict:
        return {
            "issueType": Feedback.POSITIVE_FEEDBACK,
            "description": "Test description",
        }

    def submit_feedback(self, data: Dict) -> str:
        amount = Feedback.objects.count()
        response = self.graphql_request(
            request_string=self.CREATE_NEW_FEEDBACK_MUTATION,
            context={
                "user": self.user,
                "headers": {
                    "Business-Area": self.business_area.slug,
                    "Program": encode_id_base64(self.program.id, "ProgramNode"),
                },
            },
            variables={"input": data},
        )
        assert "errors" not in response, response
        self.assertEqual(Feedback.objects.count(), amount + 1)
        return decode_id_string_required(response["data"]["createFeedback"]["feedback"]["id"])

    def create_new_feedback(self, data: Optional[Dict] = None) -> str:
        return self.submit_feedback(data or self.create_dummy_correct_input())

    def test_creating_new_feedback(self) -> None:
        self.create_new_feedback()

    def test_getting_all_feedbacks(self) -> None:
        self.create_new_feedback()
        response = self.graphql_request(
            request_string=self.ALL_FEEDBACKS_QUERY,
            context={
                "user": self.user,
                "headers": {
                    "Business-Area": self.business_area.slug,
                },
            },
            variables={},
        )
        assert "errors" not in response, response["errors"]
        self.assertEqual(len(response["data"]["allFeedbacks"]["edges"]), 1)

    def test_permission_denied_when_user_is_not_provided(self) -> None:
        self.create_new_feedback()
        response = self.graphql_request(
            request_string=self.ALL_FEEDBACKS_QUERY,
            variables={},
        )
        self.assertIsNotNone(response.get("errors"))
        self.assertIn("Permission Denied", response["errors"][0]["message"])

    def test_filtering_feedbacks(self) -> None:
        self.create_new_feedback(
            data=self.create_dummy_correct_input()
            | {
                "householdLookup": encode_id_base64(self.household.pk, "Household"),
                "individualLookup": encode_id_base64(self.individuals[0].pk, "Individual"),
                "program": encode_id_base64(self.program.pk, "Program"),
            }
        )

        def filter_it(variables: Dict) -> List:
            response = self.graphql_request(
                request_string=self.ALL_FEEDBACKS_QUERY,
                context={
                    "user": self.user,
                    "headers": {
                        "Business-Area": self.business_area.slug,
                        "Program": encode_id_base64(self.program.id, "ProgramNode"),
                    },
                },
                variables={} | variables,
            )
            assert "errors" not in response, response["errors"]
            return response["data"]["allFeedbacks"]["edges"]

        assert len(filter_it({"issueType": Feedback.NEGATIVE_FEEDBACK})) == 0
        assert len(filter_it({"issueType": Feedback.POSITIVE_FEEDBACK})) == 1

        assert len(filter_it({"feedbackId": self.program.pk})) == 0
        assert len(filter_it({"feedbackId": Feedback.objects.first().unicef_id})) == 1

        assert len(filter_it({"createdBy": str(self.user.pk)})) == 1
        assert len(filter_it({"createdBy": str(self.program.pk)})) == 0

    def test_failing_to_create_new_feedback(self) -> None:
        def expect_failure(data: Dict) -> None:
            current_amount = Feedback.objects.count()
            response = self.graphql_request(
                request_string=self.CREATE_NEW_FEEDBACK_MUTATION,
                context={"user": self.user, "headers": {"Business-Area": self.business_area.slug}},
                variables={"input": data},
            )
            assert "errors" in response, response
            self.assertEqual(Feedback.objects.count(), current_amount)

        # missing issue type
        expect_failure(
            {
                "description": "Test description",
            }
        )

        # missing description
        expect_failure(
            {
                "issueType": Feedback.POSITIVE_FEEDBACK,
            }
        )

    def test_optional_household_lookup(self) -> None:
        data = self.create_dummy_correct_input() | {
            "householdLookup": encode_id_base64(self.household.pk, "Household"),
        }
        self.submit_feedback(data)
        feedback = Feedback.objects.first()
        self.assertEqual(feedback.household_lookup, self.household)

    def test_optional_individual_lookup(self) -> None:
        data = self.create_dummy_correct_input() | {
            "individualLookup": encode_id_base64(self.individuals[0].pk, "Individual"),
        }
        self.submit_feedback(data)
        self.assertEqual(Feedback.objects.count(), 1)
        feedback = Feedback.objects.first()
        self.assertEqual(feedback.individual_lookup, self.individuals[0])

    def test_optional_comments(self) -> None:
        data = self.create_dummy_correct_input() | {
            "comments": "Test comments",
        }
        self.submit_feedback(data)
        feedback = Feedback.objects.first()
        self.assertEqual(feedback.comments, "Test comments")

    def test_optional_language(self) -> None:
        data = self.create_dummy_correct_input() | {
            "language": "en",
        }
        self.submit_feedback(data)
        feedback = Feedback.objects.first()
        self.assertEqual(feedback.language, "en")

    def test_optional_area(self) -> None:
        data = self.create_dummy_correct_input() | {
            "area": "Test area",
        }
        self.submit_feedback(data)
        feedback = Feedback.objects.first()
        self.assertEqual(feedback.area, "Test area")

    def test_optional_admin2(self) -> None:
        country = CountryFactory()
        area_type = geo_models.AreaType.objects.create(name="X", area_level=1, country=country)
        admin2 = geo_models.Area.objects.create(p_code="SO25", name="SO25", area_type=area_type)
        data = self.create_dummy_correct_input() | {
            "admin2": encode_id_base64(admin2.pk, "Area"),
        }
        self.submit_feedback(data)
        feedback = Feedback.objects.first()
        self.assertEqual(feedback.admin2, admin2)

    def test_updating_feedback(self) -> None:
        feedback_id = self.create_new_feedback()
        feedback = Feedback.objects.get(id=feedback_id)
        self.assertEqual(feedback.issue_type, Feedback.POSITIVE_FEEDBACK)
        response = self.graphql_request(
            request_string=self.UPDATE_FEEDBACK_MUTATION,
            context={
                "user": self.user,
                "headers": {
                    "Business-Area": self.business_area.slug,
                    "Program": self.id_to_base64(self.program.id, "ProgramNode"),
                },
            },
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

    def test_getting_single_feedback(self) -> None:
        feedback_id = self.create_new_feedback()
        response = self.graphql_request(
            request_string=self.SINGLE_FEEDBACK_QUERY,
            context={
                "user": self.user,
                "headers": {
                    "Business-Area": self.business_area.slug,
                    "Program": self.id_to_base64(self.program.id, "ProgramNode"),
                },
            },
            variables={"id": encode_id_base64(feedback_id, "Feedback")},
        )
        assert "errors" not in response, response["errors"]
        self.assertEqual(response["data"]["feedback"]["id"], encode_id_base64(feedback_id, "Feedback"))

    def create_linked_grievance_ticket(self, feedback_id: str) -> Dict:
        create_grievance_response = self.graphql_request(
            request_string=self.CREATE_GRIEVANCE_MUTATION,
            context={
                "user": self.user,
                "headers": {
                    "Business-Area": self.business_area.slug,
                    "Program": self.id_to_base64(self.program.id, "ProgramNode"),
                },
            },
            variables={
                "input": {
                    "description": "Test Feedback",
                    "assignedTo": self.id_to_base64(self.user.id, "UserNode"),
                    "category": GrievanceTicket.CATEGORY_REFERRAL,
                    "admin": encode_id_base64(str(self.admin_area.id), "Area"),
                    "language": "Polish, English",
                    "consent": True,
                    "businessArea": "afghanistan",
                    "linkedFeedbackId": feedback_id,
                }
            },
        )
        assert "errors" not in create_grievance_response, create_grievance_response["errors"]
        return create_grievance_response["data"]["createGrievanceTicket"]["grievanceTickets"][0]

    def test_linking_feedback_to_grievance_ticket(self) -> None:
        feedback_id = self.create_new_feedback()
        grievance_data = self.create_linked_grievance_ticket(feedback_id)
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

    def test_individuals_lookup_household_matching_household_lookup(self) -> None:
        self.other_household, self.other_individuals = create_household_and_individuals(
            household_data={
                "registration_data_import": self.registration_data_import,
                "business_area": self.business_area,
                "program": self.program,
            },
            individuals_data=[{}],
        )

        amount = Feedback.objects.count()
        response = self.graphql_request(
            request_string=self.CREATE_NEW_FEEDBACK_MUTATION,
            context={
                "user": self.user,
                "headers": {
                    "Business-Area": self.business_area.slug,
                    "Program": self.id_to_base64(self.program.id, "ProgramNode"),
                },
            },
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

    def test_ordering_by_issue_type(self) -> None:
        self.create_new_feedback(
            data=self.create_dummy_correct_input()
            | {
                "issueType": Feedback.POSITIVE_FEEDBACK,
            }
        )
        self.create_new_feedback(
            data=self.create_dummy_correct_input()
            | {
                "issueType": Feedback.NEGATIVE_FEEDBACK,
            }
        )

        response_1 = self.graphql_request(
            request_string=self.ALL_FEEDBACKS_QUERY,
            context={
                "user": self.user,
                "headers": {
                    "Business-Area": self.business_area.slug,
                },
            },
            variables={"orderBy": "-issue_type"},
        )
        assert "errors" not in response_1, response_1["errors"]
        feedbacks_1 = response_1["data"]["allFeedbacks"]["edges"]
        self.assertEqual(len(feedbacks_1), 2)
        self.assertEqual(feedbacks_1[0]["node"]["issueType"], Feedback.POSITIVE_FEEDBACK)
        self.assertEqual(feedbacks_1[1]["node"]["issueType"], Feedback.NEGATIVE_FEEDBACK)

        response_2 = self.graphql_request(
            request_string=self.ALL_FEEDBACKS_QUERY,
            context={
                "user": self.user,
                "headers": {
                    "Business-Area": self.business_area.slug,
                },
            },
            variables={"orderBy": "issue_type"},
        )
        assert "errors" not in response_2, response_2["errors"]
        feedbacks_2 = response_2["data"]["allFeedbacks"]["edges"]
        self.assertEqual(len(feedbacks_2), 2)
        self.assertEqual(feedbacks_2[0]["node"]["issueType"], Feedback.NEGATIVE_FEEDBACK)
        self.assertEqual(feedbacks_2[1]["node"]["issueType"], Feedback.POSITIVE_FEEDBACK)

    def test_ordering_by_linked_grievance(self) -> None:
        feedback_id_1 = self.create_new_feedback()
        grievance_data_1 = self.create_linked_grievance_ticket(feedback_id_1)
        feedback_id_2 = self.create_new_feedback()
        grievance_data_2 = self.create_linked_grievance_ticket(feedback_id_2)
        self.create_new_feedback()

        response_1 = self.graphql_request(
            request_string=self.ALL_FEEDBACKS_QUERY,
            context={
                "user": self.user,
                "headers": {
                    "Business-Area": self.business_area.slug,
                },
            },
            variables={"orderBy": "linked_grievance"},
        )
        assert "errors" not in response_1, response_1["errors"]
        feedbacks_1 = response_1["data"]["allFeedbacks"]["edges"]
        self.assertEqual(len(feedbacks_1), 3)
        self.assertEqual(feedbacks_1[0]["node"]["linkedGrievance"]["id"], grievance_data_1["id"])
        self.assertEqual(feedbacks_1[1]["node"]["linkedGrievance"]["id"], grievance_data_2["id"])
        self.assertEqual(feedbacks_1[2]["node"]["linkedGrievance"], None)

        response_2 = self.graphql_request(
            request_string=self.ALL_FEEDBACKS_QUERY,
            context={
                "user": self.user,
                "headers": {
                    "Business-Area": self.business_area.slug,
                },
            },
            variables={"orderBy": "-linked_grievance"},
        )
        assert "errors" not in response_2, response_2["errors"]
        feedbacks_2 = response_2["data"]["allFeedbacks"]["edges"]
        self.assertEqual(len(feedbacks_2), 3)
        self.assertEqual(feedbacks_2[0]["node"]["linkedGrievance"], None)
        self.assertEqual(feedbacks_2[1]["node"]["linkedGrievance"]["id"], grievance_data_2["id"])
        self.assertEqual(feedbacks_2[2]["node"]["linkedGrievance"]["id"], grievance_data_1["id"])
