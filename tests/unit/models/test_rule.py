import pytest

from extras.test_utils.factories.steficon import RuleCommitFactory, RuleFactory
from hope.apps.steficon.config import SAFETY_HIGH, SAFETY_STANDARD
from hope.models import Rule

pytestmark = pytest.mark.django_db


def test_str_returns_name() -> None:
    assert str(Rule(name="My Rule")) == "My Rule"


def test_get_flag_returns_value_or_default() -> None:
    rule = Rule(name="r", flags={"present": "yes"})

    assert rule.get_flag("present") == "yes"
    assert rule.get_flag("missing", "fallback") == "fallback"


def test_clean_restores_original_security_for_persisted_rule() -> None:
    rule = RuleFactory(security=SAFETY_STANDARD)
    rule.security = SAFETY_HIGH

    rule.clean()

    assert rule.security == SAFETY_STANDARD


def test_clean_keeps_security_for_unsaved_rule() -> None:
    rule = Rule(name="new", security=SAFETY_HIGH)

    rule.clean()

    assert rule.security == SAFETY_HIGH


def test_clean_definition_validates_interpreter() -> None:
    rule = Rule(name="r", definition="result.value=1")

    # python interpreter validation passes without raising
    assert rule.clean_definition() is None


def test_delete_disables_rule_without_removing_it() -> None:
    rule = RuleFactory(definition="result.value=1", enabled=True)

    deleted = rule.delete()

    assert deleted == (1, {rule._meta.label: 1})
    rule.refresh_from_db()
    assert rule.enabled is False
    assert Rule.objects.filter(pk=rule.pk).exists()


def test_release_raises_for_disabled_rule() -> None:
    rule = Rule.objects.create(name="disabled", definition="result.value=1", enabled=False)

    with pytest.raises(ValueError, match="Cannot release disabled/deprecated rules"):
        rule.release()


def test_latest_returns_none_when_no_release_exists() -> None:
    rule = Rule.objects.create(name="no-release", definition="result.value=1", enabled=True)

    # save created a non-release commit only
    assert rule.latest is None


def test_last_changes_returns_latest_commit_fields() -> None:
    rule = Rule.objects.create(name="changed", definition="result.value=1", enabled=True)

    last_changes = rule.last_changes

    assert set(last_changes.keys()) == {"fields", "before", "after"}
    assert last_changes["after"]["definition"] == "result.value=1"


def test_execute_without_only_enabled_runs_released_commit() -> None:
    rule = Rule.objects.create(name="exec", definition="result.value=7", enabled=True)
    rule.release()

    result = rule.execute(only_enabled=False)

    assert result.value == 7


def test_execute_raises_when_no_released_rules() -> None:
    rule = Rule.objects.create(name="unreleased", definition="result.value=1", enabled=False)

    with pytest.raises(ValueError, match="No Released Rules found"):
        rule.execute()


def test_commit_str_disabled() -> None:
    commit = RuleCommitFactory(enabled=False)

    assert str(commit).endswith("(Disabled)")


def test_commit_str_deprecated() -> None:
    commit = RuleCommitFactory(enabled=True, deprecated=True)

    assert str(commit).endswith("(Deprecated)")


def test_commit_str_draft() -> None:
    commit = RuleCommitFactory(enabled=True, deprecated=False, is_release=False)

    assert str(commit).endswith("(Draft)")


def test_commit_str_released_has_no_suffix() -> None:
    commit = RuleCommitFactory(enabled=True, deprecated=False, is_release=True)

    assert str(commit) == f"{commit.rule} #{commit.id}"


def test_commit_prev_and_next() -> None:
    rule = RuleFactory()
    first = RuleCommitFactory(rule=rule)
    second = RuleCommitFactory(rule=rule)
    third = RuleCommitFactory(rule=rule)

    assert second.prev == first
    assert second.next == third


def test_commit_execute_runs_interpreter() -> None:
    commit = RuleCommitFactory(definition="result.value=5", language="python")

    assert commit.execute({}).value == 5


def test_commit_release_marks_release_and_deprecates_others() -> None:
    rule = RuleFactory()
    other = RuleCommitFactory(rule=rule, enabled=True)
    target = RuleCommitFactory(rule=rule, enabled=True, is_release=False)

    released = target.release()

    assert released is target
    target.refresh_from_db()
    other.refresh_from_db()
    assert target.is_release is True
    assert other.deprecated is True


def test_commit_release_is_noop_when_already_released() -> None:
    commit = RuleCommitFactory(enabled=True, deprecated=False, is_release=True)

    assert commit.release() is commit
    assert commit.is_release is True


def test_commit_release_raises_for_disabled_commit() -> None:
    commit = RuleCommitFactory(enabled=False)

    with pytest.raises(ValueError, match="Cannot release disabled/deprecated rules"):
        commit.release()
