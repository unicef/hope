from datetime import date

import openpyxl
import pytest

from hope.apps.generic_import.generic_upload_service.parsers.xlsx_somalia_parser import XlsxSomaliaParser


@pytest.fixture
def somalia_excel_file(tmp_path):
    """Create a temporary Excel file with Somalia format data matching the screenshot."""
    # Create file in pytest's tmp_path (automatically cleaned up)
    excel_file = tmp_path / "somalia_test.xlsx"

    # Create workbook with data from screenshot
    wb = openpyxl.Workbook()
    ws = wb.active

    # Headers (exact columns from screenshot)
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

    # Data row (exact data from screenshot)
    data_row = [
        "CSSP2009442",  # HouseholdCSSPID
        "H101N1M67376",  # Srn
        252616473186,  # IndividualID
        "AAMIN MAXAMUUD WABAR MAXAMED",  # IndividualName
        "Female",  # Sex
        date(1996, 7, 1),  # IndividualDateOfBirth
        252616473186,  # IndividualPhoneNumber
        "Nbar",  # IndividualDocument
        "Nbae",  # IndividualIDNumber
        "JALALAQSI",  # District
        "Hantiwadaag",  # Village
        252616473186,  # WalletPhoneNumber
        3,  # HouseholdSize
        0,  # PregnantCount
        1,  # LactatingCount
        1,  # InfantCount
        20,  # EntitlementAmount
        "Hormuud Telecom",  # MPSP
    ]
    ws.append(data_row)

    # Add a second row for the same household (different family member)
    data_row_2 = [
        "CSSP2009442",  # Same household
        "H101N1M67377",
        252616473187,  # Different IndividualID
        "MOHAMED AAMIN WABAR",  # Different name
        "Male",  # Different sex
        date(2015, 3, 15),  # Different DOB
        252616473187,  # Different phone
        "",
        "",
        "JALALAQSI",  # Same district
        "Hantiwadaag",  # Same village
        252616473187,  # Different wallet
        3,  # Same household size
        0,
        1,
        1,
        20,
        "Hormuud Telecom",
    ]
    ws.append(data_row_2)

    # Save workbook
    wb.save(str(excel_file))

    return str(excel_file)


