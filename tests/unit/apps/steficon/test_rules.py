from typing import Tuple
from unittest.mock import Mock

import pytest
from extras.test_utils.factories.account import BusinessAreaFactory, UserFactory
from extras.test_utils.factories.household import HouseholdFactory

from hct_mis_api.admin.rule import RuleAdmin
from hct_mis_api.admin.rule_commit import RuleCommitAdmin

from hct_mis_api.apps.account.models import User
from hct_mis_api.apps.household.models import Household
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


@pytest.fixture
def basic_rule_setup() -> Tuple[User, Household]:
    BusinessAreaFactory()
    user = UserFactory(is_superuser=True, username="test")
    user.set_password("test")
    user.save()
    household = HouseholdFactory.build()
    return user, household


@pytest.mark.django_db
def test_rule() -> None:
    r = Rule(definition="result.value=1.0")
    assert r.as_dict() == {
        "definition": "result.value=1.0",
        "deprecated": False,
        "enabled": False,
        "language": "python",
        "name": "",
    }


@pytest.mark.django_db
def test_execution(basic_rule_setup: Tuple[User, Household]) -> None:
    user, household = basic_rule_setup
    rule = Rule(definition="result.value=101")
    result = rule.execute({"hh": household})
    assert result.value == 101


@pytest.mark.django_db
def test_history() -> None:
    rule = Rule(definition="result.value=1", enabled=True, name="Rule1")
    rule.save()
    # history on first save
    assert rule.history.count() == 1
    assert rule.latest_commit
    assert rule.latest_commit.before == {}
    assert rule.latest_commit.after == rule.as_dict()
    assert rule.version == rule.latest_commit.version

    # no history if no changes
    rule.save()
    assert rule.history.count() == 1, rule.last_changes
    assert rule.latest_commit.version
    assert rule.version != rule.latest_commit.version

    rule.definition = "result.value=2"
    rule.save()
    history = rule.history.all()
    assert len(history) == 2
    assert rule.version == rule.latest_commit.version
    assert history[0].version == 3  # because version 2 did not produced changes
    assert history[0].after == rule.as_dict()
    assert history[0].before["definition"] == "result.value=1"
    assert history[0].affected_fields == ["definition"]
    assert history[1].version == 1
    assert history[1].before == {}
    assert history[1].after["definition"] == "result.value=1"
    assert sorted(history[1].affected_fields) == ["definition", "deprecated", "enabled", "language", "name"]


@pytest.mark.django_db
def test_revert() -> None:
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
    assert first_commit.version == original_version
    assert rule.definition == "result.value=1"
    assert rule.version > original_version
    assert rule.version == rule.latest_commit.version


@pytest.mark.django_db
def test_release() -> None:
    rule = Rule(definition="result.value=1", enabled=True)
    rule.save()
    release1 = rule.release()
    assert release1.version == 1
    assert rule.history.count() == 1
    assert rule.latest == rule.history.latest()
    rule.save()
    release2 = rule.release()
    release1.refresh_from_db()
    assert release2.version == 2
    assert release1 != release2
    assert release1 != release2


@pytest.mark.django_db
def test_nested_rule(basic_rule_setup: Tuple[User, Household]) -> None:
    user, household = basic_rule_setup
    rule1 = Rule.objects.create(name="Rule1", definition="result.value=101", enabled=True)
    rule2 = Rule.objects.create(
        name="Rule2", definition=f"result.value=invoke({rule1.pk}, context).value", enabled=True
    )
    rule1.release()
    rule2.release()

    result = rule2.execute({"hh": household})
    assert result.value == 101


@pytest.mark.django_db
def test_modules() -> None:
    rule = Rule.objects.create(
        name="Rule1", definition="age1=dateutil.relativedelta.relativedelta(years=17)", enabled=True
    )
    is_valid = rule.interpreter.validate()
    assert is_valid

    rule = Rule.objects.create(name="Rule2", definition="age1=datetime.date.today()", enabled=True)
    is_valid = rule.execute({}, only_release=False)
    assert is_valid


@pytest.mark.django_db
def test_root_user_can_edit_version_and_rule(basic_rule_setup: Tuple[User, Household]) -> None:
    user, household = basic_rule_setup
    assert RuleCommitAdmin(Mock(), Mock()).get_readonly_fields(
        Mock(user=user, headers={"x-root-token": settings.ROOT_TOKEN})
    ) == ["updated_by"]


@pytest.mark.django_db
def test_regular_user_cannot_edit_version_and_rule() -> None:
    assert RuleCommitAdmin(Mock(), Mock()).get_readonly_fields(Mock(user=UserFactory(is_superuser=False))) == [
        "updated_by",
        "version",
        "rule",
    ]


@pytest.mark.django_db
def test_get_readonly_fields(basic_rule_setup: Tuple[User, Household]) -> None:
    user, household = basic_rule_setup
    # is_root
    assert RuleAdmin(Mock(), Mock()).get_readonly_fields(
        Mock(user=user, headers={"x-root-token": settings.ROOT_TOKEN})
    ) == ["created_by", "created_at", "updated_by", "updated_at", "version"]
    # is_superuser
    assert RuleAdmin(Mock(), Mock()).get_readonly_fields(Mock(user=UserFactory(is_superuser=True))) == [
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
    ]
    # just regular staff user
    assert RuleAdmin(Mock(), Mock()).get_readonly_fields(Mock(user=UserFactory(is_superuser=False))) == [
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
    ]
