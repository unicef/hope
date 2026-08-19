"""Cross business area scoping of the field attribute lookup (GHSA-2xf8-jjc2-9pmv).

The business area comes from the url path, the program whose flexible fields are read comes as a
global id in the query, so the two have to be reconciled.
"""

from typing import Any, Callable

import pytest
from rest_framework import status
from rest_framework.reverse import reverse

from extras.test_utils.factories import BusinessAreaFactory, FlexibleAttributeForPDUFactory, ProgramFactory, UserFactory
from hope.models import BusinessArea, Program, User

pytestmark = pytest.mark.django_db


@pytest.fixture
def attacker_business_area() -> BusinessArea:
    return BusinessAreaFactory(name="Afghanistan", slug="afghanistan")


@pytest.fixture
def attacker(attacker_business_area: BusinessArea, create_user_role_with_permissions: Callable) -> User:
    user = UserFactory()
    create_user_role_with_permissions(user, [], attacker_business_area, whole_business_area_access=True)
    return user


@pytest.fixture
def authenticated_client(api_client: Callable, attacker: User) -> Any:
    return api_client(attacker)


@pytest.fixture
def victim_program() -> Program:
    program = ProgramFactory(business_area=BusinessAreaFactory(name="Ukraine", slug="ukraine"))
    FlexibleAttributeForPDUFactory(program=program, label="Secret round")
    return program


@pytest.fixture
def url(attacker_business_area: BusinessArea) -> str:
    return reverse("api:core:business-areas-all-fields-attributes", kwargs={"slug": attacker_business_area.slug})


def test_read_field_attributes_of_program_from_other_business_area_is_denied(
    authenticated_client: Any, url: str, victim_program: Program
) -> None:
    response = authenticated_client.get(url, {"program_id": str(victim_program.id)})

    assert response.status_code == status.HTTP_404_NOT_FOUND, response.status_code
