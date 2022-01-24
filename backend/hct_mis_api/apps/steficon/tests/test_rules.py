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
        r = Rule(definition="result.value=1.0")
        self.assertEqual(
            r.as_dict(),
            {"definition": "result.value=1.0", "deprecated": False, "enabled": False, "language": "python", "name": ""},
        )

    def test_execution(self):
        rule = Rule(definition="result.value=101")
        result = rule.execute({"hh": self.household})
        self.assertEqual(result.value, 101)

    def test_history(self):
        rule = Rule(definition="result.value=1", enabled=True)
        rule.save()
        # no history on first save
        self.assertFalse(rule.history.first())

        # no history if no changes
        rule.save()
        self.assertFalse(rule.history.first())

        rule.definition = "result.value=2"
        rule.save()
        history = rule.history.first()
        self.assertTrue(history)
        self.assertEqual(history.after, rule.as_dict())
        self.assertEqual(history.before["definition"], "result.value=1")
        self.assertEqual(history.affected_fields, ["definition"])

    def test_revert(self):
        rule = Rule(definition="result.value=1", enabled=True)
        rule.save()
        original_version = rule.version

        rule.definition = "result.value=2"
        rule.save()

        rule.definition = "result.value=3"
        rule.save()

        state = rule.history.latest()
        state.revert()

        rule.refresh_from_db()
        self.assertEqual(state.version, original_version)
        self.assertEqual(rule.definition, "result.value=1")
        self.assertGreater(rule.version, original_version)

    def test_release(self):
        rule = Rule(definition="result.value=1", enabled=True)
        rule.save()
        release1 = rule.release()
        self.assertEqual(release1.version, 1)
        self.assertEqual(rule.history.count(), 1)
        self.assertEqual(rule.latest, rule.history.latest())
        rule.save()
        release2 = rule.release()
        release1.refresh_from_db()
        self.assertEqual(release2.version, 2)
        self.assertNotEquals(release1, release2)
        self.assertNotEquals(release1, release2)
