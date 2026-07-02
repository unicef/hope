import datetime
import json
from typing import Any

from django.utils import timezone
import pytest

from extras.test_utils.factories.account import UserFactory
from extras.test_utils.factories.aurora import OrganizationFactory, ProjectFactory, RecordFactory, RegistrationFactory
from extras.test_utils.factories.core import BusinessAreaFactory, DataCollectingTypeFactory
from extras.test_utils.factories.geo import CountryFactory
from extras.test_utils.factories.household import DocumentTypeFactory
from extras.test_utils.factories.payment import (
    AccountTypeFactory,
    DeliveryMechanismFactory,
    FinancialInstitutionFactory,
)
from extras.test_utils.factories.program import ProgramFactory
from hope.apps.core.utils import IDENTIFICATION_TYPE_TO_KEY_MAPPING
from hope.apps.household.const import IDENTIFICATION_TYPE_TAX_ID, ROLE_PRIMARY
from hope.contrib.aurora.models import Record
from hope.contrib.aurora.services.ukraine_flex_registration_service import UkraineUSDCRegistrationService
from hope.models import (
    DataCollectingType,
    DeliveryMechanism,
    FinancialInstitution,
    PendingAccount,
    PendingDocument,
    PendingHousehold,
    PendingIndividual,
    PendingIndividualRoleInHousehold,
    Program,
)

pytestmark = [pytest.mark.django_db, pytest.mark.usefixtures("mock_elasticsearch")]


@pytest.fixture
def business_area() -> Any:
    return BusinessAreaFactory(slug="some-ukraine-slug")


@pytest.fixture
def data_collecting_type(business_area: Any) -> DataCollectingType:
    data_collecting_type = DataCollectingTypeFactory(label="SomeFull", code="some_full")
    data_collecting_type.limit_to.add(business_area)
    return data_collecting_type


@pytest.fixture
def program(business_area: Any, data_collecting_type: DataCollectingType) -> Program:
    return ProgramFactory(
        status=Program.ACTIVE,
        business_area=business_area,
        data_collecting_type=data_collecting_type,
    )


@pytest.fixture
def organization(business_area: Any) -> Any:
    return OrganizationFactory(business_area=business_area, slug=business_area.slug)


@pytest.fixture
def project(organization: Any, program: Program) -> Any:
    return ProjectFactory(name="usdc_project", organization=organization, programme=program)


@pytest.fixture
def registration(project: Any) -> Any:
    return RegistrationFactory(name="usdc_registration", project=project)


@pytest.fixture
def user() -> Any:
    return UserFactory()


@pytest.fixture
def ukraine_country() -> Any:
    return CountryFactory(name="Ukraine", short_name="Ukraine", iso_code2="UA", iso_code3="UKR", iso_num="0804")


@pytest.fixture
def tax_id_document_type() -> Any:
    return DocumentTypeFactory(
        key=IDENTIFICATION_TYPE_TO_KEY_MAPPING[IDENTIFICATION_TYPE_TAX_ID],
        label=IDENTIFICATION_TYPE_TAX_ID,
    )


@pytest.fixture
def generic_crypto_fi() -> FinancialInstitution:
    return FinancialInstitutionFactory(
        name="Generic Crypto",
        type=FinancialInstitution.FinancialInstitutionType.OTHER,
        country=None,
    )


@pytest.fixture
def digital_wallet_delivery_mechanism(generic_crypto_fi: FinancialInstitution) -> DeliveryMechanism:
    return DeliveryMechanismFactory(
        code="transfer_to_digital_wallet",
        name="Transfer to Digital Wallet",
        transfer_type=DeliveryMechanism.TransferType.DIGITAL,
        account_type=AccountTypeFactory(key="crypto", label="Crypto"),
    )


@pytest.fixture
def submission_timestamp() -> datetime.datetime:
    return timezone.make_aware(datetime.datetime(2026, 6, 15))


