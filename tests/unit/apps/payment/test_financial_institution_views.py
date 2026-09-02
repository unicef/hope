from typing import Any, Callable

from django.urls import reverse
import pytest
from rest_framework import status
from rest_framework.test import APIClient

from extras.test_utils.factories import (
    BusinessAreaFactory,
    CountryFactory,
    FinancialInstitutionFactory,
    UserFactory,
)

pytestmark = pytest.mark.django_db


@pytest.fixture
def afghanistan() -> Any:
    business_area = BusinessAreaFactory(name="Afghanistan", slug="afghanistan", code="0060")
    business_area.countries.add(CountryFactory(name="Afghanistan", iso_code2="AF", iso_code3="AFG", iso_num="0004"))
    return business_area


@pytest.fixture
def ukraine() -> Any:
    business_area = BusinessAreaFactory(name="Ukraine", slug="ukraine", code="4410")
    business_area.countries.add(CountryFactory(name="Ukraine", iso_code2="UA", iso_code3="UKR", iso_num="0804"))
    return business_area


@pytest.fixture
def user() -> Any:
    return UserFactory()


@pytest.fixture
def client(api_client: Callable, user: Any) -> Any:
    return api_client(user)


def _choices_url(business_area_slug: str) -> str:
    return reverse(
        "api:payments:financial-institutions-choices",
        kwargs={"business_area_slug": business_area_slug},
    )


def test_choices_returns_only_institutions_of_the_business_area(
    client: Any,
    afghanistan: Any,
    ukraine: Any,
) -> None:
    afghan_institution = FinancialInstitutionFactory(name="Afghan Bank", country=afghanistan.countries.first())
    FinancialInstitutionFactory(name="Ukrainian Bank", country=ukraine.countries.first())
    countryless_institution = FinancialInstitutionFactory(name="Generic Bank", country=None)

    response = client.get(_choices_url(afghanistan.slug))

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [
        {"name": "Afghan Bank", "value": afghan_institution.id},
        {"name": "Generic Bank", "value": countryless_institution.id},
    ]


def test_choices_returns_countryless_institutions_in_every_business_area(
    client: Any,
    afghanistan: Any,
    ukraine: Any,
) -> None:
    FinancialInstitutionFactory(name="Afghan Bank", country=afghanistan.countries.first())
    countryless_institution = FinancialInstitutionFactory(name="Generic Bank", country=None)

    response = client.get(_choices_url(ukraine.slug))

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [{"name": "Generic Bank", "value": countryless_institution.id}]


def test_choices_allows_authenticated_user_without_any_role(client: Any, afghanistan: Any) -> None:
    institution = FinancialInstitutionFactory(name="Generic Bank", country=None)

    response = client.get(_choices_url(afghanistan.slug))

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [{"name": "Generic Bank", "value": institution.id}]


def test_choices_denies_anonymous_access(afghanistan: Any) -> None:
    FinancialInstitutionFactory(name="Generic Bank", country=None)

    response = APIClient().get(_choices_url(afghanistan.slug))

    assert response.status_code == status.HTTP_403_FORBIDDEN
