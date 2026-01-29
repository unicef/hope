import uuid

import pytest

from extras.test_utils.factories import (
    AccountTypeFactory,
    BusinessAreaFactory,
    CountryFactory,
    DocumentTypeFactory,
    FinancialInstitutionFactory,
    IndividualFactory,
    ProgramFactory,
    RegistrationDataImportFactory,
)
from hope.apps.generic_import.generic_upload_service.importer import Importer
from hope.models import Document, Household, Individual, IndividualIdentity


@pytest.fixture
def business_area():
    return BusinessAreaFactory()


@pytest.fixture
def program(business_area):
    return ProgramFactory(business_area=business_area)


@pytest.fixture
def rdi(business_area, program):
    return RegistrationDataImportFactory(
        business_area=business_area,
        program=program,
    )


@pytest.fixture
def country():
    return CountryFactory(name="Somalia", short_name="SOM", iso_code2="SO", iso_code3="SOM")


@pytest.fixture
def document_type():
    return DocumentTypeFactory(key="national_id", label="National ID")


@pytest.fixture
def account_type():
    return AccountTypeFactory(key="mobile_money", label="Mobile Money")


@pytest.fixture
def generic_financial_institutions():
    FinancialInstitutionFactory(name="Generic Bank")
    FinancialInstitutionFactory(name="Generic Telco Company")


@pytest.fixture
def individual(business_area, program):
    return IndividualFactory(
        business_area=business_area,
        program=program,
    )


@pytest.mark.django_db
def test_import_documents_success(rdi, individual, document_type, country, program):
    documents_data = [
        {
            "individual": individual.id,
            "type": document_type.id,
            "document_number": "ID123456",
            "country": country.id,
            "program": program.id,
        },
        {
            "individual": individual.id,
            "type": document_type.id,
            "document_number": "ID789012",
            "country": country.id,
            "program": program.id,
        },
    ]

    importer = Importer(
        registration_data_import=rdi,
        households_data=[],
        individuals_data=[],
        documents_data=documents_data,
        accounts_data=[],
        identities_data=[],
    )

    importer._import_documents()

    assert len(importer.errors) == 0, f"Errors: {importer.errors}"
    assert len(importer.documents_to_create) == 2
    assert importer.documents_to_create[0].document_number == "ID123456"
    assert importer.documents_to_create[1].document_number == "ID789012"


@pytest.mark.django_db
def test_import_documents_with_errors(rdi, individual):
    documents_data = [
        {
            "individual": individual.id,
            "document_number": "ID123456",
        },
    ]

    importer = Importer(
        registration_data_import=rdi,
        households_data=[],
        individuals_data=[],
        documents_data=documents_data,
        accounts_data=[],
        identities_data=[],
    )

    importer._import_documents()

    assert len(importer.documents_to_create) == 0
    assert len(importer.errors) == 1
    assert importer.errors[0]["type"] == "document"
    assert "type" in str(importer.errors[0]["errors"])


@pytest.mark.django_db
def test_import_accounts_success(rdi, individual, account_type, generic_financial_institutions):
    accounts_data = [
        {
            "individual": individual.id,
            "account_type": account_type.id,
            "number": "+252612345678",
            "data": {"provider": "Hormuud"},
        },
        {
            "individual": individual.id,
            "account_type": account_type.id,
            "number": "+252623456789",
            "data": {"provider": "Telesom"},
        },
    ]

    importer = Importer(
        registration_data_import=rdi,
        households_data=[],
        individuals_data=[],
        documents_data=[],
        accounts_data=accounts_data,
        identities_data=[],
    )

    importer._import_accounts()

    assert len(importer.accounts_to_create) == 2
    assert len(importer.errors) == 0
    assert importer.accounts_to_create[0].number == "+252612345678"
    assert importer.accounts_to_create[0].data["provider"] == "Hormuud"
    assert importer.accounts_to_create[1].number == "+252623456789"


