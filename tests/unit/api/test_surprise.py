from django.core.files.base import ContentFile
import pytest
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from extras.test_utils.factories.core import SurprisePageConfigFactory

pytestmark = pytest.mark.django_db


@pytest.fixture
def anon_client() -> APIClient:
    return APIClient()


@pytest.fixture
def surprise_url() -> str:
    return reverse("api:surprise-config")


def test_get_returns_200_without_authentication(anon_client: APIClient, surprise_url: str) -> None:
    response = anon_client.get(surprise_url)
    assert response.status_code == status.HTTP_200_OK


def test_get_returns_nulls_when_no_config_exists(anon_client: APIClient, surprise_url: str) -> None:
    response = anon_client.get(surprise_url)
    data = response.json()
    assert data == {"image": None, "heading": "", "subheading": ""}


def test_get_returns_config_fields(anon_client: APIClient, surprise_url: str) -> None:
    SurprisePageConfigFactory(heading="Hello!", subheading="You made it.")
    response = anon_client.get(surprise_url)
    data = response.json()
    assert data["heading"] == "Hello!"
    assert data["subheading"] == "You made it."
    assert data["image"] is None


def test_get_returns_image_url_when_image_set(anon_client: APIClient, surprise_url: str) -> None:
    config = SurprisePageConfigFactory()
    config.image.save("surprise.png", ContentFile(b"PNG"), save=True)

    response = anon_client.get(surprise_url)
    data = response.json()
    assert data["image"] is not None
    assert "surprise" in data["image"]
