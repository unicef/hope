from datetime import date

import openpyxl
import pytest

from extras.test_utils.factories import BusinessAreaFactory
from hope.apps.generic_import.generic_upload_service.parsers.xlsx_somalia_parser import XlsxSomaliaParser


@pytest.fixture
def business_area(db):
    return BusinessAreaFactory()


@pytest.fixture
def somalia_excel_file(tmp_path):
    excel_file = tmp_path / "somalia_test.xlsx"

    wb = openpyxl.Workbook()
    ws = wb.active

    headers = [
        "HouseholdCSSPID",
        "Srn",
        "IndividualID",
        "IndividualName",
        "Sex",
        "IndividualDateOfBirth",
        "IndividualPhoneNumber",
        "IndividualDocument",
        "IndividualIDNumber",
        "District",
        "Village",
        "WalletPhoneNumber",
        "HouseholdSize",
        "PregnantCount",
        "LactatingCount",
        "InfantCount",
        "EntitlementAmount",
        "MPSP",
    ]
    ws.append(headers)

    data_row = [
        "CSSP2009442",
        "H101N1M67376",
        252616473186,
        "AAMIN MAXAMUUD WABAR MAXAMED",
        "Female",
        date(1996, 7, 1),
        252616473186,
        "Nbar",
        "Nbae",
        "JALALAQSI",
        "Hantiwadaag",
        252616473186,
        3,
        0,
        1,
        1,
        20,
        "Hormuud Telecom",
    ]
    ws.append(data_row)

    data_row_2 = [
        "CSSP2009442",
        "H101N1M67377",
        252616473187,
        "MOHAMED AAMIN WABAR",
        "Male",
        date(2015, 3, 15),
        252616473187,
        "",
        "",
        "JALALAQSI",
        "Hantiwadaag",
        252616473187,
        3,
        0,
        1,
        1,
        20,
        "Hormuud Telecom",
    ]
    ws.append(data_row_2)

    wb.save(str(excel_file))

    return str(excel_file)


@pytest.fixture
def make_excel_file(tmp_path):
    def _make(filename, headers, rows):
        filepath = tmp_path / filename
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.append(headers)
        for row in rows:
            ws.append(row)
        wb.save(str(filepath))
        return str(filepath)

    return _make


@pytest.mark.django_db
def test_parser_initializes_with_empty_state(business_area):
    parser = XlsxSomaliaParser(business_area)

    assert parser._households == {}
    assert parser._individuals == []
    assert parser._accounts == []
    assert parser._errors == []
    assert parser._parsed is False


@pytest.mark.django_db
def test_parse_produces_correct_household_data(business_area, somalia_excel_file):
    parser = XlsxSomaliaParser(business_area)
    parser.parse(somalia_excel_file)

    assert parser._parsed is True

    households = parser.households_data
    assert len(households) == 1

    household = households[0]
    assert household["size"] == 3
    assert household["village"] == "Hantiwadaag"
    assert household["address"] == "JALALAQSI"
    assert household["admin1"] is None
    assert household["country"] is None
    assert household["pregnant_count"] == 0
    assert household["flex_fields"]["lactating_count_h_f"] == 1
    assert household["flex_fields"]["infant_count_h_f"] == 1
    assert household["flex_fields"]["entitlement_amount_h_f"] == 20.0
    assert household["flex_fields"]["mpsp_h_f"] == "Hormuud Telecom"
    assert household["flex_fields"]["household_cssp_id_h_f"] == "CSSP2009442"


@pytest.mark.django_db
def test_parse_produces_correct_individual_data(business_area, somalia_excel_file):
    parser = XlsxSomaliaParser(business_area)
    parser.parse(somalia_excel_file)

    individuals = parser.individuals_data
    assert len(individuals) == 2

    individual_1 = individuals[0]
    assert individual_1["given_name"] == "AAMIN"
    assert individual_1["family_name"] == "MAXAMUUD WABAR MAXAMED"
    assert individual_1["full_name"] == "AAMIN MAXAMUUD WABAR MAXAMED"
    assert individual_1["birth_date"] == "1996-07-01"
    assert individual_1["sex"] == "FEMALE"
    assert individual_1["relationship"] == "HEAD"
    assert "252616473186" in individual_1["phone_no"]
    assert individual_1["flex_fields"]["individual_id_i_f"] == 252616473186

    individual_2 = individuals[1]
    assert individual_2["given_name"] == "MOHAMED"
    assert individual_2["family_name"] == "AAMIN WABAR"
    assert individual_2["sex"] == "MALE"
    assert individual_2["birth_date"] == "2015-03-15"


@pytest.mark.django_db
def test_parse_produces_correct_account_data(business_area, somalia_excel_file):
    parser = XlsxSomaliaParser(business_area)
    parser.parse(somalia_excel_file)

    accounts = parser.accounts_data
    assert len(accounts) == 2

    account_1 = accounts[0]
    assert account_1["account_type"] == "mobile"
    assert "252616473186" in account_1["number"]
    assert account_1["data"]["provider"] == "Hormuud Telecom"

    account_2 = accounts[1]
    assert account_2["account_type"] == "mobile"
    assert "252616473187" in account_2["number"]


