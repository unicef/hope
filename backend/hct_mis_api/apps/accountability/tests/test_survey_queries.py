from parameterized import parameterized

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.accountability.factories import SurveyFactory
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.household.fixtures import create_household
from hct_mis_api.apps.targeting.fixtures import TargetPopulationFactory


class TestSurveyQueries(APITestCase):
    QUERY_LIST = """
    query AllSurveys(
        $search: String
        $targetPopulation: ID
        $program: ID
        $createdBy: ID
    ) {
      allSurveys(search: $search, targetPopulation: $targetPopulation, program: $program, createdBy: $createdBy) {
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
    def setUpTestData(cls):
        cls.business_area = create_afghanistan()
        cls.user = UserFactory(first_name="John", last_name="Wick")
        cls.target_population = TargetPopulationFactory(business_area=cls.business_area)

        households = [create_household()[0] for _ in range(14)]
        cls.target_population.households.set(households)

        SurveyFactory.create_batch(3, target_population=cls.target_population, created_by=cls.user)
        SurveyFactory(title="Test survey", target_population=cls.target_population, created_by=cls.user)
        SurveyFactory.create_batch(
            3, target_population=TargetPopulationFactory(business_area=cls.business_area), created_by=UserFactory()
        )

    def test_query_list_without_permissions(self):
        self.create_user_role_with_permissions(self.user, [], self.business_area)

        self.snapshot_graphql_request(
            request_string=self.QUERY_LIST,
            context={"user": self.user, "headers": {"Business-Area": self.business_area.slug}},
            variables={},
        )

    def test_query_list_filter_by_search(self):
        self.create_user_role_with_permissions(
            self.user, [Permissions.ACCOUNTABILITY_SURVEY_VIEW_LIST], self.business_area
        )

        self.snapshot_graphql_request(
            request_string=self.QUERY_LIST,
            context={"user": self.user, "headers": {"Business-Area": self.business_area.slug}},
            variables={"search": "Test survey"},
        )

    def test_query_list_filter_by_target_population(self):
        self.create_user_role_with_permissions(
            self.user, [Permissions.ACCOUNTABILITY_SURVEY_VIEW_LIST], self.business_area
        )

        self.snapshot_graphql_request(
            request_string=self.QUERY_LIST,
            context={"user": self.user, "headers": {"Business-Area": self.business_area.slug}},
            variables={
                "targetPopulation": self.id_to_base64(self.target_population.id, "TargetPopulationNode"),
            },
        )

    def test_query_list_filter_by_created_by(self):
        self.create_user_role_with_permissions(
            self.user, [Permissions.ACCOUNTABILITY_SURVEY_VIEW_LIST], self.business_area
        )

        self.snapshot_graphql_request(
            request_string=self.QUERY_LIST,
            context={"user": self.user, "headers": {"Business-Area": self.business_area.slug}},
            variables={
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
    def test_single_survey(self, _, permissions):
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)
        survey = SurveyFactory(
            title="Test survey single", target_population=self.target_population, created_by=self.user
        )

        self.snapshot_graphql_request(
            request_string=self.QUERY_SINGLE,
            context={"user": self.user, "headers": {"Business-Area": self.business_area.slug}},
            variables={"id": self.id_to_base64(survey.id, "SurveyNode")},
        )
