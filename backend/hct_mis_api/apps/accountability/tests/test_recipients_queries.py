from parameterized import parameterized

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.accountability.fixtures import SurveyFactory
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.household.fixtures import create_household
from hct_mis_api.apps.targeting.fixtures import TargetPopulationFactory


class TestSurveyQueries(APITestCase):
    QUERY_LIST = """
    query Recipients(
        $survey: String!
    ) {
      recipients(survey: $survey) {
        totalCount
      }
    }
    """

    @classmethod
    def setUpTestData(cls):
        cls.business_area = create_afghanistan()
        cls.user = UserFactory(first_name="John", last_name="Wick")
        cls.target_population = TargetPopulationFactory(business_area=cls.business_area)

        create_household()
        cls.households = [create_household()[0] for _ in range(4)]
        cls.target_population.households.set(cls.households)
        cls.maxDiff = None

    @parameterized.expand(
        [
            ("without_permissions", []),
            ("with_permissions", [Permissions.ACCOUNTABILITY_SURVEY_VIEW_DETAILS]),
        ]
    )
    def test_query_list(self, _, permissions):
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        survey = SurveyFactory(target_population=self.target_population, created_by=self.user)
        survey.recipients.set(self.households)

        self.snapshot_graphql_request(
            request_string=self.QUERY_LIST,
            context={"user": self.user, "headers": {"Business-Area": self.business_area.slug}},
            variables={
                "survey": self.id_to_base64(survey.id, "SurveyNode"),
            },
        )