@pytest.mark.django_db
def test_import_accounts_with_errors(rdi, individual):
    accounts_data = [
        {
            "individual": individual.id,
            "number": "+252612345678",
        },
    ]

    importer = Importer(
        registration_data_import=rdi,
        households_data=[],
        individuals_data=[],
        documents_data=[],
        accounts_data=accounts_data,
        identities_data=[],
    )

    importer._import_accounts()

    assert len(importer.accounts_to_create) == 0
    assert len(importer.errors) == 1
    assert importer.errors[0]["type"] == "account"
    assert "account_type" in str(importer.errors[0]["errors"])


@pytest.mark.django_db
def test_import_identities_success(rdi, individual, country):
    identities_data = [
        {
            "individual": individual.id,
            "number": "WFP123456",
            "country": country.id,
        },
        {
            "individual": individual.id,
            "number": "WFP789012",
            "country": country.id,
        },
    ]

    importer = Importer(
        registration_data_import=rdi,
        households_data=[],
        individuals_data=[],
        documents_data=[],
        accounts_data=[],
        identities_data=identities_data,
    )

    importer._import_identities()

    assert len(importer.errors) == 0, f"Errors: {importer.errors}"
    assert len(importer.identities_to_create) == 2
    assert importer.identities_to_create[0].number == "WFP123456"
    assert importer.identities_to_create[1].number == "WFP789012"


@pytest.mark.django_db
def test_import_identities_with_errors(rdi, individual):
    identities_data = [
        {
            "individual": individual.id,
        },
    ]

    importer = Importer(
        registration_data_import=rdi,
        households_data=[],
        individuals_data=[],
        documents_data=[],
        accounts_data=[],
        identities_data=identities_data,
    )

    importer._import_identities()

    assert len(importer.identities_to_create) == 0
    assert len(importer.errors) == 1
    assert importer.errors[0]["type"] == "identity"
    assert "number" in str(importer.errors[0]["errors"])


@pytest.mark.django_db
def test_import_all_data_types_together(
    rdi, individual, document_type, country, program, account_type, generic_financial_institutions
):
    documents_data = [
        {
            "individual": individual.id,
            "type": document_type.id,
            "document_number": "ID123456",
            "country": country.id,
            "program": program.id,
        },
    ]

    accounts_data = [
        {
            "individual": individual.id,
            "account_type": account_type.id,
            "number": "+252612345678",
            "data": {"provider": "Hormuud"},
        },
    ]

    identities_data = [
        {
            "individual": individual.id,
            "number": "WFP123456",
            "country": country.id,
        },
    ]

    importer = Importer(
        registration_data_import=rdi,
        households_data=[],
        individuals_data=[],
        documents_data=documents_data,
        accounts_data=accounts_data,
        identities_data=identities_data,
    )

    importer._import_documents()
    importer._import_accounts()
    importer._import_identities()

    assert len(importer.documents_to_create) == 1
    assert len(importer.accounts_to_create) == 1
    assert len(importer.identities_to_create) == 1
    assert len(importer.errors) == 0


@pytest.mark.django_db
def test_import_with_mixed_valid_and_invalid_data(rdi, individual, document_type, country, program):
    documents_data = [
        {
            "individual": individual.id,
            "type": document_type.id,
            "document_number": "ID123456",
            "country": country.id,
            "program": program.id,
        },
        {
            "individual": individual.id,
            "document_number": "ID789012",
        },
    ]

    importer = Importer(
        registration_data_import=rdi,
        households_data=[],
        individuals_data=[],
        documents_data=documents_data,
        accounts_data=[],
        identities_data=[],
    )

    importer._import_documents()

    assert len(importer.documents_to_create) == 1
    assert len(importer.errors) == 1
    assert importer.documents_to_create[0].document_number == "ID123456"
    assert importer.errors[0]["type"] == "document"


