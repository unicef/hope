"""Integration tests for Somalia import flow - parse + import + database verification."""

from datetime import date

import openpyxl
import pytest

from extras.test_utils.factories.program import ProgramFactory
from extras.test_utils.factories.registration_data import RegistrationDataImportFactory
from hope.apps.generic_import.generic_upload_service.importer import Importer
from hope.apps.generic_import.generic_upload_service.parsers.xlsx_somalia_parser import XlsxSomaliaParser
from hope.models import (
    Account,
    AccountType,
    BeneficiaryGroup,
    BusinessArea,
    DataCollectingType,
    Document,
    Household,
    Individual,
    Program,
    RegistrationDataImport,
)


@pytest.fixture
def business_area(db):
    """Create test business area."""
    return BusinessArea.objects.create(
        name="Test Somalia",
        code="TST",
        slug="test-somalia",
    )


@pytest.fixture
def program(db, business_area):
    """Create test program using factory."""
    # Create data collecting type for SOCIAL type
    dct = DataCollectingType.objects.create(
        label="Full",
        code="full",
        type=DataCollectingType.Type.SOCIAL,
    )

    # Create beneficiary group with master_detail=False for SOCIAL type
    bg = BeneficiaryGroup.objects.create(
        name="Test Group",
        master_detail=False,
    )

    return ProgramFactory.create(
        name="Test Somalia Program",
        business_area=business_area,
        status=Program.ACTIVE,
        data_collecting_type=dct,
        beneficiary_group=bg,
    )


@pytest.fixture
def registration_data_import(db, business_area, program):
    """Create test RDI using factory."""
    return RegistrationDataImportFactory.create(
        business_area=business_area,
        program=program,
        name="Test Somalia Import",
        status=RegistrationDataImport.LOADING,
    )


@pytest.fixture
def mobile_account_type(db):
    """Create mobile account type."""
    return AccountType.objects.create(
        key="mobile",
        label="Mobile Money",
    )


@pytest.fixture
def generic_financial_institutions(db):
    """Create generic financial institutions for accounts without FI."""
    from hope.models import FinancialInstitution

    FinancialInstitution.objects.create(name="Generic Bank")
    FinancialInstitution.objects.create(name="Generic Telco Company")


@pytest.fixture
def document_type_other_id(db):
    """Create other_id document type."""
    from hope.models import DocumentType

    return DocumentType.objects.create(
        key="other_id",
        label="Other ID",
    )


@pytest.fixture
def somalia_country(db):
    """Create Somalia country."""
    from hope.models import Country

    return Country.objects.create(
        name="Somalia",
        short_name="Somalia",
        iso_code2="SO",
        iso_code3="SOM",
        iso_num="706",
    )


@pytest.fixture
def somalia_excel_file_exact(tmp_path):
    """Create Excel file with exact data from user screenshot."""
    excel_file = tmp_path / "somalia_exact.xlsx"

    wb = openpyxl.Workbook()
    ws = wb.active

    # Headers from screenshot
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

    # Exact data from screenshot
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

    # Second individual for same household
    data_row_2 = [
        "CSSP2009442",  # Same household
        "H101N1M67377",
        252616473187,  # Different IndividualID
        "MOHAMED AAMIN WABAR",  # Different name
        "Male",
        date(2015, 3, 15),
        252616473187,
        "",
        "",
        "JALALAQSI",
        "Hantiwadaag",
        252616473187,
        3,  # Same household size
        0,
        1,
        1,
        20,
        "Hormuud Telecom",
    ]
    ws.append(data_row_2)

    wb.save(str(excel_file))
    return str(excel_file)


