from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from extras.test_utils.factories.account import UserFactory
from hope.apps.changelog.factory import ChangelogFactory

User = get_user_model()


class APITestCase(TestCase):
    def setUp(self) -> None:
        self.superuser = UserFactory(is_superuser=True, is_staff=True)
        self.user = UserFactory()

    def tests_changelog_list_view(self) -> None:
        instance1 = ChangelogFactory(active=True)
        instance2 = ChangelogFactory(active=True)
        url = reverse("changelog_changelog_list")
        # Log out
        self.client.logout()
        resp = self.client.get(url)
        assert resp.status_code == status.HTTP_302_FOUND, "You need to be logged in"
        self.client.force_login(self.user, "django.contrib.auth.backends.ModelBackend")
        resp = self.client.get(url)
        assert resp.status_code == status.HTTP_200_OK, "You need to be logged in and superuser"
        assert str(instance1.version) in resp.content.decode("utf-8")
        assert str(instance2.date.strftime("%A %d %b %Y")) in resp.content.decode("utf-8")

    def tests_changelog_detail_view(self) -> None:
        instance = ChangelogFactory()
        url = reverse(
            "changelog_changelog_detail",
            args=[
                instance.pk,
            ],
        )
        self.client.force_login(self.user, "django.contrib.auth.backends.ModelBackend")
        resp = self.client.get(url)
        assert resp.status_code == status.HTTP_200_OK, "You need to be logged in and superuser"
        assert str(instance.version) in resp.content.decode("utf-8")
