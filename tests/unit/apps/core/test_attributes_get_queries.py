import datetime as dt
import uuid

from dateutil.relativedelta import relativedelta
from django.core.exceptions import ValidationError
from django.db.models import Q
import pytest

from hope.apps.core.attributes_qet_queries import (
    age_to_birth_date_query,
    age_to_birth_date_range_query,
    country_origin_query,
    country_query,
    extra_rdis_query,
    get_birth_certificate_document_number_query,
    get_birth_certificate_issuer_query,
    get_documents_issuer_query,
    get_drivers_license_document_number_query,
    get_drivers_licensee_issuer_query,
    get_electoral_card_document_number_query,
    get_electoral_card_issuer_query,
    get_has_bank_account_number_query,
    get_has_phone_number_query,
    get_has_tax_id_query,
    get_national_id_document_number_query,
    get_national_id_issuer_query,
    get_national_passport_document_number_query,
    get_national_passport_issuer_query,
    get_other_document_number_query,
    get_other_issuer_query,
    get_receiver_poi_issuer_query,
    get_receiver_poi_number_query,
    get_role_query,
    get_scope_id_issuer_query,
    get_scope_id_number_query,
    get_tax_id_document_number_query,
    get_tax_id_issuer_query,
    get_unhcr_id_issuer_query,
    get_unhcr_id_number_query,
    registration_data_import_query,
)
from hope.apps.core.countries import Countries
from hope.models import UNHCR, WFP

TODAY = dt.date.today()


def test_age_to_birth_date_range_query_min_only():
    q = age_to_birth_date_range_query("birth_date", 30, None)
    expected_date = TODAY - relativedelta(years=30)
    assert q == Q(birth_date__lte=expected_date)


def test_age_to_birth_date_range_query_max_only():
    q = age_to_birth_date_range_query("birth_date", None, 20)
    expected_date = TODAY - relativedelta(years=21)
    assert q == Q(birth_date__gt=expected_date)


def test_age_to_birth_date_range_query_min_and_max():
    q = age_to_birth_date_range_query("birth_date", 25, 35)
    expected_min_date = TODAY - relativedelta(years=25)
    expected_max_date = TODAY - relativedelta(years=36)
    assert q == Q(birth_date__lte=expected_min_date, birth_date__gt=expected_max_date)


def test_age_to_birth_date_query_equals():
    q = age_to_birth_date_query("EQUALS", [30])
    expected_date = TODAY - relativedelta(years=30)
    assert q == Q(
        birth_date__lte=expected_date,
        birth_date__gt=expected_date - relativedelta(years=1),
    )


def test_age_to_birth_date_query_not_equals():
    q = age_to_birth_date_query("NOT_EQUALS", [30])
    expected_date = TODAY - relativedelta(years=30)
    assert q == ~(
        Q(
            birth_date__lte=expected_date,
            birth_date__gt=expected_date - relativedelta(years=1),
        )
    )


def test_age_to_birth_date_query_range():
    q = age_to_birth_date_query("RANGE", [20, 30])
    expected_min_date = TODAY - relativedelta(years=20)
    expected_max_date = TODAY - relativedelta(years=31)
    assert q == Q(birth_date__lte=expected_min_date, birth_date__gt=expected_max_date)


def test_age_to_birth_date_query_not_in_range():
    q = age_to_birth_date_query("NOT_IN_RANGE", [20, 30])
    expected_min_date = TODAY - relativedelta(years=20)
    expected_max_date = TODAY - relativedelta(years=31)
    assert q == ~(Q(birth_date__lte=expected_min_date, birth_date__gt=expected_max_date))


def test_age_to_birth_date_query_greater_than():
    q = age_to_birth_date_query("GREATER_THAN", [25])
    expected_min_date = TODAY - relativedelta(years=25)
    assert q == Q(birth_date__lte=expected_min_date)


def test_age_to_birth_date_query_less_than():
    q = age_to_birth_date_query("LESS_THAN", [25])
    expected_max_date = TODAY - relativedelta(years=26)
    assert q == Q(birth_date__gt=expected_max_date)


def test_age_to_birth_date_query_invalid_comparison_method():
    with pytest.raises(ValidationError):
        age_to_birth_date_query("INVALID_METHOD", [25])


def test_age_to_birth_date_query_incorrect_argument_count():
    with pytest.raises(ValidationError):
        age_to_birth_date_query("EQUALS", [])