class TestXlsxSomaliaParser:
    """Test suite for XlsxSomaliaParser with real Somalia data format."""

    def test_parser_initialization(self):
        """Test that parser initializes correctly."""
        parser = XlsxSomaliaParser()

        assert parser._households == {}
        assert parser._individuals == []
        assert parser._accounts == []
        assert parser._errors == []
        assert parser._parsed is False

    def test_parse_somalia_excel_file(self, somalia_excel_file):
        """Test parsing of Somalia format Excel file."""
        parser = XlsxSomaliaParser()
        parser.parse(somalia_excel_file)

        # Check parsing completed
        assert parser._parsed is True

        # Check households data
        households = parser.households_data
        assert len(households) == 1  # One household (CSSP2009442)

        household = households[0]
        assert household["size"] == 3
        assert household["village"] == "Hantiwadaag"
        assert household["address"] == "JALALAQSI"
        assert household["admin1"] is None  # Admin area not in test database
        assert household["country"] is None  # Country not in test database
        assert household["pregnant_count"] == 0
        assert household["flex_fields"]["lactating_count_h_f"] == 1
        assert household["flex_fields"]["infant_count_h_f"] == 1
        assert household["flex_fields"]["entitlement_amount_h_f"] == 20.0
        assert household["flex_fields"]["mpsp_h_f"] == "Hormuud Telecom"
        assert household["flex_fields"]["household_cssp_id_h_f"] == "CSSP2009442"

    def test_parse_individuals(self, somalia_excel_file):
        """Test that individuals are parsed correctly."""
        parser = XlsxSomaliaParser()
        parser.parse(somalia_excel_file)

        individuals = parser.individuals_data
        assert len(individuals) == 2  # Two individuals in the household

        # Check first individual (AAMIN)
        individual_1 = individuals[0]
        assert individual_1["given_name"] == "AAMIN"
        assert individual_1["family_name"] == "MAXAMUUD WABAR MAXAMED"
        assert individual_1["full_name"] == "AAMIN MAXAMUUD WABAR MAXAMED"
        assert individual_1["birth_date"] == "1996-07-01"
        assert individual_1["sex"] == "FEMALE"
        assert individual_1["relationship"] == "HEAD"
        assert "252616473186" in individual_1["phone_no"]
        assert individual_1["flex_fields"]["individual_id_i_f"] == 252616473186

        # Check second individual (MOHAMED)
        individual_2 = individuals[1]
        assert individual_2["given_name"] == "MOHAMED"
        assert individual_2["family_name"] == "AAMIN WABAR"
        assert individual_2["sex"] == "MALE"
        assert individual_2["birth_date"] == "2015-03-15"

    def test_parse_accounts(self, somalia_excel_file):
        """Test that mobile money accounts are parsed correctly."""
        parser = XlsxSomaliaParser()
        parser.parse(somalia_excel_file)

        accounts = parser.accounts_data
        assert len(accounts) == 2  # Two wallet phone numbers

        # Check first account
        account_1 = accounts[0]
        assert account_1["account_type"] == "mobile"
        assert "252616473186" in account_1["number"]
        assert account_1["data"]["provider"] == "Hormuud Telecom"

        # Check second account
        account_2 = accounts[1]
        assert account_2["account_type"] == "mobile"
        assert "252616473187" in account_2["number"]

    def test_required_columns_validation(self, tmp_path):
        """Test that parser validates required columns."""
        # Create file with missing columns
        excel_file = tmp_path / "missing_columns.xlsx"

        wb = openpyxl.Workbook()
        ws = wb.active

        # Only some headers (missing required ones)
        headers = ["HouseholdCSSPID", "IndividualName"]
        ws.append(headers)

        wb.save(str(excel_file))

        parser = XlsxSomaliaParser()
        parser.parse(str(excel_file))

        # Should have errors
        assert len(parser.errors) > 0
        assert "Missing required columns" in parser.errors[0]

    def test_sex_field_normalization(self, somalia_excel_file):
        """Test that sex field is normalized correctly."""
        parser = XlsxSomaliaParser()
        parser.parse(somalia_excel_file)

        individuals = parser.individuals_data

        # Female should be normalized to FEMALE
        assert individuals[0]["sex"] == "FEMALE"

        # Male should be normalized to MALE
        assert individuals[1]["sex"] == "MALE"

    def test_phone_number_formatting(self, somalia_excel_file):
        """Test that phone numbers are formatted correctly."""
        parser = XlsxSomaliaParser()
        parser.parse(somalia_excel_file)

        individuals = parser.individuals_data

        # Phone numbers should be strings
        phone_1 = individuals[0]["phone_no"]
        assert isinstance(phone_1, str)
        assert "252616473186" in phone_1

        # Accounts should also have formatted phone numbers
        accounts = parser.accounts_data
        account_number = accounts[0]["number"]
        assert isinstance(account_number, str)
        assert "252616473186" in account_number

    def test_household_grouping(self, somalia_excel_file):
        """Test that multiple individuals are grouped into one household."""
        parser = XlsxSomaliaParser()
        parser.parse(somalia_excel_file)

        # Should create only one household despite two rows
        households = parser.households_data
        assert len(households) == 1

        # But should create two individuals
        individuals = parser.individuals_data
        assert len(individuals) == 2

        # Both individuals should reference the same household
        household_id = households[0]["id"]
        assert individuals[0]["household_id"] == household_id
        assert individuals[1]["household_id"] == household_id

    def test_head_of_household(self, somalia_excel_file):
        """Test that head_of_household_id is set correctly."""
        parser = XlsxSomaliaParser()
        parser.parse(somalia_excel_file)

        households = parser.households_data
        individuals = parser.individuals_data

        # Should have head_of_household_id set
        household = households[0]
        assert "head_of_household_id" in household
        assert household["head_of_household_id"] is not None

        # head_of_household_id should match the first individual's id
        first_individual_id = individuals[0]["id"]
        assert household["head_of_household_id"] == first_individual_id

    def test_empty_file(self, tmp_path):
        """Test parsing of empty Excel file."""
        excel_file = tmp_path / "empty.xlsx"

        wb = openpyxl.Workbook()
        ws = wb.active

        # Only headers, no data
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
        ws.append(headers)

        wb.save(str(excel_file))

        parser = XlsxSomaliaParser()
        parser.parse(str(excel_file))

        # Should parse successfully but have no data
        assert parser._parsed is True
        assert len(parser.households_data) == 0
        assert len(parser.individuals_data) == 0

    def test_date_format_handling(self, somalia_excel_file):
        """Test that different date formats are handled correctly."""
        parser = XlsxSomaliaParser()
        parser.parse(somalia_excel_file)

        individuals = parser.individuals_data

        # Dates should be formatted as YYYY-MM-DD strings
        assert individuals[0]["birth_date"] == "1996-07-01"
        assert individuals[1]["birth_date"] == "2015-03-15"

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
            ("", "MALE"),  # Default
            ("unknown", "MALE"),  # Default
        ],
    )
    def test_sex_value_normalization(self, tmp_path, sex_value, expected):
        """Test various sex value inputs are normalized correctly."""
        excel_file = tmp_path / f"sex_test_{sex_value}.xlsx"

        wb = openpyxl.Workbook()
        ws = wb.active

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
        ws.append(headers)

        ws.append(["TEST001", 123456, "TEST NAME", sex_value, date(2000, 1, 1), "TEST", "TEST", 1])

        wb.save(str(excel_file))

        parser = XlsxSomaliaParser()
        parser.parse(str(excel_file))

        individuals = parser.individuals_data
        assert len(individuals) > 0
        assert individuals[0]["sex"] == expected
