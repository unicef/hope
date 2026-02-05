from typing import TYPE_CHECKING, Any

from django.test import Client
from django.urls import reverse
import pytest
from rest_framework import status

from extras.test_utils.factories import ChangelogFactory, UserFactory

if TYPE_CHECKING:
    from hope.models import Changelog, User

pytestmark = pytest.mark.django_db


@pytest.fixture
def user(db: Any) -> "User":
    return UserFactory()


@pytest.fixture
def changelog_active(db: Any) -> "Changelog":
    return ChangelogFactory(active=True)


@pytest.fixture
def two_active_changelogs(db: Any) -> tuple["Changelog", "Changelog"]:
    return ChangelogFactory(active=True), ChangelogFactory(active=True)


def test_changelog_list_view_redirects_unauthenticated_user(
    client: Client,
) -> None:
    url = reverse("changelog_changelog_list")
    response = client.get(url)
    assert response.status_code == status.HTTP_302_FOUND


def test_changelog_list_view_returns_200_for_authenticated_user(
    client: Client,
    user: "User",
    two_active_changelogs: tuple["Changelog", "Changelog"],
) -> None:
    instance1, instance2 = two_active_changelogs
    client.force_login(user, "django.contrib.auth.backends.ModelBackend")
    url = reverse("changelog_changelog_list")
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK
    content = response.content.decode("utf-8")
    assert str(instance1.version) in content
    assert str(instance2.date.strftime("%A %d %b %Y")) in content


def test_changelog_detail_view_returns_200_with_version(
    client: Client,
    user: "User",
    changelog_active: "Changelog",
) -> None:
    client.force_login(user, "django.contrib.auth.backends.ModelBackend")
    url = reverse("changelog_changelog_detail", args=[changelog_active.pk])
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert str(changelog_active.version) in response.content.decode("utf-8")
