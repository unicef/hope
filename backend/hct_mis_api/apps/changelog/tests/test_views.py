from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from faker import Faker

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.changelog.models import Changelog

User = get_user_model()

faker = Faker()


def create_changelog() -> Changelog:
    defaults = {
        "description": faker.paragraph(nb_sentences=5),
        "version": faker.bothify(text="#.##.###"),
        "active": faker.boolean(),
        "date": faker.date_this_month(),
    }
    return Changelog.objects.create(**defaults)


class APITestCase(TestCase):

    def setUp(self):
        self.superuser = UserFactory(is_superuser=True, is_staff=True)
        self.user = UserFactory()

    def tests_Changelog_list_view(self):
        instance1 = create_changelog()
        instance2 = create_changelog()
        url = reverse("changelog_Changelog_list")
        # Log out
        self.client.logout()
        resp = self.client.get(url)
        assert resp.status_code == 302, "You need to be logged in"
        self.client.force_login(self.user)
        resp = self.client.get(url)
        assert resp.status_code == 200, "You need to be logged in and superuser"
        assert str(instance1.date) in resp.content.decode("utf-8")
        assert str(instance2.date) in resp.content.decode("utf-8")

    def tests_Changelog_detail_view(self):
        instance = create_changelog()
        url = reverse(
            "changelog_Changelog_detail",
            args=[
                instance.pk,
            ],
        )
        self.client.force_login(self.user)
        response = self.client.get(url)
        assert response.status_code == 200
        assert str(instance.version) in response.content.decode("utf-8")