@pytest.fixture
def usdc_record(registration: Any, submission_timestamp: datetime.datetime) -> Record:
    return RecordFactory(
        registration=registration.source_id,
        timestamp=submission_timestamp,
        source_id=1,
        fields={
            "household": [{"consent_h_c": True}],
            "individuals": [
                {
                    "given_name_i_c": "Olena",
                    "middle_name_i_c": "Ivanivna",
                    "family_name_i_c": "Shevchenko",
                    "birth_date": "1990-05-12",
                    "gender_i_c": "female",
                    "phone_no_i_c": "0501112233",
                    "relationship_i_c": "head",
                    "role_i_c": "y",
                    "tax_id_no_i_c": "1234567890",
                    "wallet_address_i_c": "0xABCDEF0123456789",
                    "wallet_name_i_c": "MetaMask",
                    "wallet_num_image_i_f": "d2FsbGV0X251bV9pbWFnZQ==",
                    "id_wallet_image_i_f": "aWRfd2FsbGV0X2ltYWdl",
                }
            ],
        },
        files=json.dumps({}).encode(),
    )


def test_creates_household_in_ukraine_for_regular_programme(
    registration: Any,
    user: Any,
    program: Program,
    ukraine_country: Any,
    tax_id_document_type: Any,
    digital_wallet_delivery_mechanism: DeliveryMechanism,
    usdc_record: Record,
    submission_timestamp: datetime.datetime,
) -> None:
    service = UkraineUSDCRegistrationService(registration)
    rdi = service.create_rdi(user, "usdc rdi")

    service.process_records(rdi.id, [usdc_record.id])

    household = PendingHousehold.objects.get(registration_data_import=rdi)
    assert household.program == program
    assert household.country.iso_code2 == "UA"
    assert household.country_origin.iso_code2 == "UA"
    assert household.consent is True
    assert household.first_registration_date == submission_timestamp


def test_consent_read_from_form_when_declined(
    registration: Any,
    user: Any,
    ukraine_country: Any,
    tax_id_document_type: Any,
    digital_wallet_delivery_mechanism: DeliveryMechanism,
    submission_timestamp: datetime.datetime,
) -> None:
    record = RecordFactory(
        registration=registration.source_id,
        timestamp=submission_timestamp,
        source_id=2,
        fields={
            "household": [{"consent_h_c": "n"}],
            "individuals": [
                {
                    "given_name_i_c": "Petro",
                    "family_name_i_c": "Bondarenko",
                    "birth_date": "1985-03-01",
                    "gender_i_c": "male",
                    "relationship_i_c": "head",
                    "role_i_c": "y",
                    "tax_id_no_i_c": "9876543210",
                    "wallet_address_i_c": "0x0011223344556677",
                    "wallet_name_i_c": "Trust",
                }
            ],
        },
        files=json.dumps({}).encode(),
    )
    service = UkraineUSDCRegistrationService(registration)
    rdi = service.create_rdi(user, "usdc rdi")

    service.process_records(rdi.id, [record.id])

    household = PendingHousehold.objects.get(registration_data_import=rdi)
    assert household.consent is False


def test_consent_defaults_to_true_when_not_in_form(
    registration: Any,
    user: Any,
    ukraine_country: Any,
    tax_id_document_type: Any,
    submission_timestamp: datetime.datetime,
) -> None:
    record = RecordFactory(
        registration=registration.source_id,
        timestamp=submission_timestamp,
        source_id=7,
        fields={
            "household": [{}],
            "individuals": [
                {
                    "given_name_i_c": "Ivan",
                    "family_name_i_c": "Kovalenko",
                    "birth_date": "1970-07-07",
                    "gender_i_c": "male",
                    "relationship_i_c": "head",
                    "role_i_c": "y",
                    "tax_id_no_i_c": "5555555555",
                }
            ],
        },
        files=json.dumps({}).encode(),
    )
    service = UkraineUSDCRegistrationService(registration)
    rdi = service.create_rdi(user, "usdc rdi")

    service.process_records(rdi.id, [record.id])

    household = PendingHousehold.objects.get(registration_data_import=rdi)
    assert household.consent is True


