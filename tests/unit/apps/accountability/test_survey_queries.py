from typing import Any, List

from parameterized import parameterized

from hct_mis_api.apps.account.fixtures import PartnerFactory, UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.accountability.fixtures import SurveyFactory
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.household.fixtures import create_household
from hct_mis_api.apps.payment.fixtures import PaymentFactory, PaymentPlanFactory
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.program.models import Program


class TestSurveyQueries(APITestCase):
    QUERY_LIST = """
    query AllSurveys(
        $search: String
        $paymentPlan: ID
        $program: ID
        $createdBy: String
    ) {
      allSurveys(search: $search, paymentPlan: $paymentPlan, program: $program, createdBy: $createdBy) {
        totalCount
      }
    }
    """

    QUERY_SINGLE = """
    query Survey($id: ID!) {
      survey(id: $id) {
        title
        body
        createdBy {
          firstName
          lastName
        }
        numberOfRecipients
      }
    }
    """

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.business_area = create_afghanistan()
        cls.program = ProgramFactory(status=Program.ACTIVE)
        cls.partner = PartnerFactory(name="TestPartner")
        cls.user = UserFactory(first_name="John", last_name="Wick", partner=cls.partner)
        cls.payment_plan = PaymentPlanFactory(
            business_area=cls.business_area, created_by=cls.user, program_cycle=cls.program.cycles.first()
        )

        households = [create_household()[0] for _ in range(14)]
        for household in households:
            PaymentFactory(parent=cls.payment_plan, household=household)

        SurveyFactory.create_batch(3, program=cls.program, created_by=cls.user)
        SurveyFactory(title="Test survey", program=cls.program, payment_plan=cls.payment_plan, created_by=cls.user)

    def test_query_list_without_permissions(self) -> None:
        self.create_user_role_with_permissions(self.user, [], self.business_area)

        self.snapshot_graphql_request(
            request_string=self.QUERY_LIST,
            context={"user": self.user, "headers": {"Business-Area": self.business_area.slug}},
            variables={"program": self.id_to_base64(self.program.id, "ProgramNode")},
        )

    def test_query_list_filter_by_search(self) -> None:
        self.create_user_role_with_permissions(
            self.user, [Permissions.ACCOUNTABILITY_SURVEY_VIEW_LIST], self.business_area, self.program
        )

        self.snapshot_graphql_request(
            request_string=self.QUERY_LIST,
            context={"user": self.user, "headers": {"Business-Area": self.business_area.slug}},
            variables={"program": self.id_to_base64(self.program.id, "ProgramNode"), "search": "Test survey"},
        )

    def test_query_list_filter_by_program(self) -> None:
        self.create_user_role_with_permissions(
            self.user, [Permissions.ACCOUNTABILITY_SURVEY_VIEW_LIST], self.business_area, self.program
        )

        self.snapshot_graphql_request(
            request_string=self.QUERY_LIST,
            context={"user": self.user, "headers": {"Business-Area": self.business_area.slug}},
            variables={
                "program": self.id_to_base64(self.program.id, "ProgramNode"),
            },
        )

    def test_query_list_filter_by_target_population(self) -> None:
        self.create_user_role_with_permissions(
            self.user, [Permissions.ACCOUNTABILITY_SURVEY_VIEW_LIST], self.business_area, self.program
        )

        self.snapshot_graphql_request(
            request_string=self.QUERY_LIST,
            context={"user": self.user, "headers": {"Business-Area": self.business_area.slug}},
            variables={
                "program": self.id_to_base64(self.program.id, "ProgramNode"),
                "paymentPlan": self.id_to_base64(self.payment_plan.id, "PaymentPlanNode"),
            },
        )

    def test_query_list_filter_by_created_by(self) -> None:
        self.create_user_role_with_permissions(
            self.user, [Permissions.ACCOUNTABILITY_SURVEY_VIEW_LIST], self.business_area, self.program
        )

        self.snapshot_graphql_request(
            request_string=self.QUERY_LIST,
            context={"user": self.user, "headers": {"Business-Area": self.business_area.slug}},
            variables={
                "program": self.id_to_base64(self.program.id, "ProgramNode"),
                "createdBy": self.id_to_base64(self.user.id, "UserNode"),
            },
        )

    @parameterized.expand(
        [
            (
                "without_permission",
                [],
            ),
            ("with_permission", [Permissions.ACCOUNTABILITY_SURVEY_VIEW_DETAILS]),
        ]
    )
    def test_single_survey(self, _: Any, permissions: List[Permissions]) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)
        survey = SurveyFactory(title="Test survey single", payment_plan=self.payment_plan, created_by=self.user)

        self.snapshot_graphql_request(
            request_string=self.QUERY_SINGLE,
            context={"user": self.user, "headers": {"Business-Area": self.business_area.slug}},
            variables={"id": self.id_to_base64(survey.id, "SurveyNode")},
        )
