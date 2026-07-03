from unittest.mock import patch

import pytest
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

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


def test_get_returns_defaults(anon_client: APIClient, surprise_url: str) -> None:
    with patch("hope.api.endpoints.surprise.config") as mock_config:
        mock_config.SURPRISE_PAGE_IMAGE = ""
        mock_config.SURPRISE_PAGE_HEADING = "🎉 You found a secret!"
        mock_config.SURPRISE_PAGE_SUBHEADING = "Congratulations, explorer."
        response = anon_client.get(surprise_url)
    data = response.json()
    assert data["image"] is None
    assert data["heading"] == "🎉 You found a secret!"
    assert data["subheading"] == "Congratulations, explorer."


def test_get_returns_custom_text(anon_client: APIClient, surprise_url: str) -> None:
    with patch("hope.api.endpoints.surprise.config") as mock_config:
        mock_config.SURPRISE_PAGE_IMAGE = ""
        mock_config.SURPRISE_PAGE_HEADING = "Hello!"
        mock_config.SURPRISE_PAGE_SUBHEADING = "You made it."
        response = anon_client.get(surprise_url)
    data = response.json()
    assert data["heading"] == "Hello!"
    assert data["subheading"] == "You made it."
    assert data["image"] is None


def test_get_returns_image_url_when_image_set(anon_client: APIClient, surprise_url: str) -> None:
    with patch("hope.api.endpoints.surprise.config") as mock_config:
        mock_config.SURPRISE_PAGE_IMAGE = "surprise/photo.png"
        mock_config.SURPRISE_PAGE_HEADING = "🎉 You found a secret!"
        mock_config.SURPRISE_PAGE_SUBHEADING = "Congratulations, explorer."
        response = anon_client.get(surprise_url)
    data = response.json()
    assert data["image"] is not None
    assert data["image"].startswith("/")
    assert "surprise/photo.png" in data["image"]