def test_individual_full_name_concatenated_and_birth_date_not_estimated(
    registration: Any,
    user: Any,
    ukraine_country: Any,
    tax_id_document_type: Any,
    digital_wallet_delivery_mechanism: DeliveryMechanism,
    usdc_record: Record,
) -> None:
    service = UkraineUSDCRegistrationService(registration)
    rdi = service.create_rdi(user, "usdc rdi")

    service.process_records(rdi.id, [usdc_record.id])

    individual = PendingIndividual.objects.get(registration_data_import=rdi)
    assert individual.full_name == "Olena Ivanivna Shevchenko"
    assert str(individual.birth_date) == "1990-05-12"
    assert individual.estimated_birth_date is False


def test_individual_wallet_fields_populated(
    registration: Any,
    user: Any,
    ukraine_country: Any,
    tax_id_document_type: Any,
    digital_wallet_delivery_mechanism: DeliveryMechanism,
    usdc_record: Record,
) -> None:
    service = UkraineUSDCRegistrationService(registration)
    rdi = service.create_rdi(user, "usdc rdi")

    service.process_records(rdi.id, [usdc_record.id])

    individual = PendingIndividual.objects.get(registration_data_import=rdi)
    assert individual.wallet_address == "0xABCDEF0123456789"
    assert individual.wallet_name == "MetaMask"


def test_wallet_images_stored_as_flex_fields(
    registration: Any,
    user: Any,
    ukraine_country: Any,
    tax_id_document_type: Any,
    digital_wallet_delivery_mechanism: DeliveryMechanism,
    usdc_record: Record,
) -> None:
    service = UkraineUSDCRegistrationService(registration)
    rdi = service.create_rdi(user, "usdc rdi")

    service.process_records(rdi.id, [usdc_record.id])

    individual = PendingIndividual.objects.get(registration_data_import=rdi)
    assert individual.flex_fields["wallet_num_image_i_f"] == "d2FsbGV0X251bV9pbWFnZQ=="
    assert individual.flex_fields["id_wallet_image_i_f"] == "aWRfd2FsbGV0X2ltYWdl"


def test_creates_only_tax_id_document(
    registration: Any,
    user: Any,
    ukraine_country: Any,
    tax_id_document_type: Any,
    digital_wallet_delivery_mechanism: DeliveryMechanism,
    usdc_record: Record,
) -> None:
    service = UkraineUSDCRegistrationService(registration)
    rdi = service.create_rdi(user, "usdc rdi")

    service.process_records(rdi.id, [usdc_record.id])

    individual = PendingIndividual.objects.get(registration_data_import=rdi)
    documents = PendingDocument.objects.filter(individual=individual)
    assert documents.count() == 1
    assert documents.first().document_number == "1234567890"
    assert documents.first().type.key == IDENTIFICATION_TYPE_TO_KEY_MAPPING[IDENTIFICATION_TYPE_TAX_ID]


def test_wallet_account_created_for_collector(
    registration: Any,
    user: Any,
    ukraine_country: Any,
    tax_id_document_type: Any,
    digital_wallet_delivery_mechanism: DeliveryMechanism,
    generic_crypto_fi: FinancialInstitution,
    usdc_record: Record,
) -> None:
    service = UkraineUSDCRegistrationService(registration)
    rdi = service.create_rdi(user, "usdc rdi")

    service.process_records(rdi.id, [usdc_record.id])

    individual = PendingIndividual.objects.get(registration_data_import=rdi)
    account = PendingAccount.objects.get(individual=individual)
    assert account.account_type == digital_wallet_delivery_mechanism.account_type
    assert account.number == "0xABCDEF0123456789"
    assert account.financial_institution == generic_crypto_fi
    assert account.data == {"wallet_address": "0xABCDEF0123456789", "wallet_name": "MetaMask"}


