import pytest

from django.urls import reverse
from django.test import Client
from datetime import datetime

from hct_mis_api.apps.changelog import models as changelog_models

pytestmark = [pytest.mark.django_db]

def create_changelog_Changelog(**kwargs):
    defaults = {}
    defaults["description"] = ""
    defaults["version"] = ""
    defaults["active"] = ""
    defaults["date"] = datetime.now()
    defaults.update(**kwargs)
    return changelog_models.Changelog.objects.create(**defaults)

def tests_Changelog_list_view():
    instance1 = create_changelog_Changelog()
    instance2 = create_changelog_Changelog()
    client = Client()
    url = reverse("changelog_Changelog_list")
    response = client.get(url)
    assert response.status_code == 200
    assert str(instance1) in response.content.decode("utf-8")
    assert str(instance2) in response.content.decode("utf-8")


def tests_Changelog_detail_view():
    client = Client()
    instance = create_changelog_Changelog()
    url = reverse("changelog_Changelog_detail", args=[instance.pk, ])
    response = client.get(url)
    assert response.status_code == 200
    assert str(instance) in response.content.decode("utf-8")


