from django.test import TestCase
from hct_mis_api.apps.household.fixtures import HouseholdFactory

from hct_mis_api.apps.steficon.models import Rule

CODE = """
class SteficonConfig:
    name = "steficon"


def aaaaa(a: int):
    return 1


s: set = {}
d: dict = dict()
r = range(1)
l: list = ()
t: tuple = []
a: int = 1
s: str = ""
f: float = 1.1
s = s.upper()
"""


class TestBasicRule(TestCase):
    @classmethod
    def setUpTestData(self):
        self.household = HouseholdFactory.build()

    def test_rule(self):
        r = Rule(definition="score.value=1.0")
        self.assertEqual(
            r.as_dict(),
            {"definition": "score.value=1.0", "deprecated": False, "enabled": False, "language": "python", "name": ""},
        )

    def test_execution(self):
        rule = Rule(definition="score.value=101")
        value = rule.execute(hh=self.household)
        self.assertEqual(value, 101)

    def test_history(self):
        rule = Rule(definition="score.value=1", enabled=True)
        rule.save()
        # no history on first save
        self.assertFalse(rule.history.first())

        # no history if no changes
        rule.save()
        self.assertFalse(rule.history.first())

        rule.definition = "score.value=2"
        rule.save()
        history = rule.history.first()
        self.assertTrue(history)
        self.assertEqual(history.after, rule.as_dict())
        self.assertEqual(history.before["definition"], "score.value=1")
        self.assertEqual(history.affected_fields, ["definition"])

    def test_revert(self):
        rule = Rule(definition="score.value=1", enabled=True)
        rule.save()
        original_version = rule.version

        rule.definition = "score.value=2"
        rule.save()

        rule.definition = "score.value=3"
        rule.save()

        state = rule.history.latest()
        state.revert()

        rule.refresh_from_db()
        self.assertEqual(state.version, original_version)
        self.assertEqual(rule.definition, "score.value=1")
        self.assertGreater(rule.version, original_version)
