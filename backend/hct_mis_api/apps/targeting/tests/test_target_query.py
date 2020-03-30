import datetime as dt

from account.fixtures import UserFactory
from core.base_test_case import APITestCase
from household.fixtures import HouseholdFactory
from targeting.fixtures import TargetPopulationFactory


class TestTargetPopulationQuery(APITestCase):

    @classmethod
    def setUpTestData(cls):


    def test_all_target_population_query(self):
        self.snapshot_graphql_request(
            request_string=self.ALL_TARGET_POPULATION_QUERY,
            context={"user": self.user},
        )

    def test_all_target_population_num_individuals_query(self):
        self.snapshot_graphql_request(
            request_string=self.ALL_TARGET_POPULATION_NUM_INDIVIDUALS_QUERY,
            context={"user": self.user},
            variables={"numIndividualsMin": 1, "numIndividualsMax": 100},
        )

    def test_target_population_query(self):
        self.snapshot_graphql_request(
            request_string=self.TARGET_POPULATION_QUERY,
            context={"user": self.user},
            variables={
                "id": self.id_to_base64(self.targets[0].id, "TargetPopulation")
            },
        )
