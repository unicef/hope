from extras.test_utils.factories.core import create_afghanistan
from extras.test_utils.factories.steficon import RuleCommitFactory, RuleFactory

from hope.apps.core.base_test_case import APITestCase
from hope.apps.steficon.models import Rule

RULE_QUERY = """
query AllSteficonRules(
    $enabled: Boolean
    $deprecated: Boolean
    $type: String!
  ) {
    allSteficonRules(enabled: $enabled, deprecated: $deprecated, type: $type) {
      edges {
        node {
          name
          type
          deprecated
          enabled
        }
      }
    }
  }
"""


class TestRuleSchema(APITestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.business_area = create_afghanistan()

        cls.rule_1 = RuleFactory(
            name="rule_1",
            type=Rule.TYPE_TARGETING,
            deprecated=False,
            enabled=True,
        )
        cls.rule_1.allowed_business_areas.add(cls.business_area)
        RuleCommitFactory(rule=cls.rule_1, version=2)

        cls.rule_2 = RuleFactory(
            name="rule_2",
            type=Rule.TYPE_TARGETING,
            deprecated=False,
            enabled=True,
        )
        RuleCommitFactory(rule=cls.rule_2, version=3)

    def test_rule_schema_shows_only_allowed_rules(self) -> None:
        self.snapshot_graphql_request(
            request_string=RULE_QUERY,
            variables={"type": Rule.TYPE_TARGETING},
            context={"headers": {"Business-Area": self.business_area.slug}},
        )
