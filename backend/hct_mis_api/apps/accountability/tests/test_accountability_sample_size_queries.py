from parameterized import parameterized

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.accountability.fixtures import SurveyFactory
from hct_mis_api.apps.accountability.models import Survey
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.household.fixtures import create_household
from hct_mis_api.apps.targeting.fixtures import TargetPopulationFactory


class TestAccountabilitySampleSizeQueries(APITestCase):
    QUERY = """
    query AccountabilitySampleSize(
        $input: AccountabilitySampleSizeInput!
    ) {
      accountabilitySampleSize(input: $input) {
        numberOfRecipients
        sampleSize
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
        cls.sampling_data = {
            Survey.SAMPLING_FULL_LIST: {
                "fullListArguments": {
                    "excludedAdminAreas": [],
                },
            },
            Survey.SAMPLING_RANDOM: {
                "randomSamplingArguments": {
                    "age": {"min": 20, "max": 80},
                    # "sex": MALE,
                    "confidenceInterval": 0.8,
                    "marginOfError": 80,
                    "excludedAdminAreas": [],
                },
            },
        }

    @parameterized.expand(
        [
            (Survey.SAMPLING_FULL_LIST,),
            (Survey.SAMPLING_RANDOM,),
        ]
    )
    def test_sample_size_by_target_population(self, sampling_type):
        self.create_user_role_with_permissions(self.user, [], self.business_area)

        self.maxDiff = None
        self.snapshot_graphql_request(
            request_string=self.QUERY,
            context={"user": self.user, "headers": {"Business-Area": self.business_area.slug}},
            variables={
                "input": {
                    "targetPopulation": self.id_to_base64(self.target_population.id, "TargetPopulationNode"),
                    "samplingType": sampling_type,
                    **self.sampling_data[sampling_type],
                }
            },
        )
