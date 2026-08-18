from datetime import timedelta

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
import pytest

from extras.test_utils.factories.core import BusinessAreaFactory
from extras.test_utils.factories.household import IndividualFactory
from extras.test_utils.factories.payment import AccountAttachmentFactory, AccountFactory
from hope.models import Account, AccountAttachment, MergeStatusModel

pytestmark = pytest.mark.django_db


@pytest.fixture
def business_area():
    return BusinessAreaFactory(slug="afghanistan")


@pytest.fixture
def account(business_area):
    individual = IndividualFactory(household=None, business_area=business_area)
    return AccountFactory(individual=individual, rdi_merge_status=MergeStatusModel.MERGED)


def test_attachment_is_linked_to_account(account: Account) -> None:
    attachment = AccountAttachmentFactory(account=account, title="Wallet number image")

    assert attachment.account == account
    assert list(account.attachments.all()) == [attachment]


def test_str_returns_title(account: Account) -> None:
    attachment = AccountAttachmentFactory(account=account, title="Wallet number image")

    assert str(attachment) == "Wallet number image"


def test_str_falls_back_to_file_name_when_title_empty(account: Account) -> None:
    attachment = AccountAttachmentFactory(
        account=account,
        title="",
        file=SimpleUploadedFile("wallet.jpg", b"abc", content_type="image/jpeg"),
    )

    assert str(attachment) == attachment.file.name


def test_attachments_are_ordered_by_upload_time(account: Account) -> None:
    older = AccountAttachmentFactory(account=account, title="older")
    AccountAttachmentFactory(account=account, title="newer")
    AccountAttachment.objects.filter(pk=older.pk).update(uploaded_at=timezone.now() - timedelta(days=1))

    assert [attachment.title for attachment in account.attachments.all()] == ["older", "newer"]


def test_attachments_are_deleted_with_the_account(account: Account) -> None:
    AccountAttachmentFactory(account=account)

    account.delete()

    assert not AccountAttachment.objects.exists()


def test_rejects_file_above_size_limit(account: Account) -> None:
    oversized = SimpleUploadedFile("big.jpg", b"a" * (AccountAttachment.FILE_SIZE_LIMIT + 1), content_type="image/jpeg")

    with pytest.raises(ValidationError, match="File size must be ≤ 10MB."):
        AccountAttachmentFactory(account=account, file=oversized)


def test_rejects_replacing_file_with_one_above_size_limit(account: Account) -> None:
    attachment = AccountAttachmentFactory(account=account)

    attachment.file = SimpleUploadedFile(
        "big.jpg", b"a" * (AccountAttachment.FILE_SIZE_LIMIT + 1), content_type="image/jpeg"
    )

    with pytest.raises(ValidationError, match="File size must be ≤ 10MB."):
        attachment.save()


def test_rejects_creation_beyond_file_limit(account: Account) -> None:
    AccountAttachmentFactory.create_batch(AccountAttachment.FILE_LIMIT, account=account)

    with pytest.raises(ValidationError, match="maximum of 10 attachments"):
        AccountAttachmentFactory(account=account)


def test_limit_is_per_account(account: Account, business_area) -> None:
    AccountAttachmentFactory.create_batch(AccountAttachment.FILE_LIMIT, account=account)
    other_individual = IndividualFactory(household=None, business_area=business_area)
    other_account = AccountFactory(individual=other_individual, rdi_merge_status=MergeStatusModel.MERGED)

    attachment = AccountAttachmentFactory(account=other_account)

    assert attachment.pk is not None


def test_existing_attachment_can_be_updated_when_limit_reached(account: Account) -> None:
    attachments = AccountAttachmentFactory.create_batch(AccountAttachment.FILE_LIMIT, account=account)
    attachment = attachments[0]

    attachment.title = "renamed"
    attachment.save()

    attachment.refresh_from_db()
    assert attachment.title == "renamed"
