import datetime as dt

from account.fixtures import UserFactory
from core.base_test_case import APITestCase
from household.fixtures import HouseholdFactory
from targeting.fixtures import TargetPopulationFactory


class TestTargetPopulationQuery(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.ALL_TARGET_POPULATION_QUERY = """
        query AllTargetPopulation {
            allTargetPopulation {
                edges {
                    node {
                         name
                         status
                         createdBy {
                            firstName
                            lastName
                         }
                         createdAt
                         lastEditedAt
                         households {
                            householdCaId
                            familySize
                            address
                            location {
                                title
                            }
                            registrationDataImportId {
                                name
                            }
                            headOfHousehold {
                                fullName
                                firstName
                                lastName
                            }
                         }
                    }
                }
            }
        }
        """

        cls.TARGET_POPULATION_QUERY = """
        query TargetPopulation($id: ID!) {
            targetPopulation(id: $id) {
                name
                status
                createdBy {
                    firstName
                    lastName
                 }
                createdAt
                lastEditedAt
                households {
                    householdCaId
                    familySize
                    address
                    location {
                        title
                    }
                    registrationDataImportId {
                        name
                    }
                    headOfHousehold {
                        fullName
                        firstName
                        lastName
                    }
                 }
            }
        }
        """
        cls.user = UserFactory.create()
        cls.last_edited = dt.datetime.utcnow().astimezone()
        cls.households = HouseholdFactory.create_batch(5)
        # cls.target_rules = TargetRuleFactory.create_batch(3)
        targets_to_create = [
            {
                "name": "target_1",
                "created_by": cls.user,
                "last_edited_at": cls.last_edited,
                "households": cls.households,
                # "target_rules": cls.target_rules,
            },
            {
                "name": "target_2",
                "created_by": cls.user,
                "last_edited_at": cls.last_edited,
                "households": cls.households,
                # "target_rules": cls.target_rules,
            },
        ]
        # populate mock factory model
        cls.targets = [
            TargetPopulationFactory(**data) for data in targets_to_create
        ]

    def test_all_target_population_query(self):
        self.snapshot_graphql_request(
            request_string=self.ALL_TARGET_POPULATION_QUERY,
            context={"user": self.user},
        )

    def test_target_population_query(self):
        self.snapshot_graphql_request(
            request_string=self.TARGET_POPULATION_QUERY,
            context={"user": self.user},
            variables={
                "id": self.id_to_base64(self.targets[0].id, "TargetPopulation")
            },
        )