@pytest.mark.django_db
class TestSomaliaImportIntegration:
    """Integration tests for full Somalia import flow."""

    def test_full_import_flow(
        self,
        somalia_excel_file_exact,
        registration_data_import,
        mobile_account_type,
        document_type_other_id,
        somalia_country,
        generic_financial_institutions,
    ):
        """Test complete flow: parse → import → database verification."""
        # Step 1: Parse Excel file
        parser = XlsxSomaliaParser()
        parser.parse(somalia_excel_file_exact)

        # Verify parsing succeeded
        assert parser._parsed is True
        assert len(parser.errors) == 0
        assert len(parser.households_data) == 1
        assert len(parser.individuals_data) == 2
        assert len(parser.accounts_data) == 2

        # Step 2: Run importer
        importer = Importer(
            registration_data_import=registration_data_import,
            households_data=parser.households_data,
            individuals_data=parser.individuals_data,
            documents_data=parser.documents_data,
            accounts_data=parser.accounts_data,
            identities_data=parser.identities_data,
        )

        errors = importer.import_data()

        # Verify no import errors
        assert errors == [], f"Import errors: {errors}"

        # Step 3: Verify database objects

        # 3.1 Verify Household (use pending_objects since rdi_merge_status=PENDING)
        households = Household.pending_objects.filter(registration_data_import=registration_data_import)
        assert households.count() == 1

        household = households.first()
        assert household.size == 3
        assert household.village == "Hantiwadaag"
        assert household.address == "JALALAQSI"
        assert household.pregnant_count == 0
        assert household.business_area == registration_data_import.business_area
        assert household.program == registration_data_import.program
        assert household.registration_data_import == registration_data_import
        assert household.rdi_merge_status == Household.PENDING
        assert household.first_registration_date is not None
        assert household.last_registration_date is not None

        # Verify flex_fields
        assert household.flex_fields["lactating_count_h_f"] == 1
        assert household.flex_fields["infant_count_h_f"] == 1
        assert household.flex_fields["entitlement_amount_h_f"] == 20.0
        assert household.flex_fields["mpsp_h_f"] == "Hormuud Telecom"
        assert household.flex_fields["household_cssp_id_h_f"] == "CSSP2009442"

        # 3.2 Verify Individuals (use pending_objects since rdi_merge_status=PENDING)
        individuals = Individual.pending_objects.filter(registration_data_import=registration_data_import).order_by(
            "birth_date"
        )
        assert individuals.count() == 2

        # First individual (AAMIN - head of household)
        individual_1 = individuals[0]
        assert individual_1.given_name == "AAMIN"
        assert individual_1.family_name == "MAXAMUUD WABAR MAXAMED"
        assert individual_1.full_name == "AAMIN MAXAMUUD WABAR MAXAMED"
        assert individual_1.sex == "FEMALE"
        assert str(individual_1.birth_date) == "1996-07-01"
        assert individual_1.relationship == "HEAD"
        assert "+252616473186" in str(individual_1.phone_no)
        assert individual_1.household == household
        assert individual_1.business_area == registration_data_import.business_area
        assert individual_1.program == registration_data_import.program
        assert individual_1.registration_data_import == registration_data_import
        assert individual_1.rdi_merge_status == Individual.PENDING
        assert individual_1.first_registration_date is not None
        assert individual_1.last_registration_date is not None
        assert individual_1.flex_fields["individual_id_i_f"] == 252616473186

        # Second individual (MOHAMED)
        individual_2 = individuals[1]
        assert individual_2.given_name == "MOHAMED"
        assert individual_2.family_name == "AAMIN WABAR"
        assert individual_2.full_name == "MOHAMED AAMIN WABAR"
        assert individual_2.sex == "MALE"
        assert str(individual_2.birth_date) == "2015-03-15"
        assert "+252616473187" in str(individual_2.phone_no)
        assert individual_2.household == household
        assert individual_2.flex_fields["individual_id_i_f"] == 252616473187

        # 3.3 Verify head_of_household is set correctly
        household.refresh_from_db()  # Refresh to get updated head_of_household FK
        assert household.head_of_household is not None
        assert household.head_of_household == individual_1
        assert household.head_of_household.given_name == "AAMIN"

        # 3.4 Verify Accounts
        # Get individual IDs first using pending_objects, then filter accounts by those IDs
        individual_ids = Individual.pending_objects.filter(
            registration_data_import=registration_data_import
        ).values_list("id", flat=True)

        # Query accounts using _base_manager to bypass any filtering
        accounts = Account._base_manager.filter(individual_id__in=individual_ids).order_by("number")
        assert accounts.count() == 2

        # First account
        account_1 = accounts[0]
        assert account_1.individual == individual_1
        assert "+252616473186" in str(account_1.number)
        assert account_1.account_type == mobile_account_type
        assert account_1.data["provider"] == "Hormuud Telecom"

        # Second account
        account_2 = accounts[1]
        assert account_2.individual == individual_2
        assert "+252616473187" in str(account_2.number)
        assert account_2.account_type == mobile_account_type

        # 3.5 Verify Documents
        # Get individual IDs first using pending_objects, then filter documents by those IDs
        documents = Document._base_manager.filter(individual_id__in=individual_ids)
        assert documents.count() == 1  # Only first individual has document

        document = documents.first()
        assert document.individual == individual_1
        assert document.document_number == "Nbae"
        assert document.country.iso_code3 == "SOM"
        assert document.rdi_merge_status == Document.PENDING

        # 3.6 Verify all FK relationships work (no constraint violations)
        # Refresh from DB to ensure FKs are persisted correctly
        household_from_db = Household.pending_objects.get(id=household.id)
        individual_1_from_db = Individual.pending_objects.get(id=individual_1.id)
        individual_2_from_db = Individual.pending_objects.get(id=individual_2.id)
        account_1_from_db = Account._base_manager.get(id=account_1.id)
        account_2_from_db = Account._base_manager.get(id=account_2.id)
        document_from_db = Document._base_manager.get(id=document.id)

        # Verify FK relationships from DB
        assert individual_1_from_db.household_id == household_from_db.id
        assert individual_2_from_db.household_id == household_from_db.id
        assert household_from_db.head_of_household_id == individual_1_from_db.id
        assert account_1_from_db.individual_id == individual_1_from_db.id
        assert account_2_from_db.individual_id == individual_2_from_db.id
        assert document_from_db.individual_id == individual_1_from_db.id

    def test_import_with_missing_account_type(
        self,
        somalia_excel_file_exact,
        registration_data_import,
    ):
        """Test import fails gracefully when account_type doesn't exist."""
        # Parse without creating AccountType
        parser = XlsxSomaliaParser()
        parser.parse(somalia_excel_file_exact)

        importer = Importer(
            registration_data_import=registration_data_import,
            households_data=parser.households_data,
            individuals_data=parser.individuals_data,
            documents_data=parser.documents_data,
            accounts_data=parser.accounts_data,
            identities_data=parser.identities_data,
        )

        errors = importer.import_data()

        # Should have errors for accounts
        assert len(errors) > 0
        assert any(error["type"] == "account" for error in errors)
        assert any("Unknown account type" in str(error) for error in errors)

    def test_import_multiple_households(
        self,
        tmp_path,
        registration_data_import,
        mobile_account_type,
        generic_financial_institutions,
    ):
        """Test importing multiple households."""
        # Create file with multiple households
        excel_file = tmp_path / "multiple_households.xlsx"

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
            "WalletPhoneNumber",
            "HouseholdSize",
            "MPSP",
        ]
        ws.append(headers)

        # First household
        ws.append(
            [
                "CSSP001",
                111111,
                "Person One",
                "Male",
                date(1990, 1, 1),
                "District1",
                "Village1",
                111111,
                1,
                "Provider1",
            ]
        )

        # Second household
        ws.append(
            [
                "CSSP002",
                222222,
                "Person Two",
                "Female",
                date(1995, 1, 1),
                "District2",
                "Village2",
                222222,
                1,
                "Provider2",
            ]
        )

        wb.save(str(excel_file))

        # Parse and import
        parser = XlsxSomaliaParser()
        parser.parse(str(excel_file))

        importer = Importer(
            registration_data_import=registration_data_import,
            households_data=parser.households_data,
            individuals_data=parser.individuals_data,
            documents_data=parser.documents_data,
            accounts_data=parser.accounts_data,
            identities_data=parser.identities_data,
        )

        errors = importer.import_data()
        assert errors == []

        # Verify two households created (use pending_objects since rdi_merge_status=PENDING)
        households = Household.pending_objects.filter(registration_data_import=registration_data_import)
        assert households.count() == 2

        # Verify each household has head_of_household set
        for household in households:
            assert household.head_of_household is not None
            assert household.head_of_household.household == household

        # Verify two individuals created (use pending_objects since rdi_merge_status=PENDING)
        individuals = Individual.pending_objects.filter(registration_data_import=registration_data_import)
        assert individuals.count() == 2

        # Verify two accounts created
        individual_ids = individuals.values_list("id", flat=True)
        accounts = Account._base_manager.filter(individual_id__in=individual_ids)
        assert accounts.count() == 2
