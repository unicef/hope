import uuid

from django.test import Client
from django.urls import reverse
import pytest

from extras.test_utils.factories import BusinessAreaFactory, ProgramFactory, UserFactory
from hope.apps.registration_data.views import download_template
from hope.models import BusinessArea, Program, User

pytestmark = pytest.mark.django_db


@pytest.fixture
def afghanistan() -> BusinessArea:
    return BusinessAreaFactory(name="Afghanistan", slug="afghanistan")


@pytest.fixture
def user() -> User:
    return UserFactory()


@pytest.fixture
def program(afghanistan: BusinessArea) -> Program:
    return ProgramFactory(business_area=afghanistan)


def test_download_template_returns_xlsx_for_existing_program(client: Client, user: User, program: Program) -> None:
    client.force_login(user)
    response = client.get(reverse(download_template, args=[str(program.id)]))

    assert response.status_code == 200
    assert response["Content-Type"] == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    assert response["Content-Disposition"] == "attachment; filename=registration_data_import_template.xlsx"
    assert len(response.content) > 0


def test_download_template_returns_404_for_missing_program(client: Client, user: User) -> None:
    client.force_login(user)
    response = client.get(reverse(download_template, args=[str(uuid.uuid4())]))

    assert response.status_code == 404
