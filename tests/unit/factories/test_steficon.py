import pytest

from extras.test_utils.factories import RuleCommitFactory, RuleFactory

pytestmark = pytest.mark.django_db


def test_steficon_factories():
    assert RuleFactory()
    assert RuleCommitFactory()
