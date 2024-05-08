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
    get_has_phone_number_query,
    get_national_id_document_number_query,
    get_national_passport_document_number_query,
    get_other_document_number_query,
    get_tax_id_document_number_query,
    registration_data_import_query,
)
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.countries import Countries


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
