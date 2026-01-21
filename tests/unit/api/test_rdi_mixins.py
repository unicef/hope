import base64

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from extras.test_utils.old_factories.account import BusinessAreaFactory
from extras.test_utils.old_factories.geo import CountryFactory
from extras.test_utils.old_factories.household import DocumentTypeFactory, PendingIndividualFactory
from extras.test_utils.old_factories.program import ProgramFactory
from extras.test_utils.old_factories.registration_data import RegistrationDataImportFactory
from hope.api.endpoints.rdi.mixin import AccountMixin, DocumentMixin, PhotoMixin, get_photo_from_stream
from hope.models import AccountType, PendingAccount, PendingDocument


class PhotoMixinTests(TestCase):
    databases = {"default"}

    def test_get_photo_from_stream_returns_unique_file(self) -> None:
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

    def test_get_photo_handles_data_url_prefix(self) -> None:
        data = base64.b64encode(b"xyz").decode("utf-8")
        prefixed = f"data:image/png;base64,{data}"

        result = PhotoMixin.get_photo(prefixed, file_name_prefix="pref_")

        assert result is not None
        assert result.name.startswith("pref_")
        assert result.read() == b"xyz"

    def test_get_photo_returns_none_when_no_input(self) -> None:
        assert PhotoMixin.get_photo(None) is None


class DocumentMixinTests(TestCase):
    databases = {"default"}

    def setUp(self) -> None:
        super().setUp()
        self.business_area = BusinessAreaFactory()
        self.program = ProgramFactory(business_area=self.business_area)
        self.rdi = RegistrationDataImportFactory(business_area=self.business_area, program=self.program)

    def test_save_document_creates_pending_document(self) -> None:
        member = PendingIndividualFactory(
            registration_data_import=self.rdi, program=self.program, business_area=self.business_area
        )
        country = CountryFactory(iso_code2="AF")
        doc_type = DocumentTypeFactory(key="birth_certificate")
        photo = SimpleUploadedFile("doc.png", b"file-bytes", content_type="image/png")
        doc_payload = {
            "document_number": "DOC-1",
            "photo": photo,
            "country": country.iso_code2,
            "type": doc_type.key,
        }

        DocumentMixin.save_document(member, doc_payload)

        saved = PendingDocument.objects.get(individual=member)
        assert saved.document_number == "DOC-1"
        assert saved.country == country
        assert saved.type == doc_type
        assert saved.program == member.program
        assert saved.photo
        assert saved.photo.name.endswith(".png")


class AccountMixinTests(TestCase):
    databases = {"default"}

    def setUp(self) -> None:
        super().setUp()
        self.business_area = BusinessAreaFactory()
        self.program = ProgramFactory(business_area=self.business_area)
        self.rdi = RegistrationDataImportFactory(business_area=self.business_area, program=self.program)
        self.account_type, _ = AccountType.objects.get_or_create(
            key="bank", defaults={"label": "Bank", "unique_fields": ["number"]}
        )

    def test_save_account_creates_pending_account(self) -> None:
        member = PendingIndividualFactory(
            registration_data_import=self.rdi, program=self.program, business_area=self.business_area
        )
        account_payload = {"account_type": self.account_type, "number": "12345", "data": {"foo": "bar"}}

        AccountMixin.save_account(member, account_payload)

        saved = PendingAccount.objects.get(individual=member)
        assert saved.account_type == self.account_type
        assert saved.number == "12345"
        assert saved.data == {"foo": "bar"}
