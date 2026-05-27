import base64

from django.core.files.uploadedfile import SimpleUploadedFile
import pytest

from extras.test_utils.factories import (
    CountryFactory,
    DocumentTypeFactory,
    PendingIndividualFactory,
)
from hope.api.endpoints.rdi.mixin import AccountMixin, DocumentMixin, PhotoMixin, get_photo_from_stream
from hope.models import AccountType, PendingAccount, PendingDocument, PendingIndividual

pytestmark = pytest.mark.django_db


@pytest.fixture
def pending_individual() -> PendingIndividual:
    return PendingIndividualFactory()


@pytest.fixture
def document_payload() -> dict:
    country = CountryFactory(iso_code2="AF")
    DocumentTypeFactory(key="birth_certificate")
    photo = SimpleUploadedFile("doc.png", b"file-bytes", content_type="image/png")
    return {
        "document_number": "DOC-1",
        "photo": photo,
        "country": country.iso_code2,
        "type": "birth_certificate",
    }


@pytest.fixture
def account_payload() -> dict:
    account_type, _ = AccountType.objects.get_or_create(key="bank", defaults={"label": "Bank"})
    return {"account_type": account_type, "number": "12345", "data": {"foo": "bar"}}


def test_get_photo_from_stream_returns_unique_file() -> None:
    data = base64.b64encode(b"abc123").decode("utf-8")

    result1 = get_photo_from_stream(data, "first_")
    result2 = get_photo_from_stream(data, "second_")

    assert result1 is not None
    assert result2 is not None
    assert result1.name.startswith("first_")
    assert result2.name.startswith("second_")
    assert result1.name.endswith(".png")
    assert result2.name.endswith(".png")
    assert result1.name != result2.name
    assert result1.read() == b"abc123"
    assert result1.content_type == "image/png"


def test_get_photo_handles_data_url_prefix() -> None:
    data = base64.b64encode(b"xyz").decode("utf-8")
    prefixed = f"data:image/png;base64,{data}"

    result = PhotoMixin.get_photo(prefixed, file_name_prefix="pref_")

    assert result is not None
    assert result.name.startswith("pref_")
    assert result.read() == b"xyz"


def test_get_photo_returns_none_when_no_input() -> None:
    assert PhotoMixin.get_photo(None) is None


def test_save_document_creates_pending_document(pending_individual: PendingIndividual, document_payload: dict) -> None:
    DocumentMixin.save_document(pending_individual, document_payload)

    saved = PendingDocument.objects.get(individual=pending_individual)
    assert saved.document_number == "DOC-1"
    assert saved.country.iso_code2 == "AF"
    assert saved.type.key == "birth_certificate"
    assert saved.program == pending_individual.program
    assert saved.photo
    assert saved.photo.name.endswith(".png")


def test_save_account_creates_pending_account(pending_individual: PendingIndividual, account_payload: dict) -> None:
    AccountMixin.save_account(pending_individual, account_payload)

    saved = PendingAccount.objects.get(individual=pending_individual)
    assert saved.account_type.key == "bank"
    assert saved.number == "12345"
    assert saved.data == {"foo": "bar"}