@pytest.mark.django_db
def test_parse_reports_error_for_missing_required_columns(business_area, make_excel_file):
    excel_file = make_excel_file("missing_columns.xlsx", ["HouseholdCSSPID", "IndividualName"], [])

    parser = XlsxSomaliaParser(business_area)
    parser.parse(excel_file)

    assert len(parser.errors) > 0
    assert "Missing required columns" in parser.errors[0]


@pytest.mark.django_db
def test_parse_normalizes_sex_field_values(business_area, somalia_excel_file):
    parser = XlsxSomaliaParser(business_area)
    parser.parse(somalia_excel_file)

    individuals = parser.individuals_data

    assert individuals[0]["sex"] == "FEMALE"
    assert individuals[1]["sex"] == "MALE"


@pytest.mark.django_db
def test_parse_formats_phone_numbers_as_strings(business_area, somalia_excel_file):
    parser = XlsxSomaliaParser(business_area)
    parser.parse(somalia_excel_file)

    individuals = parser.individuals_data

    phone_1 = individuals[0]["phone_no"]
    assert isinstance(phone_1, str)
    assert "252616473186" in phone_1

    accounts = parser.accounts_data
    account_number = accounts[0]["number"]
    assert isinstance(account_number, str)
    assert "252616473186" in account_number


@pytest.mark.django_db
def test_parse_groups_rows_with_same_id_into_one_household(business_area, somalia_excel_file):
    parser = XlsxSomaliaParser(business_area)
    parser.parse(somalia_excel_file)

    households = parser.households_data
    assert len(households) == 1

    individuals = parser.individuals_data
    assert len(individuals) == 2

    household_id = households[0]["id"]
    assert individuals[0]["household_id"] == household_id
    assert individuals[1]["household_id"] == household_id


@pytest.mark.django_db
def test_parse_sets_first_individual_as_head_of_household(business_area, somalia_excel_file):
    parser = XlsxSomaliaParser(business_area)
    parser.parse(somalia_excel_file)

    households = parser.households_data
    individuals = parser.individuals_data

    household = households[0]
    assert "head_of_household_id" in household
    assert household["head_of_household_id"] is not None

    first_individual_id = individuals[0]["id"]
    assert household["head_of_household_id"] == first_individual_id


@pytest.mark.django_db
def test_parse_produces_no_data_for_headers_only_file(business_area, make_excel_file):
    headers = [
        "HouseholdCSSPID",
        "Srn",
        "IndividualID",
        "IndividualName",
        "Sex",
        "IndividualDateOfBirth",
        "District",
        "Village",
        "HouseholdSize",
    ]
    excel_file = make_excel_file("empty.xlsx", headers, [])

    parser = XlsxSomaliaParser(business_area)
    parser.parse(excel_file)

    assert parser._parsed is True
    assert len(parser.households_data) == 0
    assert len(parser.individuals_data) == 0


@pytest.mark.django_db
def test_parse_formats_dates_as_iso_strings(business_area, somalia_excel_file):
    parser = XlsxSomaliaParser(business_area)
    parser.parse(somalia_excel_file)

    individuals = parser.individuals_data

    assert individuals[0]["birth_date"] == "1996-07-01"
    assert individuals[1]["birth_date"] == "2015-03-15"


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("sex_value", "expected"),
    [
        ("Female", "FEMALE"),
        ("female", "FEMALE"),
        ("f", "FEMALE"),
        ("F", "FEMALE"),
        ("Male", "MALE"),
        ("male", "MALE"),
        ("m", "MALE"),
        ("M", "MALE"),
        ("", "MALE"),
        ("unknown", "MALE"),
    ],
)
def test_sex_value_normalization(business_area, make_excel_file, sex_value, expected):
    headers = [
        "HouseholdCSSPID",
        "IndividualID",
        "IndividualName",
        "Sex",
        "IndividualDateOfBirth",
        "District",
        "Village",
        "HouseholdSize",
    ]
    excel_file = make_excel_file(
        f"sex_test_{sex_value}.xlsx",
        headers,
        [["TEST001", 123456, "TEST NAME", sex_value, date(2000, 1, 1), "TEST", "TEST", 1]],
    )

    parser = XlsxSomaliaParser(business_area)
    parser.parse(excel_file)

    individuals = parser.individuals_data
    assert len(individuals) > 0
    assert individuals[0]["sex"] == expected


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("input_value", "expected"),
    [
        ("", ""),
        (None, ""),
        ("   ", ""),
        ("+252612345678", "+252612345678"),
        ("252612345678.0", "+252612345678"),
        ("N/A", "N/A"),
        ("invalid-phone", "invalid-phone"),
    ],
)
def test_format_phone_returns_expected_value(business_area, input_value, expected):
    parser = XlsxSomaliaParser(business_area)
    assert parser._format_phone(input_value) == expected


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("input_value", "expected"),
    [
        (None, 0),
        ("", 0),
        (3.7, 3),
        ("5.9", 5),
        ("invalid", 0),
        ("abc123", 0),
    ],
)
def test_parse_int_returns_expected_value(business_area, input_value, expected):
    parser = XlsxSomaliaParser(business_area)
    assert parser._parse_int(input_value) == expected


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("input_value", "expected"),
    [
        (None, 0.0),
        ("", 0.0),
        (3.5, 3.5),
        ("5.9", 5.9),
        ("invalid", 0.0),
        ("abc123", 0.0),
    ],
)
def test_parse_float_returns_expected_value(business_area, input_value, expected):
    parser = XlsxSomaliaParser(business_area)
    assert parser._parse_float(input_value) == expected


