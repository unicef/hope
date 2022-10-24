from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.accountability.models import Survey
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.household.fixtures import create_household
from hct_mis_api.apps.targeting.fixtures import TargetPopulationFactory


class TestCreateSurvey(APITestCase):
    CREATE_SURVEY_MUTATION = """
    mutation CreateSurvey($input: CreateSurveyInput!) {
      createSurvey(input: $input) {
        survey {
          title
          numberOfRecipients
          createdBy {
            firstName
            lastName
          }
        }
      }
    }
    """

    @classmethod
    def setUpTestData(cls):
        cls.business_area = create_afghanistan()
        cls.user = UserFactory(first_name="John", last_name="Doe")
        cls.tp = TargetPopulationFactory(business_area=cls.business_area)

    def test_create_survey_without_permission(self):
        self.create_user_role_with_permissions(self.user, [], self.business_area)

        self.snapshot_graphql_request(
            request_string=self.CREATE_SURVEY_MUTATION,
            context={"user": self.user, "headers": {"Business-Area": self.business_area.slug}},
            variables={
                "input": {
                    "title": "Test survey",
                    "category": Survey.CATEGORY_MANUAL,
                    "samplingType": Survey.SAMPLING_RANDOM,
                }
            },
        )

    def test_create_survey_without_target_population_and_program(self):
        self.create_user_role_with_permissions(
            self.user, [Permissions.ACCOUNTABILITY_SURVEY_VIEW_CREATE], self.business_area
        )

        self.snapshot_graphql_request(
            request_string=self.CREATE_SURVEY_MUTATION,
            context={"user": self.user, "headers": {"Business-Area": self.business_area.slug}},
            variables={
                "input": {
                    "title": "Test survey",
                    "category": Survey.CATEGORY_MANUAL,
                    "samplingType": Survey.SAMPLING_RANDOM,
                }
            },
        )

    def test_create_survey(self):
        self.create_user_role_with_permissions(
            self.user, [Permissions.ACCOUNTABILITY_SURVEY_VIEW_CREATE], self.business_area
        )

        create_household({"size": 3})
        households = [create_household({"size": 3})[0] for _ in range(3)]
        self.tp.households.set(households)

        self.snapshot_graphql_request(
            request_string=self.CREATE_SURVEY_MUTATION,
            context={"user": self.user, "headers": {"Business-Area": self.business_area.slug}},
            variables={
                "input": {
                    "title": "Test survey",
                    "category": Survey.CATEGORY_MANUAL,
                    "samplingType": Survey.SAMPLING_FULL_LIST,
                    "targetPopulation": self.id_to_base64(self.tp.id, "TargetPopulationNode"),
                    "fullListArguments": {
                        "excludedAdminAreas": [],
                    },
                }
            },
        )
