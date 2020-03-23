from account.fixtures import UserFactory
from core.base_test_case import APITestCase
from household.fixtures import HouseholdFactory
from targeting.fixtures import TargetPopulationFactory
from targeting.fixtures import TargetRuleFactory


class TestTargetPopulationQuery(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.COPY_TARGET_MUTATION = """
        mutation CopyTarget($input: CopyTargetInput!) {
          copyTarget(input: $input) {
            targetPopulation {
              id
              name
              createdBy {
                id
                firstName
                lastName
              }
              createdAt
              status
              lastEditedAt
              totalHouseholds
              totalFamilySize
              targetRules {
                totalCount
              }
            }
          }
        }
        """
        cls.user = UserFactory.create()
        cls.target = TargetPopulationFactory.create()
        cls.target.created_by = cls.user
        cls.target.households.set(HouseholdFactory.create_batch(5))
        cls.target.target_rules.set(TargetRuleFactory.create_batch(5))
        cls.target.save()

    def test_copy_target(self):
        self.snapshot_graphql_request(
            request_string=self.COPY_TARGET_MUTATION,
            context={"user": self.user},
            variables={
                "input": {
                    "targetPopulationData": {
                        "id": self.id_to_base64(
                            self.target.id, "TargetPopulation"
                        ),
                        "name": "Test New Copy Name",
                    }
                }
            },
        )