@pytest.mark.django_db
def test_empty_data_lists(rdi):
    importer = Importer(
        registration_data_import=rdi,
        households_data=[],
        individuals_data=[],
        documents_data=[],
        accounts_data=[],
        identities_data=[],
    )

    importer._import_documents()
    importer._import_accounts()
    importer._import_identities()

    assert len(importer.documents_to_create) == 0
    assert len(importer.accounts_to_create) == 0
    assert len(importer.identities_to_create) == 0
    assert len(importer.errors) == 0


@pytest.mark.django_db
def test_import_data_full_flow(rdi, document_type, country, program):
    household_temp_id = uuid.uuid4().hex
    individual_temp_id = uuid.uuid4().hex

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
            "household_id": household_temp_id,
            "given_name": "John",
            "family_name": "Doe",
            "full_name": "John Doe",
            "sex": "MALE",
            "birth_date": "1990-01-01",
        },
    ]

    documents_data = [
        {
            "individual_id": individual_temp_id,
            "type": document_type.id,
            "document_number": "PASS123456",
            "country": country.id,
            "program": program.id,
        },
    ]

    importer = Importer(
        registration_data_import=rdi,
        households_data=households_data,
        individuals_data=individuals_data,
        documents_data=documents_data,
        accounts_data=[],
        identities_data=[],
    )

    errors = importer.import_data()

    assert len(errors) == 0, f"Errors: {errors}"

    assert Household.pending_objects.count() == 1
    assert Individual.pending_objects.count() == 1
    assert Document.pending_objects.count() == 1

    household = Household.pending_objects.first()
    individual = Individual.pending_objects.first()
    document = Document.pending_objects.first()

    assert household.size == 3
    assert household.village == "Test Village"
    assert individual.given_name == "John"
    assert individual.full_name == "John Doe"
    assert document.document_number == "PASS123456"


@pytest.mark.django_db
def test_household_individual_relationship(rdi):
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
        registration_data_import=rdi,
        households_data=households_data,
        individuals_data=individuals_data,
        documents_data=[],
        accounts_data=[],
        identities_data=[],
    )

    importer.import_data()

    household = Household.pending_objects.first()
    individual = Individual.pending_objects.first()

    assert individual.household is not None
    assert individual.household.id == household.id
    assert individual.household.village == "Village A"

    assert Individual.pending_objects.filter(household=household).count() == 1
    assert Individual.pending_objects.filter(household=household).first().id == individual.id


@pytest.mark.django_db
def test_document_individual_relationship(rdi, document_type, country, program):
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
            "type": document_type.id,
            "document_number": "ID999888",
            "country": country.id,
            "program": program.id,
        },
    ]

    importer = Importer(
        registration_data_import=rdi,
        households_data=[],
        individuals_data=individuals_data,
        documents_data=documents_data,
        accounts_data=[],
        identities_data=[],
    )

    importer.import_data()

    individual = Individual.pending_objects.first()
    document = Document.pending_objects.first()

    assert document.individual is not None
    assert document.individual.id == individual.id
    assert document.individual.full_name == "Bob Johnson"

    assert Document.pending_objects.filter(individual=individual).count() == 1
    assert Document.pending_objects.filter(individual=individual).first().document_number == "ID999888"


@pytest.mark.django_db
def test_rdi_merge_status_is_pending(rdi, document_type, country, program):
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
            "type": document_type.id,
            "document_number": "DOC123",
            "country": country.id,
            "program": program.id,
        }
    ]
    identities_data = [
        {
            "individual_id": individual_temp_id,
            "number": "WFP999",
            "country": country.id,
        }
    ]

    importer = Importer(
        registration_data_import=rdi,
        households_data=households_data,
        individuals_data=individuals_data,
        documents_data=documents_data,
        accounts_data=[],
        identities_data=identities_data,
    )

    importer.import_data()

    household = Household.pending_objects.first()
    individual = Individual.pending_objects.first()
    document = Document.pending_objects.first()
    identity = IndividualIdentity.pending_objects.first()

    assert household.rdi_merge_status == Household.PENDING
    assert individual.rdi_merge_status == Individual.PENDING
    assert document.rdi_merge_status == Document.PENDING
    assert identity.rdi_merge_status == IndividualIdentity.PENDING


