from django.urls import reverse
import pytest

from extras.test_utils.factories import BusinessAreaFactory, ProgramFactory
from hope.models import Program, UniversalUpdate, User

pytestmark = pytest.mark.django_db


@pytest.fixture
def admin_user():
    return User.objects.create_superuser(
        username="root",
        email="root@root.com",
        password="password",
    )


@pytest.fixture
def client_logged(client, admin_user):
    client.login(username="root", password="password")
    return client


@pytest.fixture
def business_area():
    return BusinessAreaFactory(code="0060", slug="afghanistan", name="Afghanistan", active=True)


@pytest.fixture
def program(business_area):
    return ProgramFactory(
        name="Test Program for Household",
        status=Program.ACTIVE,
        business_area=business_area,
    )


def test_universal_update_admin_edit_page_loads(client_logged, program):
    universal_update = UniversalUpdate.objects.create(
        program=program,
        individual_fields=["given_name", "family_name"],
    )

    url = reverse(
        "admin:universal_update_script_universalupdate_change",
        args=(universal_update.pk,),
    )

    response = client_logged.get(url)

    assert response.status_code == 200
    assert "Test Program for Household" in response.content.decode()