def test_country_query_equals():
    q = country_query("EQUALS", ["USA"])
    assert q == Q(country=Countries.get_country_value("USA"))


def test_country_query_not_equals():
    q = country_query("NOT_EQUALS", ["USA"])
    assert q == ~Q(country=Countries.get_country_value("USA"))


def test_country_query_invalid_comparison_method():
    with pytest.raises(ValidationError):
        country_query("INVALID_METHOD", ["USA"])


def test_registration_data_import_query():
    q = registration_data_import_query("EQUALS", [1, 2, 3])
    assert q == Q(registration_data_import__pk__in=[1, 2, 3])


@pytest.mark.parametrize(
    ("has_phone", "expected"),
    [
        (True, ~Q(phone_no="")),
        (False, Q(phone_no="")),
    ],
)
def test_get_has_phone_number_query(has_phone, expected):
    q = get_has_phone_number_query(None, [has_phone])
    assert q == expected


def test_get_birth_certificate_document_number_query():
    q = get_birth_certificate_document_number_query(None, ["1234"])
    assert q == Q(documents__type__key="birth_certificate", documents__document_number="1234")


def test_get_tax_id_document_number_query():
    q = get_tax_id_document_number_query(None, ["5678"])
    assert q == Q(documents__type__key="tax_id", documents__document_number="5678")


def test_get_drivers_license_document_number_query():
    q = get_drivers_license_document_number_query(None, ["ABCD"])
    assert q == Q(documents__type__key="drivers_license", documents__document_number="ABCD")


def test_get_national_id_document_number_query():
    q = get_national_id_document_number_query(None, ["EFGH"])
    assert q == Q(documents__type__key="national_id", documents__document_number="EFGH")


def test_get_national_passport_document_number_query():
    q = get_national_passport_document_number_query(None, ["IJKL"])
    assert q == Q(documents__type__key="national_passport", documents__document_number="IJKL")


def test_get_electoral_card_document_number_query():
    q = get_electoral_card_document_number_query(None, ["MNOP"])
    assert q == Q(documents__type__key="electoral_card", documents__document_number="MNOP")


def test_get_other_document_number_query():
    q = get_other_document_number_query(None, ["QRST"])
    assert q == Q(documents__type__key="other", documents__document_number="QRST")


@pytest.mark.parametrize(
    ("has_bank_account", "expected"),
    [
        (True, Q(accounts__account_type__key="bank")),
        (False, ~Q(accounts__account_type__key="bank")),
    ],
)
def test_get_has_bank_account_number_query(has_bank_account, expected):
    result = get_has_bank_account_number_query(None, [has_bank_account])
    assert result == expected


@pytest.mark.parametrize(
    ("has_tax_id", "is_social_worker", "expected"),
    [
        (True, False, Q(documents__type__key__iexact="TAX_ID")),
        (False, False, ~Q(documents__type__key__iexact="TAX_ID")),
        (True, True, Q(individuals__documents__type__key__iexact="TAX_ID")),
        (False, True, ~Q(individuals__documents__type__key__iexact="TAX_ID")),
    ],
)
def test_get_has_tax_id_query(has_tax_id, is_social_worker, expected):
    result = get_has_tax_id_query(None, [has_tax_id], is_social_worker_query=is_social_worker)
    assert result == expected


@pytest.mark.parametrize(
    ("is_social_worker", "expected"),
    [
        (False, Q(households_and_roles__role="manager")),
        (True, Q(individuals__households_and_roles__role="manager")),
    ],
)
def test_get_role_query(is_social_worker, expected):
    result = get_role_query(None, ["manager"], is_social_worker)
    assert result == expected


@pytest.mark.parametrize(
    ("is_social_worker", "expected"),
    [
        (False, Q(identities__partner__name=WFP, identities__number="123456")),
        (True, Q(individuals__identities__partner__name=WFP, individuals__identities__number="123456")),
    ],
)
def test_get_scope_id_number_query(is_social_worker, expected):
    result = get_scope_id_number_query(None, ["123456"], is_social_worker)
    assert result == expected


@pytest.mark.parametrize(
    ("is_social_worker", "expected"),
    [
        (False, Q(identities__partner__name=WFP, identities__country__iso_code3="KEN")),
        (True, Q(individuals__identities__partner__name=WFP, individuals__identities__country__iso_code3="KEN")),
    ],
)
def test_get_scope_id_issuer_query(is_social_worker, expected):
    result = get_scope_id_issuer_query(None, ["KEN"], is_social_worker)
    assert result == expected