@pytest.mark.django_db
def test_import_individual_with_missing_household(rdi):
    individual_temp_id = uuid.uuid4().hex
    non_existent_household_id = uuid.uuid4().hex

    individuals_data = [
        {
            "id": individual_temp_id,
            "household_id": non_existent_household_id,
            "given_name": "Orphan",
            "family_name": "Individual",
            "full_name": "Orphan Individual",
            "sex": "MALE",
            "birth_date": "1990-01-01",
        }
    ]

    importer = Importer(
        registration_data_import=rdi,
        households_data=[],
        individuals_data=individuals_data,
        documents_data=[],
        accounts_data=[],
        identities_data=[],
    )

    importer._import_households()
    importer._import_individuals()

    assert len(importer.errors) == 1
    assert importer.errors[0]["type"] == "individual"
    assert "household_id" in importer.errors[0]["errors"]
    assert non_existent_household_id in str(importer.errors[0]["errors"]["household_id"])


@pytest.mark.django_db
def test_import_document_with_unknown_country_code(rdi, document_type):
    individual_temp_id = uuid.uuid4().hex

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
            "country": "XXX",
        }
    ]

    importer = Importer(
        registration_data_import=rdi,
        households_data=[],
        individuals_data=individuals_data,
        documents_data=documents_data,
        accounts_data=[],
        identities_data=[],
    )

    importer._import_individuals()
    importer._import_documents()

    doc_errors = [e for e in importer.errors if e["type"] == "document"]
    assert len(doc_errors) == 1
    assert "country" in doc_errors[0]["errors"]
    assert "Unknown country code: XXX" in str(doc_errors[0]["errors"]["country"])


@pytest.mark.django_db
def test_import_document_with_missing_individual(rdi, document_type, country, program):
    non_existent_individual_id = uuid.uuid4().hex

    documents_data = [
        {
            "individual_id": non_existent_individual_id,
            "type": document_type.id,
            "document_number": "DOC123",
            "country": country.id,
            "program": program.id,
        }
    ]

    importer = Importer(
        registration_data_import=rdi,
        households_data=[],
        individuals_data=[],
        documents_data=documents_data,
        accounts_data=[],
        identities_data=[],
    )

    importer._import_documents()

    assert len(importer.errors) == 1
    assert importer.errors[0]["type"] == "document"
    assert "individual_id" in importer.errors[0]["errors"]
    assert non_existent_individual_id in str(importer.errors[0]["errors"]["individual_id"])


@pytest.mark.django_db
def test_import_account_with_missing_individual(rdi, account_type):
    non_existent_individual_id = uuid.uuid4().hex

    accounts_data = [
        {
            "individual_id": non_existent_individual_id,
            "account_type": account_type.id,
            "number": "+252612345678",
            "data": {"provider": "Test"},
        }
    ]

    importer = Importer(
        registration_data_import=rdi,
        households_data=[],
        individuals_data=[],
        documents_data=[],
        accounts_data=accounts_data,
        identities_data=[],
    )

    importer._import_accounts()

    assert len(importer.errors) == 1
    assert importer.errors[0]["type"] == "account"
    assert "individual_id" in importer.errors[0]["errors"]
    assert non_existent_individual_id in str(importer.errors[0]["errors"]["individual_id"])


