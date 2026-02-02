import pytest
from rest_framework import status
from rest_framework.test import APIClient

from extras.test_utils.factories.account import UserFactory

pytestmark = pytest.mark.django_db


@pytest.fixture()
def authenticated_client(db):
    user = UserFactory(is_staff=True, is_superuser=True)
    client = APIClient()
    client.force_authenticate(user=user)
    return client


def test_openapi_schema_returns_200(authenticated_client):
    response = authenticated_client.get("/api/rest/")
    assert response.status_code == status.HTTP_200_OK


def test_swagger_ui_returns_200(authenticated_client):
    response = authenticated_client.get("/api/rest/swagger/")
    assert response.status_code == status.HTTP_200_OK


def test_redoc_returns_200(authenticated_client):
    response = authenticated_client.get("/api/rest/redoc/")
    assert response.status_code == status.HTTP_200_OK
