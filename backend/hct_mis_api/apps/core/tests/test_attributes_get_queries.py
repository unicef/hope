import datetime as dt

from django.core.exceptions import ValidationError
from django.db.models import Q

from dateutil.relativedelta import relativedelta

from hct_mis_api.apps.core.attributes_qet_queries import (
    age_to_birth_date_query,
    age_to_birth_date_range_query,
    country_query,
    get_birth_certificate_document_number_query,
    get_drivers_license_document_number_query,
    get_electoral_card_document_number_query,
    get_has_bank_account_number_query,
    get_has_phone_number_query,
    get_has_tax_id_query,
    get_national_id_document_number_query,
    get_national_passport_document_number_query,
    get_other_document_number_query,
    get_role_query,
    get_scope_id_issuer_query,
    get_scope_id_number_query,
    get_tax_id_document_number_query,
    get_unhcr_id_issuer_query,
    get_unhcr_id_number_query,
    registration_data_import_query,
)
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.countries import Countries
from hct_mis_api.apps.household.models import UNHCR, WFP


class TestAttributesGetQueries(APITestCase):
    def setUp(self) -> None:
        self.today = dt.date.today()
        self.social_worker_prefix = "individuals__"
        super().setUp()

    def test_age_to_birth_date_range_query_min_only(self) -> None:
        q = age_to_birth_date_range_query("birth_date", 30, None)
        expected_date = self.today - relativedelta(years=30)
        self.assertEqual(q, Q(birth_date__lte=expected_date))

    def test_age_to_birth_date_range_query_max_only(self) -> None:
        q = age_to_birth_date_range_query("birth_date", None, 20)
        expected_date = self.today - relativedelta(years=21)
        self.assertEqual(q, Q(birth_date__gt=expected_date))

    def test_age_to_birth_date_range_query_min_and_max(self) -> None:
        q = age_to_birth_date_range_query("birth_date", 25, 35)
        expected_min_date = self.today - relativedelta(years=25)
        expected_max_date = self.today - relativedelta(years=36)
        self.assertEqual(q, Q(birth_date__lte=expected_min_date, birth_date__gt=expected_max_date))

    def test_age_to_birth_date_query_equals(self) -> None:
        q = age_to_birth_date_query("EQUALS", [30])
        expected_date = self.today - relativedelta(years=30)
        print("*" * 399)
        print(q)
        print(Q(birth_date__lte=expected_date, birth_date__gt=expected_date - relativedelta(years=1)))
        self.assertEqual(q, Q(birth_date__lte=expected_date, birth_date__gt=expected_date - relativedelta(years=1)))

    def test_age_to_birth_date_query_not_equals(self) -> None:
        q = age_to_birth_date_query("NOT_EQUALS", [30])
        expected_date = self.today - relativedelta(years=30)
        self.assertEqual(q, ~(Q(birth_date__lte=expected_date, birth_date__gt=expected_date - relativedelta(years=1))))

    def test_age_to_birth_date_query_range(self) -> None:
        q = age_to_birth_date_query("RANGE", [20, 30])
        expected_min_date = self.today - relativedelta(years=20)
        expected_max_date = self.today - relativedelta(years=31)
        self.assertEqual(q, Q(birth_date__lte=expected_min_date, birth_date__gt=expected_max_date))

    def test_age_to_birth_date_query_not_in_range(self) -> None:
        q = age_to_birth_date_query("NOT_IN_RANGE", [20, 30])
        expected_min_date = self.today - relativedelta(years=20)
        expected_max_date = self.today - relativedelta(years=31)
        self.assertEqual(q, ~(Q(birth_date__lte=expected_min_date, birth_date__gt=expected_max_date)))

    def test_age_to_birth_date_query_greater_than(self) -> None:
        q = age_to_birth_date_query("GREATER_THAN", [25])
        expected_min_date = self.today - relativedelta(years=25)
        self.assertEqual(q, Q(birth_date__lte=expected_min_date))

    def test_age_to_birth_date_query_less_than(self) -> None:
        q = age_to_birth_date_query("LESS_THAN", [25])
        expected_max_date = self.today - relativedelta(years=26)
        self.assertEqual(q, Q(birth_date__gt=expected_max_date))

    def test_invalid_comparison_method(self) -> None:
        with self.assertRaises(ValidationError):
            age_to_birth_date_query("INVALID_METHOD", [25])

    def test_incorrect_argument_count(self) -> None:
        with self.assertRaises(ValidationError):
            age_to_birth_date_query("EQUALS", [])

    def test_country_query_equals(self) -> None:
        q = country_query("EQUALS", ["USA"])
        self.assertEqual(q, Q(country=Countries.get_country_value("USA")))

    def test_country_query_not_equals(self) -> None:
        q = country_query("NOT_EQUALS", ["USA"])
        self.assertEqual(q, ~Q(country=Countries.get_country_value("USA")))

    def test_registration_data_import_query(self) -> None:
        q = registration_data_import_query("EQUALS", [1, 2, 3])
        self.assertEqual(q, Q(registration_data_import__pk__in=[1, 2, 3]))

    def test_invalid_country_comparison_method(self) -> None:
        with self.assertRaises(ValidationError):
            country_query("INVALID_METHOD", ["USA"])

    def test_get_has_phone_number_query_true(self) -> None:
        q = get_has_phone_number_query(None, [True])
        self.assertEqual(q, ~Q(phone_no=""))

    def test_get_has_phone_number_query_false(self) -> None:
        q = get_has_phone_number_query(None, [False])
        self.assertEqual(q, Q(phone_no=""))

    def test_get_birth_certificate_document_number_query(self) -> None:
        q = get_birth_certificate_document_number_query(None, ["1234"])
        self.assertEqual(q, Q(documents__type__key="birth_certificate", documents__document_number="1234"))

    def test_get_tax_id_document_number_query(self) -> None:
        q = get_tax_id_document_number_query(None, ["5678"])
        self.assertEqual(q, Q(documents__type__key="tax_id", documents__document_number="5678"))

    def test_get_drivers_license_document_number_query(self) -> None:
        q = get_drivers_license_document_number_query(None, ["ABCD"])
        self.assertEqual(q, Q(documents__type__key="drivers_license", documents__document_number="ABCD"))

    def test_get_national_id_document_number_query(self) -> None:
        q = get_national_id_document_number_query(None, ["EFGH"])
        self.assertEqual(q, Q(documents__type__key="national_id", documents__document_number="EFGH"))

    def test_get_national_passport_document_number_query(self) -> None:
        q = get_national_passport_document_number_query(None, ["IJKL"])
        self.assertEqual(q, Q(documents__type__key="national_passport", documents__document_number="IJKL"))

    def test_get_electoral_card_document_number_query(self) -> None:
        q = get_electoral_card_document_number_query(None, ["MNOP"])
        self.assertEqual(q, Q(documents__type__key="electoral_card", documents__document_number="MNOP"))

    def test_get_other_document_number_query(self) -> None:
        q = get_other_document_number_query(None, ["QRST"])
        self.assertEqual(q, Q(documents__type__key="other", documents__document_number="QRST"))

    def test_get_has_bank_account_number_query_true(self) -> None:
        # Test for individuals who have a bank account number
        expected_query = Q(bank_account_info__isnull=False) & ~Q(bank_account_info__bank_account_number="")
        result = get_has_bank_account_number_query(None, [True])
        self.assertEqual(result, expected_query)

    def test_get_has_bank_account_number_query_false(self) -> None:
        # Test for individuals who do not have a bank account number
        expected_query = Q(bank_account_info__isnull=True) | Q(bank_account_info__bank_account_number="")
        result = get_has_bank_account_number_query(None, [False])
        self.assertEqual(result, expected_query)

    def test_get_has_bank_account_number_query_social_worker_true(self) -> None:
        # Test with social worker prefix for individuals who have a bank account number
        expected_query = Q(individuals__bank_account_info__isnull=False) & ~Q(
            individuals__bank_account_info__bank_account_number=""
        )
        result = get_has_bank_account_number_query(None, [True], is_social_worker_query=True)
        self.assertEqual(result, expected_query)

    def test_get_has_bank_account_number_query_social_worker_false(self) -> None:
        # Test with social worker prefix for individuals who do not have a bank account number
        expected_query = Q(individuals__bank_account_info__isnull=True) | Q(
            individuals__bank_account_info__bank_account_number=""
        )
        result = get_has_bank_account_number_query(None, [False], is_social_worker_query=True)
        self.assertEqual(result, expected_query)

    def test_get_has_tax_id_query_true(self) -> None:
        # Test for individuals who have a tax ID
        expected_query = Q(documents__type__key__iexact="TAX_ID")
        result = get_has_tax_id_query(None, [True])
        self.assertEqual(result, expected_query)

    def test_get_has_tax_id_query_false(self) -> None:
        # Test for individuals who do not have a tax ID
        expected_query = ~Q(documents__type__key__iexact="TAX_ID")
        result = get_has_tax_id_query(None, [False])
        self.assertEqual(result, expected_query)

    def test_get_has_tax_id_query_social_worker_true(self) -> None:
        # Test with social worker prefix for individuals who have a tax ID
        expected_query = Q(individuals__documents__type__key__iexact="TAX_ID")
        result = get_has_tax_id_query(None, [True], is_social_worker_query=True)
        self.assertEqual(result, expected_query)

    def test_get_has_tax_id_query_social_worker_false(self) -> None:
        # Test with social worker prefix for individuals who do not have a tax ID
        expected_query = ~Q(individuals__documents__type__key__iexact="TAX_ID")
        result = get_has_tax_id_query(None, [False], is_social_worker_query=True)
        self.assertEqual(result, expected_query)

    def test_get_role_query(self) -> None:
        # Without social worker prefix
        expected = Q(households_and_roles__role="manager")
        result = get_role_query(None, ["manager"])
        self.assertEqual(result, expected)

        # With social worker prefix
        expected = Q(individuals__households_and_roles__role="manager")
        result = get_role_query(None, ["manager"], True)
        self.assertEqual(result, expected)

    def test_get_scope_id_number_query(self) -> None:
        # Without social worker prefix
        expected = Q(identities__partner__name=WFP, identities__number="123456")
        result = get_scope_id_number_query(None, ["123456"])
        self.assertEqual(result, expected)

        # With social worker prefix
        expected = Q(individuals__identities__partner__name=WFP, individuals__identities__number="123456")
        result = get_scope_id_number_query(None, ["123456"], True)
        self.assertEqual(result, expected)

    def test_get_scope_id_issuer_query(self) -> None:
        # Without social worker prefix
        expected = Q(identities__partner__name=WFP, identities__country__iso_code3="KEN")
        result = get_scope_id_issuer_query(None, ["KEN"])
        self.assertEqual(result, expected)

        # With social worker prefix
        expected = Q(individuals__identities__partner__name=WFP, individuals__identities__country__iso_code3="KEN")
        result = get_scope_id_issuer_query(None, ["KEN"], True)
        self.assertEqual(result, expected)

    def test_get_unhcr_id_number_query(self) -> None:
        # Without social worker prefix
        expected = Q(identities__partner__name=UNHCR, identities__number="987654")
        result = get_unhcr_id_number_query(None, ["987654"])
        self.assertEqual(result, expected)

        # With social worker prefix
        expected = Q(individuals__identities__partner__name=UNHCR, individuals__identities__number="987654")
        result = get_unhcr_id_number_query(None, ["987654"], True)
        self.assertEqual(result, expected)

    def test_get_unhcr_id_issuer_query(self) -> None:
        # Without social worker prefix
        expected = Q(identities__partner__name=UNHCR, identities__country__iso_code3="UGA")
        result = get_unhcr_id_issuer_query(None, ["UGA"])
        self.assertEqual(result, expected)

        # With social worker prefix
        expected = Q(individuals__identities__partner__name=UNHCR, individuals__identities__country__iso_code3="UGA")
        result = get_unhcr_id_issuer_query(None, ["UGA"], True)
        self.assertEqual(result, expected)
