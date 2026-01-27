import pytest

from extras.test_utils.factories import ChangelogFactory


@pytest.mark.django_db
def test_changelog_factories():
    changelog = ChangelogFactory()
    assert changelog.pk is not None
