import pytest

from extras.test_utils.factories.core import create_afghanistan
from extras.test_utils.factories.geo import CountryFactory
from extras.test_utils.factories.household import (
    DocumentTypeFactory,
    IndividualFactory,
)
from extras.test_utils.factories.payment import AccountTypeFactory, FinancialInstitutionFactory
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

        # Create generic financial institutions for accounts without FI
        FinancialInstitutionFactory(name="Generic Bank")
        FinancialInstitutionFactory(name="Generic Telco Company")

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

    def test_import_data_full_flow(self):
        """Test complete import_data() flow with households, individuals, and documents."""
        import uuid

        from hope.apps.household.models import Document, Household, Individual

        # Create temporary UUIDs (simulating parser output)
        household_temp_id = uuid.uuid4().hex
        individual_temp_id = uuid.uuid4().hex

        # Prepare test data as parser would return it
        households_data = [
            {
                "id": household_temp_id,
                "size": 3,
                "village": "Test Village",
                "address": "Test Address",
            },
        ]

        individuals_data = [
            {
                "id": individual_temp_id,
                "household_id": household_temp_id,  # Link to household via temp ID
                "given_name": "John",
                "family_name": "Doe",
                "full_name": "John Doe",
                "sex": "MALE",
                "birth_date": "1990-01-01",
            },
        ]

        documents_data = [
            {
                "individual_id": individual_temp_id,  # Link to individual via temp ID
                "type": self.document_type.id,
                "document_number": "PASS123456",
                "country": self.country.id,
                "program": self.program.id,
            },
        ]

        # Create importer and run import_data()
        importer = Importer(
            registration_data_import=self.registration_data_import,
            households_data=households_data,
            individuals_data=individuals_data,
            documents_data=documents_data,
            accounts_data=[],
            identities_data=[],
        )

        errors = importer.import_data()

        # Assert no errors occurred
        assert len(errors) == 0, f"Errors: {errors}"

        # Assert objects were saved to database (use pending_objects for PENDING status)
        assert Household.pending_objects.count() == 1
        assert Individual.pending_objects.count() == 1
        assert Document.pending_objects.count() == 1

        # Get created objects
        household = Household.pending_objects.first()
        individual = Individual.pending_objects.first()
        document = Document.pending_objects.first()

        # Assert data integrity
        assert household.size == 3
        assert household.village == "Test Village"
        assert individual.given_name == "John"
        assert individual.full_name == "John Doe"
        assert document.document_number == "PASS123456"

    def test_household_individual_relationship(self):
        """Test that Individual.household FK correctly points to created Household."""
        import uuid

        from hope.apps.household.models import Household, Individual

        household_temp_id = uuid.uuid4().hex
        individual_temp_id = uuid.uuid4().hex

        households_data = [
            {
                "id": household_temp_id,
                "size": 2,
                "village": "Village A",
            },
        ]

        individuals_data = [
            {
                "id": individual_temp_id,
                "household_id": household_temp_id,
                "given_name": "Jane",
                "family_name": "Smith",
                "full_name": "Jane Smith",
                "sex": "FEMALE",
                "birth_date": "1995-05-15",
            },
        ]

        importer = Importer(
            registration_data_import=self.registration_data_import,
            households_data=households_data,
            individuals_data=individuals_data,
            documents_data=[],
            accounts_data=[],
            identities_data=[],
        )

        importer.import_data()

        # Get created objects (use pending_objects for PENDING status)
        household = Household.pending_objects.first()
        individual = Individual.pending_objects.first()

        # Assert FK relationship is correct
        assert individual.household is not None
        assert individual.household.id == household.id
        assert individual.household.village == "Village A"

        # Assert Individual is in Household's reverse relation (use pending_objects filter)
        assert Individual.pending_objects.filter(household=household).count() == 1
        assert Individual.pending_objects.filter(household=household).first().id == individual.id

    def test_document_individual_relationship(self):
        """Test that Document.individual FK correctly points to created Individual."""
        import uuid

        from hope.apps.household.models import Document, Individual

        individual_temp_id = uuid.uuid4().hex

        individuals_data = [
            {
                "id": individual_temp_id,
                "given_name": "Bob",
                "family_name": "Johnson",
                "full_name": "Bob Johnson",
                "sex": "MALE",
                "birth_date": "1985-03-20",
            },
        ]

        documents_data = [
            {
                "individual_id": individual_temp_id,
                "type": self.document_type.id,
                "document_number": "ID999888",
                "country": self.country.id,
                "program": self.program.id,
            },
        ]

        importer = Importer(
            registration_data_import=self.registration_data_import,
            households_data=[],
            individuals_data=individuals_data,
            documents_data=documents_data,
            accounts_data=[],
            identities_data=[],
        )

        importer.import_data()

        # Get created objects (use pending_objects for PENDING status)
        individual = Individual.pending_objects.first()
        document = Document.pending_objects.first()

        # Assert FK relationship is correct
        assert document.individual is not None
        assert document.individual.id == individual.id
        assert document.individual.full_name == "Bob Johnson"

        # Assert Document is in Individual's reverse relation (use pending_objects filter)
        assert Document.pending_objects.filter(individual=individual).count() == 1
        assert Document.pending_objects.filter(individual=individual).first().document_number == "ID999888"

    def test_rdi_merge_status_is_pending(self):
        """Test that all created objects have rdi_merge_status = PENDING."""
        import uuid

        from hope.apps.household.models import Document, Household, Individual, IndividualIdentity

        household_temp_id = uuid.uuid4().hex
        individual_temp_id = uuid.uuid4().hex

        households_data = [{"id": household_temp_id, "size": 1}]
        individuals_data = [
            {
                "id": individual_temp_id,
                "household_id": household_temp_id,
                "given_name": "Test",
                "family_name": "User",
                "full_name": "Test User",
                "sex": "MALE",
                "birth_date": "2000-01-01",
            }
        ]
        documents_data = [
            {
                "individual_id": individual_temp_id,
                "type": self.document_type.id,
                "document_number": "DOC123",
                "country": self.country.id,
                "program": self.program.id,
            }
        ]
        identities_data = [
            {
                "individual_id": individual_temp_id,
                "number": "WFP999",
                "country": self.country.id,
            }
        ]

        importer = Importer(
            registration_data_import=self.registration_data_import,
            households_data=households_data,
            individuals_data=individuals_data,
            documents_data=documents_data,
            accounts_data=[],
            identities_data=identities_data,
        )

        importer.import_data()

        # Assert all objects have rdi_merge_status = PENDING (use pending_objects)
        household = Household.pending_objects.first()
        individual = Individual.pending_objects.first()
        document = Document.pending_objects.first()
        identity = IndividualIdentity.pending_objects.first()

        assert household.rdi_merge_status == Household.PENDING
        assert individual.rdi_merge_status == Individual.PENDING
        assert document.rdi_merge_status == Document.PENDING
        assert identity.rdi_merge_status == IndividualIdentity.PENDING

    def test_import_individual_with_missing_household(self):
        """Test that individual with non-existent household_id produces error."""
        import uuid

        individual_temp_id = uuid.uuid4().hex
        non_existent_household_id = uuid.uuid4().hex

        individuals_data = [
            {
                "id": individual_temp_id,
                "household_id": non_existent_household_id,  # This household doesn't exist
                "given_name": "Orphan",
                "family_name": "Individual",
                "full_name": "Orphan Individual",
                "sex": "MALE",
                "birth_date": "1990-01-01",
            }
        ]

        importer = Importer(
            registration_data_import=self.registration_data_import,
            households_data=[],  # No households
            individuals_data=individuals_data,
            documents_data=[],
            accounts_data=[],
            identities_data=[],
        )

        importer._import_households()
        importer._import_individuals()

        # Assert error was recorded
        assert len(importer.errors) == 1
        assert importer.errors[0]["type"] == "individual"
        assert "household_id" in importer.errors[0]["errors"]
        assert non_existent_household_id in str(importer.errors[0]["errors"]["household_id"])

    def test_import_document_with_unknown_country_code(self):
        """Test that document with unknown country code produces error."""
        import uuid

        individual_temp_id = uuid.uuid4().hex

        # First create individual
        individuals_data = [
            {
                "id": individual_temp_id,
                "given_name": "Test",
                "family_name": "Person",
                "full_name": "Test Person",
                "sex": "MALE",
                "birth_date": "1990-01-01",
            }
        ]

        documents_data = [
            {
                "individual_id": individual_temp_id,
                "type_key": "national_id",
                "document_number": "DOC123",
                "country": "XXX",  # Invalid country code
            }
        ]

        importer = Importer(
            registration_data_import=self.registration_data_import,
            households_data=[],
            individuals_data=individuals_data,
            documents_data=documents_data,
            accounts_data=[],
            identities_data=[],
        )

        importer._import_individuals()
        importer._import_documents()

        # Assert error was recorded for unknown country
        doc_errors = [e for e in importer.errors if e["type"] == "document"]
        assert len(doc_errors) == 1
        assert "country" in doc_errors[0]["errors"]
        assert "Unknown country code: XXX" in str(doc_errors[0]["errors"]["country"])

    def test_import_document_with_missing_individual(self):
        """Test that document with non-existent individual_id produces error."""
        import uuid

        non_existent_individual_id = uuid.uuid4().hex

        documents_data = [
            {
                "individual_id": non_existent_individual_id,
                "type": self.document_type.id,
                "document_number": "DOC123",
                "country": self.country.id,
                "program": self.program.id,
            }
        ]

        importer = Importer(
            registration_data_import=self.registration_data_import,
            households_data=[],
            individuals_data=[],  # No individuals
            documents_data=documents_data,
            accounts_data=[],
            identities_data=[],
        )

        importer._import_documents()

        # Assert error was recorded
        assert len(importer.errors) == 1
        assert importer.errors[0]["type"] == "document"
        assert "individual_id" in importer.errors[0]["errors"]
        assert non_existent_individual_id in str(importer.errors[0]["errors"]["individual_id"])

    def test_import_account_with_missing_individual(self):
        """Test that account with non-existent individual_id produces error."""
        import uuid

        non_existent_individual_id = uuid.uuid4().hex

        accounts_data = [
            {
                "individual_id": non_existent_individual_id,
                "account_type": self.account_type.id,
                "number": "+252612345678",
                "data": {"provider": "Test"},
            }
        ]

        importer = Importer(
            registration_data_import=self.registration_data_import,
            households_data=[],
            individuals_data=[],  # No individuals
            documents_data=[],
            accounts_data=accounts_data,
            identities_data=[],
        )

        importer._import_accounts()

        # Assert error was recorded
        assert len(importer.errors) == 1
        assert importer.errors[0]["type"] == "account"
        assert "individual_id" in importer.errors[0]["errors"]
        assert non_existent_individual_id in str(importer.errors[0]["errors"]["individual_id"])

    def test_import_identity_with_missing_individual(self):
        """Test that identity with non-existent individual_id produces error."""
        import uuid

        non_existent_individual_id = uuid.uuid4().hex

        identities_data = [
            {
                "individual_id": non_existent_individual_id,
                "number": "WFP123456",
                "country": self.country.id,
            }
        ]

        importer = Importer(
            registration_data_import=self.registration_data_import,
            households_data=[],
            individuals_data=[],  # No individuals
            documents_data=[],
            accounts_data=[],
            identities_data=identities_data,
        )

        importer._import_identities()

        # Assert error was recorded
        assert len(importer.errors) == 1
        assert importer.errors[0]["type"] == "identity"
        assert "individual_id" in importer.errors[0]["errors"]
        assert non_existent_individual_id in str(importer.errors[0]["errors"]["individual_id"])

    def test_import_account_with_unknown_type_key(self):
        """Test that account with unknown account_type key produces error."""
        import uuid

        individual_temp_id = uuid.uuid4().hex

        # First create individual
        individuals_data = [
            {
                "id": individual_temp_id,
                "given_name": "Test",
                "family_name": "Person",
                "full_name": "Test Person",
                "sex": "MALE",
                "birth_date": "1990-01-01",
            }
        ]

        accounts_data = [
            {
                "individual_id": individual_temp_id,
                "account_type": "unknown_type_key",  # String key that doesn't exist
                "number": "+252612345678",
                "data": {"provider": "Test"},
            }
        ]

        importer = Importer(
            registration_data_import=self.registration_data_import,
            households_data=[],
            individuals_data=individuals_data,
            documents_data=[],
            accounts_data=accounts_data,
            identities_data=[],
        )

        importer._import_individuals()
        importer._import_accounts()

        # Assert error was recorded for unknown account type
        account_errors = [e for e in importer.errors if e["type"] == "account"]
        assert len(account_errors) == 1
        assert "account_type" in account_errors[0]["errors"]
        assert "Unknown account type: unknown_type_key" in str(account_errors[0]["errors"]["account_type"])

    def test_import_document_with_unknown_type_key(self):
        """Test that document with unknown type_key produces error."""
        import uuid

        individual_temp_id = uuid.uuid4().hex

        # First create individual
        individuals_data = [
            {
                "id": individual_temp_id,
                "given_name": "Test",
                "family_name": "Person",
                "full_name": "Test Person",
                "sex": "MALE",
                "birth_date": "1990-01-01",
            }
        ]

        documents_data = [
            {
                "individual_id": individual_temp_id,
                "type_key": "unknown_document_type",  # Type key that doesn't exist
                "document_number": "DOC123",
                "country": "SOM",
            }
        ]

        importer = Importer(
            registration_data_import=self.registration_data_import,
            households_data=[],
            individuals_data=individuals_data,
            documents_data=documents_data,
            accounts_data=[],
            identities_data=[],
        )

        importer._import_individuals()
        importer._import_documents()

        # Assert error was recorded for unknown document type
        doc_errors = [e for e in importer.errors if e["type"] == "document"]
        assert len(doc_errors) == 1
        assert "type_key" in doc_errors[0]["errors"]
        assert "Unknown document type: unknown_document_type" in str(doc_errors[0]["errors"]["type_key"])

    def test_import_household_with_validation_errors(self):
        """Test that household with invalid data produces validation error."""
        import uuid

        household_temp_id = uuid.uuid4().hex

        # Household with invalid data (size is required and must be positive)
        households_data = [
            {
                "id": household_temp_id,
                "size": "invalid_size",  # Invalid - should be integer
                "village": "Test Village",
            }
        ]

        importer = Importer(
            registration_data_import=self.registration_data_import,
            households_data=households_data,
            individuals_data=[],
            documents_data=[],
            accounts_data=[],
            identities_data=[],
        )

        importer._import_households()

        # Assert error was recorded
        household_errors = [e for e in importer.errors if e["type"] == "household"]
        assert len(household_errors) == 1
        assert "size" in household_errors[0]["errors"]

    def test_import_individual_with_validation_errors_no_fk(self):
        """Test that individual with invalid field data produces validation error."""
        import uuid

        individual_temp_id = uuid.uuid4().hex

        # Individual with invalid sex value
        individuals_data = [
            {
                "id": individual_temp_id,
                "given_name": "Test",
                "family_name": "Person",
                "full_name": "Test Person",
                "sex": "INVALID_SEX",  # Invalid - not in choices
                "birth_date": "not-a-date",  # Invalid date format
            }
        ]

        importer = Importer(
            registration_data_import=self.registration_data_import,
            households_data=[],
            individuals_data=individuals_data,
            documents_data=[],
            accounts_data=[],
            identities_data=[],
        )

        importer._import_individuals()

        # Assert error was recorded
        individual_errors = [e for e in importer.errors if e["type"] == "individual"]
        assert len(individual_errors) >= 1

    def test_save_empty_individuals_list(self):
        """Test that _save_individuals handles empty list correctly."""
        import uuid

        household_temp_id = uuid.uuid4().hex

        # Only household, no individuals
        households_data = [
            {
                "id": household_temp_id,
                "size": 0,
                "village": "Test Village",
            }
        ]

        importer = Importer(
            registration_data_import=self.registration_data_import,
            households_data=households_data,
            individuals_data=[],  # Empty
            documents_data=[],
            accounts_data=[],
            identities_data=[],
        )

        # This should not raise any exceptions
        errors = importer.import_data()

        # No errors expected for empty individuals list
        individual_errors = [e for e in errors if e.get("type") == "individual"]
        assert len(individual_errors) == 0