def test_wallet_accounts_created_for_each_individual_with_wallet(
    registration: Any,
    user: Any,
    ukraine_country: Any,
    tax_id_document_type: Any,
    digital_wallet_delivery_mechanism: DeliveryMechanism,
    generic_crypto_fi: FinancialInstitution,
    submission_timestamp: datetime.datetime,
) -> None:
    record = RecordFactory(
        registration=registration.source_id,
        timestamp=submission_timestamp,
        source_id=4,
        fields={
            "household": [{"consent_h_c": True}],
            "individuals": [
                {
                    "given_name_i_c": "Olena",
                    "family_name_i_c": "Shevchenko",
                    "birth_date": "1990-05-12",
                    "gender_i_c": "female",
                    "relationship_i_c": "head",
                    "role_i_c": "y",
                    "wallet_address_i_c": "0xAAA1",
                    "wallet_name_i_c": "MetaMask",
                },
                {
                    "given_name_i_c": "Mykola",
                    "family_name_i_c": "Shevchenko",
                    "birth_date": "2010-08-08",
                    "gender_i_c": "male",
                    "relationship_i_c": "son_daughter",
                    "role_i_c": "n",
                    "wallet_address_i_c": "0xBBB2",
                    "wallet_name_i_c": "Trust",
                },
            ],
        },
        files=json.dumps({}).encode(),
    )
    service = UkraineUSDCRegistrationService(registration)
    rdi = service.create_rdi(user, "usdc rdi")

    service.process_records(rdi.id, [record.id])

    accounts = PendingAccount.objects.filter(individual__registration_data_import=rdi)
    assert accounts.count() == 2
    assert set(accounts.values_list("number", flat=True)) == {"0xAAA1", "0xBBB2"}


def test_import_errors_when_delivery_mechanism_not_configured(
    registration: Any,
    user: Any,
    ukraine_country: Any,
    tax_id_document_type: Any,
    usdc_record: Record,
) -> None:
    service = UkraineUSDCRegistrationService(registration)
    rdi = service.create_rdi(user, "usdc rdi")

    service.process_records(rdi.id, [usdc_record.id])

    usdc_record.refresh_from_db()
    assert usdc_record.status == Record.STATUS_ERROR
    assert not PendingHousehold.objects.filter(registration_data_import=rdi).exists()


def test_no_wallet_account_when_address_missing(
    registration: Any,
    user: Any,
    ukraine_country: Any,
    tax_id_document_type: Any,
    digital_wallet_delivery_mechanism: DeliveryMechanism,
    generic_crypto_fi: FinancialInstitution,
    submission_timestamp: datetime.datetime,
) -> None:
    record = RecordFactory(
        registration=registration.source_id,
        timestamp=submission_timestamp,
        source_id=6,
        fields={
            "household": [{"consent_h_c": True}],
            "individuals": [
                {
                    "given_name_i_c": "Ivan",
                    "family_name_i_c": "Kovalenko",
                    "birth_date": "1970-07-07",
                    "gender_i_c": "male",
                    "relationship_i_c": "head",
                    "role_i_c": "y",
                    "wallet_name_i_c": "Trust",
                }
            ],
        },
        files=json.dumps({}).encode(),
    )
    service = UkraineUSDCRegistrationService(registration)
    rdi = service.create_rdi(user, "usdc rdi")

    service.process_records(rdi.id, [record.id])

    individual = PendingIndividual.objects.get(registration_data_import=rdi)
    assert individual.wallet_name == "Trust"
    assert not PendingAccount.objects.filter(individual=individual).exists()


def test_role_creates_primary_collector(
    registration: Any,
    user: Any,
    ukraine_country: Any,
    tax_id_document_type: Any,
    digital_wallet_delivery_mechanism: DeliveryMechanism,
    usdc_record: Record,
) -> None:
    service = UkraineUSDCRegistrationService(registration)
    rdi = service.create_rdi(user, "usdc rdi")

    service.process_records(rdi.id, [usdc_record.id])

    household = PendingHousehold.objects.get(registration_data_import=rdi)
    individual = PendingIndividual.objects.get(registration_data_import=rdi)
    assert household.head_of_household == individual
    assert PendingIndividualRoleInHousehold.objects.filter(
        household=household, individual=individual, role=ROLE_PRIMARY
    ).exists()
