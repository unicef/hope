from typing import Callable

import pytest

from extras.test_utils.factories.account import PartnerFactory
from extras.test_utils.factories.geo import CountryFactory
from extras.test_utils.factories.household import (
    DocumentFactory,
    IndividualFactory,
    IndividualIdentityFactory,
)
from hope.apps.core.field_attributes.lookup_functions import (
    get_birth_certificate_issuer,
    get_birth_certificate_no,
    get_document_issuer,
    get_document_no,
    get_drivers_license_issuer,
    get_drivers_license_no,
    get_electoral_card_issuer,
    get_electoral_card_no,
    get_national_id_issuer,
    get_national_id_no,
    get_national_passport_issuer,
    get_national_passport_no,
    get_other_id_issuer,
    get_other_id_no,
    get_scope_id_issuer,
    get_scope_id_no,
    get_tax_id_issuer,
    get_tax_id_no,
    get_unhcr_id_issuer,
    get_unhcr_id_no,
)
from hope.apps.household.const import (
    IDENTIFICATION_TYPE_BIRTH_CERTIFICATE,
    IDENTIFICATION_TYPE_DRIVERS_LICENSE,
    IDENTIFICATION_TYPE_ELECTORAL_CARD,
    IDENTIFICATION_TYPE_NATIONAL_ID,
    IDENTIFICATION_TYPE_NATIONAL_PASSPORT,
    IDENTIFICATION_TYPE_OTHER,
    IDENTIFICATION_TYPE_TAX_ID,
    UNHCR,
    WFP,
)
from hope.models import Individual

pytestmark = pytest.mark.django_db


DOCUMENT_NO_FUNCTIONS = [
    (get_birth_certificate_no, IDENTIFICATION_TYPE_BIRTH_CERTIFICATE),
    (get_tax_id_no, IDENTIFICATION_TYPE_TAX_ID),
    (get_drivers_license_no, IDENTIFICATION_TYPE_DRIVERS_LICENSE),
    (get_electoral_card_no, IDENTIFICATION_TYPE_ELECTORAL_CARD),
    (get_national_passport_no, IDENTIFICATION_TYPE_NATIONAL_PASSPORT),
    (get_national_id_no, IDENTIFICATION_TYPE_NATIONAL_ID),
    (get_other_id_no, IDENTIFICATION_TYPE_OTHER),
]

DOCUMENT_ISSUER_FUNCTIONS = [
    (get_birth_certificate_issuer, IDENTIFICATION_TYPE_BIRTH_CERTIFICATE),
    (get_tax_id_issuer, IDENTIFICATION_TYPE_TAX_ID),
    (get_drivers_license_issuer, IDENTIFICATION_TYPE_DRIVERS_LICENSE),
    (get_electoral_card_issuer, IDENTIFICATION_TYPE_ELECTORAL_CARD),
    (get_national_passport_issuer, IDENTIFICATION_TYPE_NATIONAL_PASSPORT),
    (get_national_id_issuer, IDENTIFICATION_TYPE_NATIONAL_ID),
    (get_other_id_issuer, IDENTIFICATION_TYPE_OTHER),
]


@pytest.fixture
def individual() -> Individual:
    return IndividualFactory()


@pytest.mark.parametrize(("function", "identification_type"), DOCUMENT_NO_FUNCTIONS)
def test_get_document_no_returns_document_number(function: Callable, identification_type: str) -> None:
    document = DocumentFactory(type__key=identification_type.lower(), document_number="DOC-123")

    assert function(document.individual) == "DOC-123"


def test_get_document_no_returns_empty_string_when_no_document(individual: Individual) -> None:
    assert get_birth_certificate_no(individual) == ""


def test_get_document_no_ignores_other_document_types(individual: Individual) -> None:
    DocumentFactory(
        individual=individual,
        type__key=IDENTIFICATION_TYPE_TAX_ID.lower(),
        document_number="TAX-1",
    )

    assert get_document_no(individual, IDENTIFICATION_TYPE_NATIONAL_ID) == ""


@pytest.mark.parametrize(("function", "identification_type"), DOCUMENT_ISSUER_FUNCTIONS)
def test_get_document_issuer_returns_country_iso_code3(function: Callable, identification_type: str) -> None:
    country = CountryFactory(iso_code3="POL")
    document = DocumentFactory(type__key=identification_type.lower(), country=country)

    assert function(document.individual) == "POL"


def test_get_document_issuer_returns_empty_string_when_no_document(individual: Individual) -> None:
    assert get_birth_certificate_issuer(individual) == ""


def test_get_document_issuer_returns_empty_string_when_document_has_no_country(individual: Individual) -> None:
    DocumentFactory(
        individual=individual,
        type__key=IDENTIFICATION_TYPE_BIRTH_CERTIFICATE.lower(),
        country=None,
    )

    assert get_document_issuer(individual, IDENTIFICATION_TYPE_BIRTH_CERTIFICATE) == ""


def test_get_unhcr_id_no_returns_identity_number(individual: Individual) -> None:
    IndividualIdentityFactory(individual=individual, partner=PartnerFactory(name=UNHCR), number="UNHCR-1")

    assert get_unhcr_id_no(individual) == "UNHCR-1"


def test_get_unhcr_id_no_returns_empty_string_when_no_identity(individual: Individual) -> None:
    assert get_unhcr_id_no(individual) == ""


def test_get_unhcr_id_issuer_returns_country_iso_code3(individual: Individual) -> None:
    IndividualIdentityFactory(
        individual=individual,
        partner=PartnerFactory(name=UNHCR),
        country=CountryFactory(iso_code3="UGA"),
    )

    assert get_unhcr_id_issuer(individual) == "UGA"


def test_get_unhcr_id_issuer_returns_empty_string_when_no_identity(individual: Individual) -> None:
    assert get_unhcr_id_issuer(individual) == ""


def test_get_scope_id_no_returns_identity_number(individual: Individual) -> None:
    IndividualIdentityFactory(individual=individual, partner=PartnerFactory(name=WFP), number="WFP-1")

    assert get_scope_id_no(individual) == "WFP-1"


def test_get_scope_id_no_returns_empty_string_when_no_identity(individual: Individual) -> None:
    assert get_scope_id_no(individual) == ""


def test_get_scope_id_issuer_returns_country_iso_code3(individual: Individual) -> None:
    IndividualIdentityFactory(
        individual=individual,
        partner=PartnerFactory(name=WFP),
        country=CountryFactory(iso_code3="KEN"),
    )

    assert get_scope_id_issuer(individual) == "KEN"


def test_get_scope_id_issuer_returns_empty_string_when_no_identity(individual: Individual) -> None:
    assert get_scope_id_issuer(individual) == ""
