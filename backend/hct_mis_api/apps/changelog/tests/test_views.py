from datetime import datetime

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from faker import Faker

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.changelog.models import Changelog

User = get_user_model()

faker = Faker()


def create_changelog_Changelog(**kwargs):
    defaults = {}
    defaults["description"] = faker.paragraph(nb_sentences=5)
    defaults["version"] = faker.bothify(text="#.##.###")
    defaults["active"] = faker.boolean()
    defaults["date"] = faker.date_this_month()
    defaults.update(**kwargs)
    return Changelog.objects.create(**defaults)


class APITestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.superuser: User = UserFactory(is_superuser=True, is_staff=True)
        cls.user: User = UserFactory()

    # def setUp(self):
    #     self.client.force_login(self.superuser)

    def tests_Changelog_list_view(self):
        instance1 = create_changelog_Changelog()
        instance2 = create_changelog_Changelog()
        url = reverse("changelog_Changelog_list")
        resp = self.client.get(url)
        assert resp.status_code == 302, "You need to be logged in"
        self.client.force_login(self.user)
        resp = self.client.get(url)
        assert resp.status_code == 200, "You need to be logged in and superuser"
        assert str(f"{instance1.version}-{instance1.date}") in resp.content.decode("utf-8")
        assert str(instance2.date) in resp.content.decode("utf-8")

    def tests_Changelog_detail_view(self):
        instance = create_changelog_Changelog()
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
