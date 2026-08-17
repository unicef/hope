from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
import pytest

from extras.test_utils.factories.household import IndividualFactory
from extras.test_utils.factories.payment import (
    AccountAttachmentFactory,
    AccountFactory,
    AccountTypeFactory,
    DeliveryMechanismFactory,
)
from hope.models import AccountAttachment, AccountType, Individual
from hope.one_time_scripts.migrate_wallet_images_to_account_attachments import (
    migrate_wallet_images_to_account_attachments,
)

pytestmark = [pytest.mark.django_db, pytest.mark.usefixtures("mock_elasticsearch")]


@pytest.fixture
def wallet_account_type() -> AccountType:
    account_type = AccountTypeFactory(key="mobile")
    DeliveryMechanismFactory(code="transfer_to_digital_wallet", account_type=account_type)
    return account_type


@pytest.fixture
def stored_image() -> str:
    return default_storage.save("wallet_number.jpg", ContentFile(b"wallet-number-image"))


def test_flex_image_copied_to_attachment_on_wallet_account(wallet_account_type: AccountType, stored_image: str) -> None:
    individual = IndividualFactory(flex_fields={"wallet_num_image_i_f": stored_image, "other_i_f": "keep"})
    account = AccountFactory(individual=individual, account_type=wallet_account_type)

    migrate_wallet_images_to_account_attachments()

    attachment = AccountAttachment.objects.get(account=account)
    individual.refresh_from_db()
    assert attachment.title == "Wallet number image"
    assert default_storage.exists(attachment.file.name)
    assert attachment.file.read() == b"wallet-number-image"
    assert default_storage.exists(stored_image)
    assert individual.flex_fields == {"other_i_f": "keep"}


def test_flex_field_untouched_when_individual_has_no_wallet_account(
    wallet_account_type: AccountType, stored_image: str
) -> None:
    individual = IndividualFactory(flex_fields={"wallet_num_image_i_f": stored_image})

    migrate_wallet_images_to_account_attachments()

    individual.refresh_from_db()
    assert not AccountAttachment.objects.exists()
    assert individual.flex_fields == {"wallet_num_image_i_f": stored_image}


def test_individual_with_unrelated_account_type_is_skipped(wallet_account_type: AccountType, stored_image: str) -> None:
    individual = IndividualFactory(flex_fields={"wallet_num_image_i_f": stored_image})
    AccountFactory(individual=individual, account_type=AccountTypeFactory(key="bank"))

    migrate_wallet_images_to_account_attachments()

    individual.refresh_from_db()
    assert not AccountAttachment.objects.exists()
    assert individual.flex_fields == {"wallet_num_image_i_f": stored_image}


def test_rerun_does_not_duplicate_attachments(wallet_account_type: AccountType, stored_image: str) -> None:
    individual = IndividualFactory(flex_fields={"wallet_num_image_i_f": stored_image})
    account = AccountFactory(individual=individual, account_type=wallet_account_type)

    migrate_wallet_images_to_account_attachments()
    migrate_wallet_images_to_account_attachments()

    assert AccountAttachment.objects.filter(account=account).count() == 1


def test_missing_source_file_leaves_flex_field_in_place(wallet_account_type: AccountType) -> None:
    individual = IndividualFactory(flex_fields={"wallet_num_image_i_f": "gone.jpg"})
    AccountFactory(individual=individual, account_type=wallet_account_type)

    migrate_wallet_images_to_account_attachments()

    individual.refresh_from_db()
    assert not AccountAttachment.objects.exists()
    assert individual.flex_fields == {"wallet_num_image_i_f": "gone.jpg"}


def test_pending_individual_is_migrated(wallet_account_type: AccountType, stored_image: str) -> None:
    individual = IndividualFactory(
        flex_fields={"wallet_num_image_i_f": stored_image}, rdi_merge_status=Individual.PENDING
    )
    account = AccountFactory(
        individual=individual, account_type=wallet_account_type, rdi_merge_status=Individual.PENDING
    )

    migrate_wallet_images_to_account_attachments()

    individual.refresh_from_db()
    assert AccountAttachment.objects.filter(account=account).exists()
    assert individual.flex_fields == {}


def test_one_failing_record_does_not_stop_the_run(wallet_account_type: AccountType, stored_image: str) -> None:
    failing_individual = IndividualFactory(flex_fields={"wallet_num_image_i_f": stored_image})
    failing_account = AccountFactory(individual=failing_individual, account_type=wallet_account_type)
    AccountAttachmentFactory.create_batch(AccountAttachment.FILE_LIMIT, account=failing_account, title="other")
    healthy_individual = IndividualFactory(flex_fields={"wallet_num_image_i_f": stored_image})
    healthy_account = AccountFactory(individual=healthy_individual, account_type=wallet_account_type)

    migrate_wallet_images_to_account_attachments()

    failing_individual.refresh_from_db()
    healthy_individual.refresh_from_db()
    assert failing_individual.flex_fields == {"wallet_num_image_i_f": stored_image}
    assert healthy_individual.flex_fields == {}
    assert AccountAttachment.objects.get(account=healthy_account).title == "Wallet number image"


def test_failed_attachment_creation_removes_the_copied_file(
    wallet_account_type: AccountType, stored_image: str
) -> None:
    individual = IndividualFactory(flex_fields={"wallet_num_image_i_f": stored_image})
    account = AccountFactory(individual=individual, account_type=wallet_account_type)
    AccountAttachmentFactory.create_batch(AccountAttachment.FILE_LIMIT, account=account, title="other")
    names_before = set(default_storage.listdir("")[1])

    migrate_wallet_images_to_account_attachments()

    individual.refresh_from_db()
    assert individual.flex_fields == {"wallet_num_image_i_f": stored_image}
    assert default_storage.exists(stored_image)
    assert set(default_storage.listdir("")[1]) == names_before