@pytest.mark.django_db
def test_import_identity_with_missing_individual(rdi, country):
    non_existent_individual_id = uuid.uuid4().hex

    identities_data = [
        {
            "individual_id": non_existent_individual_id,
            "number": "WFP123456",
            "country": country.id,
        }
    ]

    importer = Importer(
        registration_data_import=rdi,
        households_data=[],
        individuals_data=[],
        documents_data=[],
        accounts_data=[],
        identities_data=identities_data,
    )

    importer._import_identities()

    assert len(importer.errors) == 1
    assert importer.errors[0]["type"] == "identity"
    assert "individual_id" in importer.errors[0]["errors"]
    assert non_existent_individual_id in str(importer.errors[0]["errors"]["individual_id"])


@pytest.mark.django_db
def test_import_account_with_unknown_type_key(rdi):
    individual_temp_id = uuid.uuid4().hex

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
            "account_type": "unknown_type_key",
            "number": "+252612345678",
            "data": {"provider": "Test"},
        }
    ]

    importer = Importer(
        registration_data_import=rdi,
        households_data=[],
        individuals_data=individuals_data,
        documents_data=[],
        accounts_data=accounts_data,
        identities_data=[],
    )

    importer._import_individuals()
    importer._import_accounts()

    account_errors = [e for e in importer.errors if e["type"] == "account"]
    assert len(account_errors) == 1
    assert "account_type" in account_errors[0]["errors"]
    assert "Unknown account type: unknown_type_key" in str(account_errors[0]["errors"]["account_type"])


@pytest.mark.django_db
def test_import_document_with_unknown_type_key(rdi):
    individual_temp_id = uuid.uuid4().hex

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
            "type_key": "unknown_document_type",
            "document_number": "DOC123",
            "country": "SOM",
        }
    ]

    importer = Importer(
        registration_data_import=rdi,
        households_data=[],
        individuals_data=individuals_data,
        documents_data=documents_data,
        accounts_data=[],
        identities_data=[],
    )

    importer._import_individuals()
    importer._import_documents()

    doc_errors = [e for e in importer.errors if e["type"] == "document"]
    assert len(doc_errors) == 1
    assert "type_key" in doc_errors[0]["errors"]
    assert "Unknown document type: unknown_document_type" in str(doc_errors[0]["errors"]["type_key"])


@pytest.mark.django_db
def test_import_household_with_validation_errors(rdi):
    household_temp_id = uuid.uuid4().hex

    households_data = [
        {
            "id": household_temp_id,
            "size": "invalid_size",
            "village": "Test Village",
        }
    ]

    importer = Importer(
        registration_data_import=rdi,
        households_data=households_data,
        individuals_data=[],
        documents_data=[],
        accounts_data=[],
        identities_data=[],
    )

    importer._import_households()

    household_errors = [e for e in importer.errors if e["type"] == "household"]
    assert len(household_errors) == 1
    assert "size" in household_errors[0]["errors"]


@pytest.mark.django_db
def test_import_individual_with_validation_errors_no_fk(rdi):
    individual_temp_id = uuid.uuid4().hex

    individuals_data = [
        {
            "id": individual_temp_id,
            "given_name": "Test",
            "family_name": "Person",
            "full_name": "Test Person",
            "sex": "INVALID_SEX",
            "birth_date": "not-a-date",
        }
    ]

    importer = Importer(
        registration_data_import=rdi,
        households_data=[],
        individuals_data=individuals_data,
        documents_data=[],
        accounts_data=[],
        identities_data=[],
    )

    importer._import_individuals()

    individual_errors = [e for e in importer.errors if e["type"] == "individual"]
    assert len(individual_errors) >= 1


@pytest.mark.django_db
def test_save_empty_individuals_list(rdi):
    household_temp_id = uuid.uuid4().hex

    households_data = [
        {
            "id": household_temp_id,
            "size": 0,
            "village": "Test Village",
        }
    ]

    importer = Importer(
        registration_data_import=rdi,
        households_data=households_data,
        individuals_data=[],
        documents_data=[],
        accounts_data=[],
        identities_data=[],
    )

    errors = importer.import_data()

    individual_errors = [e for e in errors if e.get("type") == "individual"]
    assert len(individual_errors) == 0
