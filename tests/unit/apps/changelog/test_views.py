from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from extras.test_utils.factories.account import UserFactory
from rest_framework import status

from hct_mis_api.apps.changelog.factory import ChangelogFactory

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
        self.assertEqual(resp.status_code, status.HTTP_302_FOUND, msg="You need to be logged in")
        self.client.force_login(self.user, "django.contrib.auth.backends.ModelBackend")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK, "You need to be logged in and superuser")
        self.assertIn(str(instance1.version), resp.content.decode("utf-8"))
        self.assertIn(str(instance2.date.strftime("%A %d %b %Y")), resp.content.decode("utf-8"))

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
        self.assertEqual(resp.status_code, status.HTTP_200_OK, "You need to be logged in and superuser")
        self.assertIn(str(instance.version), resp.content.decode("utf-8"))