@pytest.mark.django_db
def test_validate_file_structure_returns_false_before_parsing(business_area):
    parser = XlsxSomaliaParser(business_area)
    assert parser.validate_file_structure() is False


@pytest.mark.django_db
def test_validate_file_structure_returns_false_with_parse_errors(business_area, make_excel_file):
    excel_file = make_excel_file("invalid.xlsx", ["HouseholdCSSPID"], [])

    parser = XlsxSomaliaParser(business_area)
    parser.parse(excel_file)

    assert parser.validate_file_structure() is False
    assert len(parser.errors) > 0


@pytest.mark.django_db
def test_validate_file_structure_returns_true_after_successful_parse(business_area, somalia_excel_file):
    parser = XlsxSomaliaParser(business_area)
    parser.parse(somalia_excel_file)

    assert parser.validate_file_structure() is True
    assert len(parser.errors) == 0


@pytest.mark.django_db
def test_supported_file_types_includes_xlsx_and_xls(business_area):
    parser = XlsxSomaliaParser(business_area)
    supported = parser.supported_file_types

    assert ".xlsx" in supported
    assert ".xls" in supported
    assert len(supported) == 2


@pytest.mark.django_db
def test_individual_roles_in_households_data_returns_empty_list(business_area):
    parser = XlsxSomaliaParser(business_area)
    assert parser.individual_roles_in_households_data == []


@pytest.mark.django_db
def test_parse_handles_corrupted_file_gracefully(business_area, tmp_path):
    invalid_file = tmp_path / "corrupted.xlsx"
    invalid_file.write_bytes(b"not a valid xlsx file")

    parser = XlsxSomaliaParser(business_area)
    parser.parse(str(invalid_file))

    assert len(parser.errors) > 0
    assert "Error parsing file" in parser.errors[0]
    assert parser._parsed is False


@pytest.mark.django_db
def test_parse_preserves_string_date_format(business_area, make_excel_file):
    headers = [
        "HouseholdCSSPID",
        "IndividualID",
        "IndividualName",
        "Sex",
        "IndividualDateOfBirth",
        "District",
        "Village",
        "HouseholdSize",
    ]
    excel_file = make_excel_file(
        "string_date.xlsx",
        headers,
        [["TEST001", 123456, "TEST NAME", "Male", "1990-01-15", "TEST", "TEST", 1]],
    )

    parser = XlsxSomaliaParser(business_area)
    parser.parse(excel_file)

    individuals = parser.individuals_data
    assert len(individuals) == 1
    assert individuals[0]["birth_date"] == "1990-01-15"


@pytest.mark.django_db
def test_parse_skips_documents_with_none_id_number(business_area, make_excel_file):
    headers = [
        "HouseholdCSSPID",
        "IndividualID",
        "IndividualName",
        "Sex",
        "IndividualDateOfBirth",
        "District",
        "Village",
        "HouseholdSize",
        "IndividualIDDocument",
        "IndividualIDNumber",
    ]
    excel_file = make_excel_file(
        "none_doc.xlsx",
        headers,
        [["TEST001", 123456, "TEST NAME", "Male", date(1990, 1, 1), "TEST", "TEST", 1, "passport", "None"]],
    )

    parser = XlsxSomaliaParser(business_area)
    parser.parse(excel_file)

    assert len(parser.documents_data) == 0


@pytest.mark.django_db
def test_parser_sets_financial_institution_to_none_when_ba_has_no_countries(business_area):
    parser = XlsxSomaliaParser(business_area)
    assert parser._financial_institution is None


@pytest.mark.django_db
def test_parse_skips_empty_rows(business_area, make_excel_file):
    headers = [
        "HouseholdCSSPID",
        "IndividualID",
        "IndividualName",
        "Sex",
        "IndividualDateOfBirth",
        "District",
        "Village",
        "HouseholdSize",
    ]
    rows = [
        ["HH001", 123456, "Person One", "Male", date(1990, 1, 1), "District1", "Village1", 2],
        [None, None, None, None, None, None, None, None],
        ["", "", "", "", "", "", "", ""],
        ["HH001", 123457, "Person Two", "Female", date(1992, 5, 15), "District1", "Village1", 2],
    ]
    excel_file = make_excel_file("empty_rows.xlsx", headers, rows)

    parser = XlsxSomaliaParser(business_area)
    parser.parse(excel_file)

    assert len(parser.households_data) == 1
    assert len(parser.individuals_data) == 2
