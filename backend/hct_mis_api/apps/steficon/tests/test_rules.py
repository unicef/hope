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
        rule = Rule(definition="result.value=1", enabled=True, name="Rule1")
        rule.save()
        # history on first save
        # self.assertTrue(rule.history.first())
        self.assertEqual(rule.history.count(), 1)
        self.assertTrue(rule.latest_commit)
        self.assertEqual(rule.latest_commit.before, {})
        self.assertEqual(rule.latest_commit.after, rule.as_dict())
        self.assertEqual(rule.version, rule.latest_commit.version)

        # no history if no changes
        rule.save()
        self.assertEqual(rule.history.count(), 1, rule.last_changes)
        self.assertTrue(rule.latest_commit.version, rule.version)
        self.assertNotEqual(rule.version, rule.latest_commit.version)

        rule.definition = "result.value=2"
        rule.save()
        history = rule.history.all()
        self.assertEqual(len(history), 2)
        self.assertEqual(rule.version, rule.latest_commit.version)
        self.assertEqual(history[0].version, 3)  # because version 2 did not produced changes
        self.assertEqual(history[0].after, rule.as_dict())
        self.assertEqual(history[0].before["definition"], "result.value=1")
        self.assertEqual(history[0].affected_fields, ["definition"])
        self.assertEqual(history[1].version, 1)
        self.assertEqual(history[1].before, {})
        self.assertEqual(history[1].after["definition"], "result.value=1")
        self.assertListEqual(
            sorted(history[1].affected_fields), ["definition", "deprecated", "enabled", "language", "name"]
        )

    def test_revert(self):
        rule = Rule(definition="result.value=1", enabled=True)
        rule.save()
        first_commit = rule.latest_commit
        original_version = rule.version

        rule.definition = "result.value=2"
        rule.save()

        rule.definition = "result.value=3"
        rule.save()

        first_commit.revert()

        rule.refresh_from_db()
        self.assertEqual(first_commit.version, original_version)
        self.assertEqual(rule.definition, "result.value=1")
        self.assertGreater(rule.version, original_version)
        self.assertEqual(rule.version, rule.latest_commit.version)

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
        self.assertNotEqual(release1, release2)
        self.assertNotEqual(release1, release2)

    def test_nested_rule(self):
        rule1 = Rule.objects.create(name="Rule1", definition="result.value=101", enabled=True)
        rule2 = Rule.objects.create(
            name="Rule2", definition=f"result.value=invoke({rule1.pk}, context).value", enabled=True
        )
        rule1.release()
        rule2.release()

        result = rule2.execute({"hh": self.household})
        self.assertEqual(result.value, 101)

    def test_modules(self):
        rule = Rule.objects.create(
            name="Rule1", definition="age1=dateutil.relativedelta.relativedelta(years=17)", enabled=True
        )
        is_valid = rule.interpreter.validate()
        self.assertTrue(is_valid)

        rule = Rule.objects.create(name="Rule2", definition="age1=datetime.date.today()", enabled=True)
        is_valid = rule.execute({}, only_release=False)
        self.assertTrue(is_valid)
