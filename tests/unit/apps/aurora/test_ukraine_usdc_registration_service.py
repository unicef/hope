import datetime
import json
from typing import Any

from django.core.files.storage import default_storage
from django.utils import timezone
import pytest

from extras.test_utils.factories.account import UserFactory
from extras.test_utils.factories.aurora import OrganizationFactory, ProjectFactory, RecordFactory, RegistrationFactory
from extras.test_utils.factories.core import (
    BusinessAreaFactory,
    DataCollectingTypeFactory,
    FlexibleAttributeFactory,
)
from extras.test_utils.factories.geo import CountryFactory
from extras.test_utils.factories.household import DocumentTypeFactory
from extras.test_utils.factories.payment import (
    AccountTypeFactory,
    DeliveryMechanismFactory,
    FinancialInstitutionFactory,
)
from extras.test_utils.factories.program import ProgramFactory
from hope.apps.core.utils import IDENTIFICATION_TYPE_TO_KEY_MAPPING, resolve_flex_fields_choices_to_string
from hope.apps.household.const import IDENTIFICATION_TYPE_TAX_ID, ROLE_PRIMARY
from hope.contrib.aurora.models import Record
from hope.contrib.aurora.services.ukraine_flex_registration_service import UkraineUSDCRegistrationService
from hope.models import (
    AccountAttachment,
    DataCollectingType,
    DeliveryMechanism,
    FinancialInstitution,
    FlexibleAttribute,
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
            "consent": [{"consent_h_c": ["1"]}],
            "individual_details": [
                {
                    "given_name_i_c": "Olena",
                    "middle_name_i_c": "Ivanivna",
                    "family_name_i_c": "Shevchenko",
                    "birth_date": "1990-05-12",
                    "gender_i_c": "female",
                    "phone_no_i_c": "0501112233",
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
    assert household.size == 1
    assert household.first_registration_date == submission_timestamp


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


def test_ukrainian_phone_number_normalized(
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
    assert individual.phone_no == "+380501112233"


def test_wallet_stored_on_account(
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
    account = PendingAccount.objects.get(individual=individual)
    assert account.data == {"wallet_address": "0xABCDEF0123456789", "wallet_name": "MetaMask"}


def test_wallet_images_stored_as_saved_files(
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
    account = PendingAccount.objects.get(individual=individual)
    attachment = AccountAttachment.objects.get(account=account)
    id_image_path = individual.flex_fields["id_wallet_image_i_f"]
    assert "wallet_num_image_i_f" not in individual.flex_fields
    assert attachment.title == "Wallet number image"
    assert attachment.file.name.endswith(".jpg")
    assert default_storage.exists(attachment.file.name)
    assert default_storage.exists(id_image_path)


def test_individual_detail_flex_image_resolves_to_url(
    registration: Any,
    user: Any,
    ukraine_country: Any,
    tax_id_document_type: Any,
    digital_wallet_delivery_mechanism: DeliveryMechanism,
    usdc_record: Record,
) -> None:
    FlexibleAttributeFactory(name="id_wallet_image_i_f", type=FlexibleAttribute.IMAGE)
    service = UkraineUSDCRegistrationService(registration)
    rdi = service.create_rdi(user, "usdc rdi")

    service.process_records(rdi.id, [usdc_record.id])

    individual = PendingIndividual.objects.get(registration_data_import=rdi)
    resolved = resolve_flex_fields_choices_to_string(individual)

    assert "wallet_num_image_i_f" not in resolved
    assert resolved["id_wallet_image_i_f"].endswith(".jpg")


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


def test_single_individual_is_head_and_primary_collector(
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


def test_rejects_record_with_more_than_one_individual(
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
        source_id=4,
        fields={
            "consent": [{"consent_h_c": ["1"]}],
            "individual_details": [
                {
                    "given_name_i_c": "Olena",
                    "family_name_i_c": "Shevchenko",
                    "birth_date": "1990-05-12",
                    "gender_i_c": "female",
                    "wallet_address_i_c": "0xAAA1",
                    "wallet_name_i_c": "MetaMask",
                },
                {
                    "given_name_i_c": "Mykola",
                    "family_name_i_c": "Shevchenko",
                    "birth_date": "2010-08-08",
                    "gender_i_c": "male",
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

    record.refresh_from_db()
    assert record.status == Record.STATUS_ERROR
    assert not PendingHousehold.objects.filter(registration_data_import=rdi).exists()


def test_invalid_individual_rejects_record(
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
        source_id=8,
        fields={
            "consent": [{"consent_h_c": ["1"]}],
            "individual_details": [
                {
                    "given_name_i_c": "Olena",
                    "family_name_i_c": "Shevchenko",
                    "birth_date": "1990-99-99",
                    "gender_i_c": "female",
                    "tax_id_no_i_c": "1234567890",
                    "wallet_address_i_c": "0xABCDEF0123456789",
                    "wallet_name_i_c": "MetaMask",
                }
            ],
        },
        files=json.dumps({}).encode(),
    )
    service = UkraineUSDCRegistrationService(registration)
    rdi = service.create_rdi(user, "usdc rdi")

    service.process_records(rdi.id, [record.id])

    record.refresh_from_db()
    assert record.status == Record.STATUS_ERROR
    assert "individual nr 1" in record.error_message
    assert not PendingHousehold.objects.filter(registration_data_import=rdi).exists()


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
            "consent": [{"consent_h_c": ["1"]}],
            "individual_details": [
                {
                    "given_name_i_c": "Ivan",
                    "family_name_i_c": "Kovalenko",
                    "birth_date": "1970-07-07",
                    "gender_i_c": "male",
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
    assert not PendingAccount.objects.filter(individual=individual).exists()


def test_no_attachment_when_wallet_address_missing(
    registration: Any,
    user: Any,
    ukraine_country: Any,
    tax_id_document_type: Any,
    digital_wallet_delivery_mechanism: DeliveryMechanism,
    generic_crypto_fi: FinancialInstitution,
    submission_timestamp: datetime.datetime,
    settings: Any,
    tmp_path: Any,
) -> None:
    settings.MEDIA_ROOT = str(tmp_path)
    record = RecordFactory(
        registration=registration.source_id,
        timestamp=submission_timestamp,
        source_id=11,
        fields={
            "consent": [{"consent_h_c": ["1"]}],
            "individual_details": [
                {
                    "given_name_i_c": "Ivan",
                    "family_name_i_c": "Kovalenko",
                    "birth_date": "1970-07-07",
                    "gender_i_c": "male",
                    "wallet_num_image_i_f": "d2FsbGV0X251bV9pbWFnZQ==",
                }
            ],
        },
        files=json.dumps({}).encode(),
    )
    service = UkraineUSDCRegistrationService(registration)
    rdi = service.create_rdi(user, "usdc rdi")

    service.process_records(rdi.id, [record.id])

    individual = PendingIndividual.objects.get(registration_data_import=rdi)
    assert not AccountAttachment.objects.filter(account__individual=individual).exists()
    assert list(tmp_path.iterdir()) == []


def test_head_of_household_phone_number_marked_valid(
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
    assert individual.phone_no_valid is True


def test_head_of_household_phone_number_marked_invalid(
    registration: Any,
    user: Any,
    ukraine_country: Any,
    tax_id_document_type: Any,
    digital_wallet_delivery_mechanism: DeliveryMechanism,
    usdc_record: Record,
) -> None:
    usdc_record.fields["individual_details"][0]["phone_no_i_c"] = "123"
    usdc_record.save(update_fields=["fields"])
    service = UkraineUSDCRegistrationService(registration)
    rdi = service.create_rdi(user, "usdc rdi")

    service.process_records(rdi.id, [usdc_record.id])

    individual = PendingIndividual.objects.get(registration_data_import=rdi)
    assert individual.phone_no_valid is False


def test_no_flex_fields_when_wallet_images_missing(
    registration: Any,
    user: Any,
    ukraine_country: Any,
    tax_id_document_type: Any,
    digital_wallet_delivery_mechanism: DeliveryMechanism,
    usdc_record: Record,
) -> None:
    usdc_record.fields["individual_details"][0].pop("wallet_num_image_i_f")
    usdc_record.fields["individual_details"][0].pop("id_wallet_image_i_f")
    usdc_record.save(update_fields=["fields"])
    service = UkraineUSDCRegistrationService(registration)
    rdi = service.create_rdi(user, "usdc rdi")

    service.process_records(rdi.id, [usdc_record.id])

    individual = PendingIndividual.objects.get(registration_data_import=rdi)
    assert individual.flex_fields == {}


def test_only_present_wallet_image_stored(
    registration: Any,
    user: Any,
    ukraine_country: Any,
    tax_id_document_type: Any,
    digital_wallet_delivery_mechanism: DeliveryMechanism,
    usdc_record: Record,
) -> None:
    usdc_record.fields["individual_details"][0].pop("id_wallet_image_i_f")
    usdc_record.save(update_fields=["fields"])
    service = UkraineUSDCRegistrationService(registration)
    rdi = service.create_rdi(user, "usdc rdi")

    service.process_records(rdi.id, [usdc_record.id])

    individual = PendingIndividual.objects.get(registration_data_import=rdi)
    attachment = AccountAttachment.objects.get(account__individual=individual)
    assert individual.flex_fields == {}
    assert attachment.file.name.endswith(".jpg")
    assert default_storage.exists(attachment.file.name)


def test_rejects_record_with_no_individuals(
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
        source_id=9,
        fields={"consent": [{"consent_h_c": ["1"]}], "individual_details": []},
        files=json.dumps({}).encode(),
    )
    service = UkraineUSDCRegistrationService(registration)
    rdi = service.create_rdi(user, "usdc rdi")

    service.process_records(rdi.id, [record.id])

    record.refresh_from_db()
    assert record.status == Record.STATUS_ERROR
    assert not PendingHousehold.objects.filter(registration_data_import=rdi).exists()


def test_wallet_account_created_when_name_missing(
    registration: Any,
    user: Any,
    ukraine_country: Any,
    tax_id_document_type: Any,
    digital_wallet_delivery_mechanism: DeliveryMechanism,
    usdc_record: Record,
) -> None:
    usdc_record.fields["individual_details"][0].pop("wallet_name_i_c")
    usdc_record.save(update_fields=["fields"])
    service = UkraineUSDCRegistrationService(registration)
    rdi = service.create_rdi(user, "usdc rdi")

    service.process_records(rdi.id, [usdc_record.id])

    individual = PendingIndividual.objects.get(registration_data_import=rdi)
    account = PendingAccount.objects.get(individual=individual)
    assert account.number == "0xABCDEF0123456789"
    assert account.data == {"wallet_address": "0xABCDEF0123456789", "wallet_name": ""}


def test_detail_id_links_household_and_individual_to_source_record(
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
    assert household.detail_id == str(usdc_record.source_id)
    assert individual.detail_id == str(usdc_record.source_id)


def test_reimporting_same_record_does_not_duplicate_household(
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
    service.process_records(rdi.id, [usdc_record.id])

    assert PendingHousehold.objects.filter(registration_data_import=rdi).count() == 1


def test_malformed_wallet_image_rejects_record_without_killing_batch(
    registration: Any,
    user: Any,
    ukraine_country: Any,
    tax_id_document_type: Any,
    digital_wallet_delivery_mechanism: DeliveryMechanism,
    usdc_record: Record,
) -> None:
    usdc_record.fields["individual_details"][0]["wallet_num_image_i_f"] = "abcde"
    usdc_record.save(update_fields=["fields"])
    service = UkraineUSDCRegistrationService(registration)
    rdi = service.create_rdi(user, "usdc rdi")

    service.process_records(rdi.id, [usdc_record.id])

    usdc_record.refresh_from_db()
    assert usdc_record.status == Record.STATUS_ERROR
    assert not PendingHousehold.objects.filter(registration_data_import=rdi).exists()


def test_failed_individual_validation_leaves_no_orphan_images(
    registration: Any,
    user: Any,
    ukraine_country: Any,
    tax_id_document_type: Any,
    digital_wallet_delivery_mechanism: DeliveryMechanism,
    usdc_record: Record,
    settings: Any,
    tmp_path: Any,
) -> None:
    settings.MEDIA_ROOT = str(tmp_path)
    usdc_record.fields["individual_details"][0]["birth_date"] = "1990-99-99"
    usdc_record.save(update_fields=["fields"])
    service = UkraineUSDCRegistrationService(registration)
    rdi = service.create_rdi(user, "usdc rdi")

    service.process_records(rdi.id, [usdc_record.id])

    usdc_record.refresh_from_db()
    assert usdc_record.status == Record.STATUS_ERROR
    assert list(tmp_path.iterdir()) == []
