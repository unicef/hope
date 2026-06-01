import pytest
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from extras.test_utils.factories.core import SurprisePageConfigFactory

pytestmark = pytest.mark.django_db

SURPRISE_URL = reverse("api:surprise-config")


@pytest.fixture
def anon_client() -> APIClient:
    return APIClient()


def test_get_returns_200_without_authentication(anon_client: APIClient) -> None:
    response = anon_client.get(SURPRISE_URL)
    assert response.status_code == status.HTTP_200_OK


def test_get_returns_nulls_when_no_config_exists(anon_client: APIClient) -> None:
    response = anon_client.get(SURPRISE_URL)
    data = response.json()
    assert data == {"image": None, "heading": "", "subheading": ""}


def test_get_returns_config_fields(anon_client: APIClient) -> None:
    SurprisePageConfigFactory(heading="Hello!", subheading="You made it.")
    response = anon_client.get(SURPRISE_URL)
    data = response.json()
    assert data["heading"] == "Hello!"
    assert data["subheading"] == "You made it."
    assert data["image"] is None


def test_get_returns_image_url_when_image_set(anon_client: APIClient, settings) -> None:
    from django.core.files.base import ContentFile

    config = SurprisePageConfigFactory()
    config.image.save("surprise.png", ContentFile(b"PNG"), save=True)

    response = anon_client.get(SURPRISE_URL)
    data = response.json()
    assert data["image"] is not None
    assert "surprise" in data["image"]