@pytest.mark.parametrize(
    ("is_social_worker", "expected"),
    [
        (False, Q(identities__partner__name=UNHCR, identities__number="987654")),
        (True, Q(individuals__identities__partner__name=UNHCR, individuals__identities__number="987654")),
    ],
)
def test_get_unhcr_id_number_query(is_social_worker, expected):
    result = get_unhcr_id_number_query(None, ["987654"], is_social_worker)
    assert result == expected


@pytest.mark.parametrize(
    ("is_social_worker", "expected"),
    [
        (False, Q(identities__partner__name=UNHCR, identities__country__iso_code3="UGA")),
        (True, Q(individuals__identities__partner__name=UNHCR, individuals__identities__country__iso_code3="UGA")),
    ],
)
def test_get_unhcr_id_issuer_query(is_social_worker, expected):
    result = get_unhcr_id_issuer_query(None, ["UGA"], is_social_worker)
    assert result == expected


def test_get_national_id_issuer_query():
    expected = Q(
        documents__type__type="NATIONAL_ID",
        documents__type__country__iso_code3="USA",
    )
    result = get_national_id_issuer_query(None, ["USA"])
    assert result == expected


def test_get_national_passport_issuer_query():
    expected = Q(
        documents__type__type="NATIONAL_PASSPORT",
        documents__type__country__iso_code3="GBR",
    )
    result = get_national_passport_issuer_query(None, ["GBR"])
    assert result == expected


def test_get_electoral_card_issuer_query():
    expected = Q(
        documents__type__type="ELECTORAL_CARD",
        documents__type__country__iso_code3="IND",
    )
    result = get_electoral_card_issuer_query(None, ["IND"])
    assert result == expected


def test_get_documents_issuer_query():
    expected = Q(
        documents__type__type="GENERIC_TYPE",
        documents__type__country__iso_code3="FRA",
    )
    result = get_documents_issuer_query("GENERIC_TYPE", "FRA")
    assert result == expected


def test_get_receiver_poi_number_query():
    expected = Q(documents__type__key="receiver_poi", documents__document_number="12345")
    result = get_receiver_poi_number_query(None, ["12345"])
    assert result == expected


def test_get_receiver_poi_issuer_query():
    expected = Q(
        documents__type__type="receiver_poi",
        documents__type__country__iso_code3="CAN",
    )
    result = get_receiver_poi_issuer_query(None, ["CAN"])
    assert result == expected


def test_country_origin_query_equals():
    expected = Q(individuals__country_origin="CA")
    result = country_origin_query("EQUALS", ["CAN"], is_social_worker_query=True)
    assert result == expected


def test_country_origin_query_not_equals():
    expected = ~Q(individuals__country_origin="CA")
    result = country_origin_query("NOT_EQUALS", ["CAN"], is_social_worker_query=True)
    assert result == expected


def test_country_origin_query_invalid_comparison():
    with pytest.raises(ValidationError):
        country_origin_query("INVALID", ["CAN"], is_social_worker_query=True)


def test_get_birth_certificate_issuer_query():
    country_code = "USA"
    result = get_birth_certificate_issuer_query(None, [country_code])
    expected = Q(
        documents__type__type="BIRTH_CERTIFICATE",
        documents__type__country__iso_code3=country_code,
    )
    assert result == expected


def test_get_tax_id_issuer_query():
    country_code = "GBR"
    result = get_tax_id_issuer_query(None, [country_code])
    expected = Q(
        documents__type__type="TAX_ID",
        documents__type__country__iso_code3=country_code,
    )
    assert result == expected


def test_get_drivers_licensee_issuer_query():
    country_code = "CAN"
    result = get_drivers_licensee_issuer_query(None, [country_code])
    expected = Q(
        documents__type__type="DRIVERS_LICENSE",
        documents__type__country__iso_code3=country_code,
    )
    assert result == expected


def test_get_other_issuer_query():
    country_code = "AUS"
    result = get_other_issuer_query(None, [country_code])
    expected = Q(
        documents__type__type="OTHER",
        documents__type__country__iso_code3=country_code,
    )
    assert result == expected


def test_extra_rdis_query():
    rdis_uuids = [uuid.uuid4(), uuid.uuid4()]
    result = extra_rdis_query("CONTAINS", rdis_uuids)
    expected = Q(extra_rdis__in=rdis_uuids)
    assert result == expected
