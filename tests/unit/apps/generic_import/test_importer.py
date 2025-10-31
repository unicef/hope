import pytest

from extras.test_utils.factories.core import create_afghanistan
from extras.test_utils.factories.geo import CountryFactory
from extras.test_utils.factories.household import (
    DocumentTypeFactory,
    IndividualFactory,
)
from extras.test_utils.factories.payment import AccountTypeFactory
from extras.test_utils.factories.program import ProgramFactory
from extras.test_utils.factories.registration_data import RegistrationDataImportFactory
from hope.apps.core.models import BusinessArea
from hope.apps.generic_import.generic_upload_service.importer import Importer


@pytest.mark.django_db
class TestImporter:
    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test fixtures."""
        create_afghanistan()
        self.business_area = BusinessArea.objects.get(slug="afghanistan")
        self.program = ProgramFactory(business_area=self.business_area)
        self.registration_data_import = RegistrationDataImportFactory(
            business_area=self.business_area,
            program=self.program,
        )

        # Create necessary related objects
        self.country = CountryFactory(name="Somalia", short_name="SOM", iso_code2="SO", iso_code3="SOM")
        self.document_type = DocumentTypeFactory(key="national_id", label="National ID")
        self.account_type = AccountTypeFactory(key="mobile_money", label="Mobile Money")

        # Create test individual
        self.individual = IndividualFactory(
            business_area=self.business_area,
            program=self.program,
        )

    def test_import_documents_success(self):
        """Test successful import of documents."""
        # Prepare test data matching parser output format
        documents_data = [
            {
                "individual": self.individual.id,
                "type": self.document_type.id,
                "document_number": "ID123456",
                "country": self.country.id,
                "program": self.program.id,
            },
            {
                "individual": self.individual.id,
                "type": self.document_type.id,
                "document_number": "ID789012",
                "country": self.country.id,
                "program": self.program.id,
            },
        ]

        # Create importer instance
        importer = Importer(
            registration_data_import=self.registration_data_import,
            households_data=[],
            individuals_data=[],
            documents_data=documents_data,
            accounts_data=[],
            identities_data=[],
        )

        # Execute import
        importer._import_documents()

        # Assert
        assert len(importer.errors) == 0, f"Errors: {importer.errors}"
        assert len(importer.documents_to_create) == 2
        assert importer.documents_to_create[0].document_number == "ID123456"
        assert importer.documents_to_create[1].document_number == "ID789012"

    def test_import_documents_with_errors(self):
        """Test document import with validation errors."""
        # Prepare invalid data (missing required fields)
        documents_data = [
            {
                "individual": self.individual.id,
                # missing 'type' field
                "document_number": "ID123456",
            },
        ]

        importer = Importer(
            registration_data_import=self.registration_data_import,
            households_data=[],
            individuals_data=[],
            documents_data=documents_data,
            accounts_data=[],
            identities_data=[],
        )

        importer._import_documents()

        # Assert errors were recorded
        assert len(importer.documents_to_create) == 0
        assert len(importer.errors) == 1
        assert importer.errors[0]["type"] == "document"
        assert "type" in str(importer.errors[0]["errors"])

    def test_import_accounts_success(self):
        """Test successful import of accounts."""
        # Prepare test data matching parser output format
        accounts_data = [
            {
                "individual": self.individual.id,
                "account_type": self.account_type.id,
                "number": "+252612345678",
                "data": {"provider": "Hormuud"},
            },
            {
                "individual": self.individual.id,
                "account_type": self.account_type.id,
                "number": "+252623456789",
                "data": {"provider": "Telesom"},
            },
        ]

        importer = Importer(
            registration_data_import=self.registration_data_import,
            households_data=[],
            individuals_data=[],
            documents_data=[],
            accounts_data=accounts_data,
            identities_data=[],
        )

        importer._import_accounts()

        # Assert
        assert len(importer.accounts_to_create) == 2
        assert len(importer.errors) == 0
        assert importer.accounts_to_create[0].number == "+252612345678"
        assert importer.accounts_to_create[0].data["provider"] == "Hormuud"
        assert importer.accounts_to_create[1].number == "+252623456789"

    def test_import_accounts_with_errors(self):
        """Test account import with validation errors."""
        # Prepare invalid data (missing required fields)
        accounts_data = [
            {
                "individual": self.individual.id,
                # missing 'account_type' field
                "number": "+252612345678",
            },
        ]

        importer = Importer(
            registration_data_import=self.registration_data_import,
            households_data=[],
            individuals_data=[],
            documents_data=[],
            accounts_data=accounts_data,
            identities_data=[],
        )

        importer._import_accounts()

        # Assert errors were recorded
        assert len(importer.accounts_to_create) == 0
        assert len(importer.errors) == 1
        assert importer.errors[0]["type"] == "account"
        assert "account_type" in str(importer.errors[0]["errors"])

    def test_import_identities_success(self):
        """Test successful import of identities."""
        # Prepare test data
        identities_data = [
            {
                "individual": self.individual.id,
                "number": "WFP123456",
                "country": self.country.id,
            },
            {
                "individual": self.individual.id,
                "number": "WFP789012",
                "country": self.country.id,
            },
        ]

        importer = Importer(
            registration_data_import=self.registration_data_import,
            households_data=[],
            individuals_data=[],
            documents_data=[],
            accounts_data=[],
            identities_data=identities_data,
        )

        importer._import_identities()

        # Assert
        assert len(importer.errors) == 0, f"Errors: {importer.errors}"
        assert len(importer.identities_to_create) == 2
        assert importer.identities_to_create[0].number == "WFP123456"
        assert importer.identities_to_create[1].number == "WFP789012"

    def test_import_identities_with_errors(self):
        """Test identity import with validation errors."""
        # Prepare invalid data (missing required fields)
        identities_data = [
            {
                "individual": self.individual.id,
                # missing 'number' field
            },
        ]

        importer = Importer(
            registration_data_import=self.registration_data_import,
            households_data=[],
            individuals_data=[],
            documents_data=[],
            accounts_data=[],
            identities_data=identities_data,
        )

        importer._import_identities()

        # Assert errors were recorded
        assert len(importer.identities_to_create) == 0
        assert len(importer.errors) == 1
        assert importer.errors[0]["type"] == "identity"
        assert "number" in str(importer.errors[0]["errors"])

    def test_import_all_data_types_together(self):
        """Test importing documents, accounts, and identities together."""
        documents_data = [
            {
                "individual": self.individual.id,
                "type": self.document_type.id,
                "document_number": "ID123456",
                "country": self.country.id,
                "program": self.program.id,
            },
        ]

        accounts_data = [
            {
                "individual": self.individual.id,
                "account_type": self.account_type.id,
                "number": "+252612345678",
                "data": {"provider": "Hormuud"},
            },
        ]

        identities_data = [
            {
                "individual": self.individual.id,
                "number": "WFP123456",
                "country": self.country.id,
            },
        ]

        importer = Importer(
            registration_data_import=self.registration_data_import,
            households_data=[],
            individuals_data=[],
            documents_data=documents_data,
            accounts_data=accounts_data,
            identities_data=identities_data,
        )

        # Execute all imports
        importer._import_documents()
        importer._import_accounts()
        importer._import_identities()

        # Assert all data was processed
        assert len(importer.documents_to_create) == 1
        assert len(importer.accounts_to_create) == 1
        assert len(importer.identities_to_create) == 1
        assert len(importer.errors) == 0

    def test_import_with_mixed_valid_and_invalid_data(self):
        """Test importing mix of valid and invalid data."""
        documents_data = [
            {
                "individual": self.individual.id,
                "type": self.document_type.id,
                "document_number": "ID123456",
                "country": self.country.id,
                "program": self.program.id,
            },
            {
                "individual": self.individual.id,
                # missing 'type' field - invalid
                "document_number": "ID789012",
            },
        ]

        importer = Importer(
            registration_data_import=self.registration_data_import,
            households_data=[],
            individuals_data=[],
            documents_data=documents_data,
            accounts_data=[],
            identities_data=[],
        )

        importer._import_documents()

        # Assert valid data was processed and invalid data was recorded as error
        assert len(importer.documents_to_create) == 1
        assert len(importer.errors) == 1
        assert importer.documents_to_create[0].document_number == "ID123456"
        assert importer.errors[0]["type"] == "document"

    def test_empty_data_lists(self):
        """Test importer with empty data lists."""
        importer = Importer(
            registration_data_import=self.registration_data_import,
            households_data=[],
            individuals_data=[],
            documents_data=[],
            accounts_data=[],
            identities_data=[],
        )

        importer._import_documents()
        importer._import_accounts()
        importer._import_identities()

        # Assert no data was created and no errors occurred
        assert len(importer.documents_to_create) == 0
        assert len(importer.accounts_to_create) == 0
        assert len(importer.identities_to_create) == 0
        assert len(importer.errors) == 0
