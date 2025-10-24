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
from hope.apps.household.models import UNHCR, WFP


class TestAttributesGetQueries:
    @pytest.fixture(autouse=True)
    def setUp(self) -> None:
        self.today = dt.date.today()
        self.social_worker_prefix = "individuals__"

    def test_age_to_birth_date_range_query_min_only(self) -> None:
        q = age_to_birth_date_range_query("birth_date", 30, None)
        expected_date = self.today - relativedelta(years=30)
        assert q == Q(birth_date__lte=expected_date)

    def test_age_to_birth_date_range_query_max_only(self) -> None:
        q = age_to_birth_date_range_query("birth_date", None, 20)
        expected_date = self.today - relativedelta(years=21)
        assert q == Q(birth_date__gt=expected_date)

    def test_age_to_birth_date_range_query_min_and_max(self) -> None:
        q = age_to_birth_date_range_query("birth_date", 25, 35)
        expected_min_date = self.today - relativedelta(years=25)
        expected_max_date = self.today - relativedelta(years=36)
        assert q == Q(birth_date__lte=expected_min_date, birth_date__gt=expected_max_date)

    def test_age_to_birth_date_query_equals(self) -> None:
        q = age_to_birth_date_query("EQUALS", [30])
        expected_date = self.today - relativedelta(years=30)
        assert q == Q(
            birth_date__lte=expected_date,
            birth_date__gt=expected_date - relativedelta(years=1),
        )

    def test_age_to_birth_date_query_not_equals(self) -> None:
        q = age_to_birth_date_query("NOT_EQUALS", [30])
        expected_date = self.today - relativedelta(years=30)
        assert q == ~(
            Q(
                birth_date__lte=expected_date,
                birth_date__gt=expected_date - relativedelta(years=1),
            )
        )

    def test_age_to_birth_date_query_range(self) -> None:
        q = age_to_birth_date_query("RANGE", [20, 30])
        expected_min_date = self.today - relativedelta(years=20)
        expected_max_date = self.today - relativedelta(years=31)
        assert q == Q(birth_date__lte=expected_min_date, birth_date__gt=expected_max_date)

    def test_age_to_birth_date_query_not_in_range(self) -> None:
        q = age_to_birth_date_query("NOT_IN_RANGE", [20, 30])
        expected_min_date = self.today - relativedelta(years=20)
        expected_max_date = self.today - relativedelta(years=31)
        assert q == ~(Q(birth_date__lte=expected_min_date, birth_date__gt=expected_max_date))

    def test_age_to_birth_date_query_greater_than(self) -> None:
        q = age_to_birth_date_query("GREATER_THAN", [25])
        expected_min_date = self.today - relativedelta(years=25)
        assert q == Q(birth_date__lte=expected_min_date)

    def test_age_to_birth_date_query_less_than(self) -> None:
        q = age_to_birth_date_query("LESS_THAN", [25])
        expected_max_date = self.today - relativedelta(years=26)
        assert q == Q(birth_date__gt=expected_max_date)

    def test_invalid_comparison_method(self) -> None:
        with pytest.raises(ValidationError):
            age_to_birth_date_query("INVALID_METHOD", [25])

    def test_incorrect_argument_count(self) -> None:
        with pytest.raises(ValidationError):
            age_to_birth_date_query("EQUALS", [])

    def test_country_query_equals(self) -> None:
        q = country_query("EQUALS", ["USA"])
        assert q == Q(country=Countries.get_country_value("USA"))

    def test_country_query_not_equals(self) -> None:
        q = country_query("NOT_EQUALS", ["USA"])
        assert q == ~Q(country=Countries.get_country_value("USA"))

    def test_registration_data_import_query(self) -> None:
        q = registration_data_import_query("EQUALS", [1, 2, 3])
        assert q == Q(registration_data_import__pk__in=[1, 2, 3])

    def test_invalid_country_comparison_method(self) -> None:
        with pytest.raises(ValidationError):
            country_query("INVALID_METHOD", ["USA"])

    def test_get_has_phone_number_query_true(self) -> None:
        q = get_has_phone_number_query(None, [True])
        assert q == ~Q(phone_no="")

    def test_get_has_phone_number_query_false(self) -> None:
        q = get_has_phone_number_query(None, [False])
        assert q == Q(phone_no="")

    def test_get_birth_certificate_document_number_query(self) -> None:
        q = get_birth_certificate_document_number_query(None, ["1234"])
        assert q == Q(documents__type__key="birth_certificate", documents__document_number="1234")

    def test_get_tax_id_document_number_query(self) -> None:
        q = get_tax_id_document_number_query(None, ["5678"])
        assert q == Q(documents__type__key="tax_id", documents__document_number="5678")

    def test_get_drivers_license_document_number_query(self) -> None:
        q = get_drivers_license_document_number_query(None, ["ABCD"])
        assert q == Q(documents__type__key="drivers_license", documents__document_number="ABCD")

    def test_get_national_id_document_number_query(self) -> None:
        q = get_national_id_document_number_query(None, ["EFGH"])
        assert q == Q(documents__type__key="national_id", documents__document_number="EFGH")

    def test_get_national_passport_document_number_query(self) -> None:
        q = get_national_passport_document_number_query(None, ["IJKL"])
        assert q == Q(documents__type__key="national_passport", documents__document_number="IJKL")

    def test_get_electoral_card_document_number_query(self) -> None:
        q = get_electoral_card_document_number_query(None, ["MNOP"])
        assert q == Q(documents__type__key="electoral_card", documents__document_number="MNOP")

    def test_get_other_document_number_query(self) -> None:
        q = get_other_document_number_query(None, ["QRST"])
        assert q == Q(documents__type__key="other", documents__document_number="QRST")

    def test_get_has_bank_account_number_query_true(self) -> None:
        expected_query = Q(accounts__account_type__key="bank")
        result = get_has_bank_account_number_query(None, [True])
        assert result == expected_query

    def test_get_has_bank_account_number_query_false(self) -> None:
        expected_query = ~Q(accounts__account_type__key="bank")
        result = get_has_bank_account_number_query(None, [False])
        assert result == expected_query

    def test_get_has_tax_id_query_true(self) -> None:
        # Test for individuals who have a tax ID
        expected_query = Q(documents__type__key__iexact="TAX_ID")
        result = get_has_tax_id_query(None, [True])
        assert result == expected_query

    def test_get_has_tax_id_query_false(self) -> None:
        # Test for individuals who do not have a tax ID
        expected_query = ~Q(documents__type__key__iexact="TAX_ID")
        result = get_has_tax_id_query(None, [False])
        assert result == expected_query

    def test_get_has_tax_id_query_social_worker_true(self) -> None:
        # Test with social worker prefix for individuals who have a tax ID
        expected_query = Q(individuals__documents__type__key__iexact="TAX_ID")
        result = get_has_tax_id_query(None, [True], is_social_worker_query=True)
        assert result == expected_query

    def test_get_has_tax_id_query_social_worker_false(self) -> None:
        # Test with social worker prefix for individuals who do not have a tax ID
        expected_query = ~Q(individuals__documents__type__key__iexact="TAX_ID")
        result = get_has_tax_id_query(None, [False], is_social_worker_query=True)
        assert result == expected_query

    def test_get_role_query(self) -> None:
        # Without social worker prefix
        expected = Q(households_and_roles__role="manager")
        result = get_role_query(None, ["manager"])
        assert result == expected

        # With social worker prefix
        expected = Q(individuals__households_and_roles__role="manager")
        result = get_role_query(None, ["manager"], True)
        assert result == expected

    def test_get_scope_id_number_query(self) -> None:
        # Without social worker prefix
        expected = Q(identities__partner__name=WFP, identities__number="123456")
        result = get_scope_id_number_query(None, ["123456"])
        assert result == expected

        # With social worker prefix
        expected = Q(
            individuals__identities__partner__name=WFP,
            individuals__identities__number="123456",
        )
        result = get_scope_id_number_query(None, ["123456"], True)
        assert result == expected

    def test_get_scope_id_issuer_query(self) -> None:
        # Without social worker prefix
        expected = Q(identities__partner__name=WFP, identities__country__iso_code3="KEN")
        result = get_scope_id_issuer_query(None, ["KEN"])
        assert result == expected

        # With social worker prefix
        expected = Q(
            individuals__identities__partner__name=WFP,
            individuals__identities__country__iso_code3="KEN",
        )
        result = get_scope_id_issuer_query(None, ["KEN"], True)
        assert result == expected

    def test_get_unhcr_id_number_query(self) -> None:
        # Without social worker prefix
        expected = Q(identities__partner__name=UNHCR, identities__number="987654")
        result = get_unhcr_id_number_query(None, ["987654"])
        assert result == expected

        # With social worker prefix
        expected = Q(
            individuals__identities__partner__name=UNHCR,
            individuals__identities__number="987654",
        )
        result = get_unhcr_id_number_query(None, ["987654"], True)
        assert result == expected

    def test_get_unhcr_id_issuer_query(self) -> None:
        # Without social worker prefix
        expected = Q(identities__partner__name=UNHCR, identities__country__iso_code3="UGA")
        result = get_unhcr_id_issuer_query(None, ["UGA"])
        assert result == expected

        expected = Q(
            individuals__identities__partner__name=UNHCR,
            individuals__identities__country__iso_code3="UGA",
        )
        result = get_unhcr_id_issuer_query(None, ["UGA"], True)
        assert result == expected

    def test_get_national_id_issuer_query(self) -> None:
        expected = Q(
            documents__type__type="NATIONAL_ID",
            documents__type__country__iso_code3="USA",
        )
        result = get_national_id_issuer_query(None, ["USA"])
        assert result == expected

    def test_get_national_passport_issuer_query(self) -> None:
        expected = Q(
            documents__type__type="NATIONAL_PASSPORT",
            documents__type__country__iso_code3="GBR",
        )
        result = get_national_passport_issuer_query(None, ["GBR"])
        assert result == expected

    def test_get_electoral_card_issuer_query(self) -> None:
        expected = Q(
            documents__type__type="ELECTORAL_CARD",
            documents__type__country__iso_code3="IND",
        )
        result = get_electoral_card_issuer_query(None, ["IND"])
        assert result == expected

    def test_get_documents_issuer_query(self) -> None:
        expected = Q(
            documents__type__type="GENERIC_TYPE",
            documents__type__country__iso_code3="FRA",
        )
        result = get_documents_issuer_query("GENERIC_TYPE", "FRA")
        assert result == expected

    def test_get_receiver_poi_number_query(self) -> None:
        expected = Q(documents__type__key="receiver_poi", documents__document_number="12345")
        result = get_receiver_poi_number_query(None, ["12345"])
        assert result == expected

    def test_get_receiver_poi_issuer_query(self) -> None:
        expected = Q(
            documents__type__type="receiver_poi",
            documents__type__country__iso_code3="CAN",
        )
        result = get_receiver_poi_issuer_query(None, ["CAN"])
        assert result == expected

    def test_country_origin_query_equals(self) -> None:
        expected = Q(individuals__country_origin="CA")
        result = country_origin_query("EQUALS", ["CAN"], is_social_worker_query=True)
        assert result == expected

    def test_country_origin_query_not_equals(self) -> None:
        expected = ~Q(individuals__country_origin="CA")
        result = country_origin_query("NOT_EQUALS", ["CAN"], is_social_worker_query=True)
        assert result == expected

    def test_invalid_country_origin_comparison(self) -> None:
        with pytest.raises(ValidationError):
            country_origin_query("INVALID", ["CAN"], is_social_worker_query=True)

    def test_get_birth_certificate_issuer_query(self) -> None:
        country_code = "USA"
        result = get_birth_certificate_issuer_query(None, [country_code])
        expected = Q(
            documents__type__type="BIRTH_CERTIFICATE",
            documents__type__country__iso_code3=country_code,
        )
        assert result == expected

    def test_get_tax_id_issuer_query(self) -> None:
        country_code = "GBR"
        result = get_tax_id_issuer_query(None, [country_code])
        expected = Q(
            documents__type__type="TAX_ID",
            documents__type__country__iso_code3=country_code,
        )
        assert result == expected

    def test_get_drivers_licensee_issuer_query(self) -> None:
        country_code = "CAN"
        result = get_drivers_licensee_issuer_query(None, [country_code])
        expected = Q(
            documents__type__type="DRIVERS_LICENSE",
            documents__type__country__iso_code3=country_code,
        )
        assert result == expected

    def test_get_other_issuer_query(self) -> None:
        country_code = "AUS"
        result = get_other_issuer_query(None, [country_code])
        expected = Q(
            documents__type__type="OTHER",
            documents__type__country__iso_code3=country_code,
        )
        assert result == expected

    def test_get_extra_rdis_query(self) -> None:
        rdis_uuids = [uuid.uuid4(), uuid.uuid4()]
        result = extra_rdis_query("CONTAINS", rdis_uuids)
        expected = Q(extra_rdis__in=rdis_uuids)
        assert result == expected
