from unittest.mock import Mock

from django.contrib.auth import get_user_model
from django.test import TestCase

from extras.test_utils.factories.account import BusinessAreaFactory, UserFactory
from extras.test_utils.factories.household import HouseholdFactory

from hct_mis_api.apps.steficon.admin import RuleAdmin, RuleCommitAdmin
from hct_mis_api.apps.steficon.models import Rule
from hct_mis_api.config import settings

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
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        BusinessAreaFactory()
        cls.user = get_user_model().objects.create_superuser(username="test", password="test")
        cls.household = HouseholdFactory.build()

    def test_rule(self) -> None:
        r = Rule(definition="result.value=1.0")
        self.assertEqual(
            r.as_dict(),
            {"definition": "result.value=1.0", "deprecated": False, "enabled": False, "language": "python", "name": ""},
        )

    def test_execution(self) -> None:
        rule = Rule(definition="result.value=101")
        result = rule.execute({"hh": self.household})
        self.assertEqual(result.value, 101)

    def test_history(self) -> None:
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

    def test_revert(self) -> None:
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

    def test_release(self) -> None:
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

    def test_nested_rule(self) -> None:
        rule1 = Rule.objects.create(name="Rule1", definition="result.value=101", enabled=True)
        rule2 = Rule.objects.create(
            name="Rule2", definition=f"result.value=invoke({rule1.pk}, context).value", enabled=True
        )
        rule1.release()
        rule2.release()

        result = rule2.execute({"hh": self.household})
        self.assertEqual(result.value, 101)

    def test_modules(self) -> None:
        rule = Rule.objects.create(
            name="Rule1", definition="age1=dateutil.relativedelta.relativedelta(years=17)", enabled=True
        )
        is_valid = rule.interpreter.validate()
        self.assertTrue(is_valid)

        rule = Rule.objects.create(name="Rule2", definition="age1=datetime.date.today()", enabled=True)
        is_valid = rule.execute({}, only_release=False)
        self.assertTrue(is_valid)

    def test_root_user_can_edit_version_and_rule(self) -> None:
        self.assertEqual(
            RuleCommitAdmin(Mock(), Mock()).get_readonly_fields(
                Mock(user=self.user, headers={"x-root-token": settings.ROOT_TOKEN})
            ),
            ["updated_by"],
        )

    def test_regular_user_cannot_edit_version_and_rule(self) -> None:
        self.assertEqual(
            RuleCommitAdmin(Mock(), Mock()).get_readonly_fields(Mock(user=UserFactory(is_superuser=False))),
            ["updated_by", "version", "rule"],
        )

    def test_get_readonly_fields(self) -> None:
        # is_root
        self.assertEqual(
            RuleAdmin(Mock(), Mock()).get_readonly_fields(
                Mock(user=self.user, headers={"x-root-token": settings.ROOT_TOKEN})
            ),
            ["created_by", "created_at", "updated_by", "updated_at", "version"],
        )
        # is_superuser
        self.assertEqual(
            RuleAdmin(Mock(), Mock()).get_readonly_fields(Mock(user=UserFactory(is_superuser=True))),
            [
                "created_by",
                "created_at",
                "updated_by",
                "updated_at",
                "version",
                "name",
                "type",
                "enabled",
                "deprecated",
                "language",
                "definition",
                "description",
                "flags",
            ],
        )
        # just regular staff user
        self.assertEqual(
            RuleAdmin(Mock(), Mock()).get_readonly_fields(Mock(user=UserFactory(is_superuser=False))),
            [
                "created_by",
                "created_at",
                "updated_by",
                "updated_at",
                "version",
                "name",
                "type",
                "enabled",
                "deprecated",
                "language",
                "definition",
                "description",
                "flags",
                "allowed_business_areas",
            ],
        )
