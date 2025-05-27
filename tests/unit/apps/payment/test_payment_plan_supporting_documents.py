from io import BytesIO

from django.core.files.storage import default_storage
from django.core.files.uploadedfile import (InMemoryUploadedFile,
                                            SimpleUploadedFile)
from django.http import FileResponse
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APIRequestFactory

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.account.models import Role, RoleAssignment
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.payment.api.serializers import \
    PaymentPlanSupportingDocumentSerializer
from hct_mis_api.apps.payment.fixtures import PaymentPlanFactory
from hct_mis_api.apps.payment.models import (PaymentPlan,
                                             PaymentPlanSupportingDocument)


class PaymentPlanSupportingDocumentSerializerTests(TestCase):
    def setUp(cls) -> None:
        create_afghanistan()
        cls.payment_plan = PaymentPlanFactory(
            status=PaymentPlan.Status.OPEN,
        )
        factory = APIRequestFactory()
        cls.request = factory.post("/just_any_url/")
        cls.request.user = cls.client  # type: ignore
        cls.request.parser_context = {
            "kwargs": {
                "payment_plan_id": str(cls.payment_plan.id),
            }
        }
        cls.context = {"payment_plan": cls.payment_plan, "request": cls.request}
        cls.file = SimpleUploadedFile("test.pdf", b"123", content_type="application/pdf")

    def test_validate_file_size_success(self) -> None:
        document_data = {"file": self.file, "title": "test"}
        serializer = PaymentPlanSupportingDocumentSerializer(data=document_data, context=self.context)
        serializer.is_valid()
        self.assertEqual(serializer.errors, {})

    def test_validate_file_size_failure(self) -> None:
        # just mock file size over limit
        self.file.size = PaymentPlanSupportingDocument.FILE_SIZE_LIMIT + 1
        document_data = {"file": self.file, "title": "test"}
        serializer = PaymentPlanSupportingDocumentSerializer(data=document_data, context=self.context)
        self.assertFalse(serializer.is_valid())
        self.assertIn("file", serializer.errors)
        self.assertEqual(serializer.errors["file"][0], "File size must be ≤ 10MB.")

    def test_validate_file_extension_success(self) -> None:
        valid_file = SimpleUploadedFile("test.jpg", b"abc", content_type="image/jpeg")
        document_data = {"file": valid_file, "title": "test"}
        serializer = PaymentPlanSupportingDocumentSerializer(data=document_data, context=self.context)
        self.assertTrue(serializer.is_valid())

    def test_validate_file_extension_failure(self) -> None:
        invalid_file = SimpleUploadedFile("test.exe", b"abc", content_type="application/octet-stream")
        document_data = {"file": invalid_file, "title": "test"}
        serializer = PaymentPlanSupportingDocumentSerializer(data=document_data, context=self.context)
        self.assertFalse(serializer.is_valid())
        self.assertIn("file", serializer.errors)
        self.assertEqual(serializer.errors["file"][0], "Unsupported file type.")

    def test_validate_payment_plan_status_failure(self) -> None:
        self.payment_plan.status = PaymentPlan.Status.FINISHED
        self.payment_plan.save(update_fields=["status"])
        serializer = PaymentPlanSupportingDocumentSerializer(
            data={"file": self.file, "title": "test"}, context=self.context
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("non_field_errors", serializer.errors)
        self.assertEqual(serializer.errors["non_field_errors"][0], "Payment plan must be within status OPEN or LOCKED.")

    def test_validate_file_limit_failure(self) -> None:
        # create 10 documents
        for _ in range(11):
            PaymentPlanSupportingDocument.objects.create(
                payment_plan=self.payment_plan,
                title="Test 1",
                file=InMemoryUploadedFile(
                    name="Test123.jpg",
                    file=BytesIO(b"abc"),
                    charset=None,
                    field_name="0",
                    size=10,
                    content_type="image/jpeg",
                ),
            )

        serializer = PaymentPlanSupportingDocumentSerializer(
            data={"file": self.file, "title": "test"}, context=self.context
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("non_field_errors", serializer.errors)
        self.assertEqual(
            serializer.errors["non_field_errors"][0],
            f"Payment plan already has the maximum of {PaymentPlanSupportingDocument.FILE_LIMIT} supporting documents.",
        )


class PaymentPlanSupportingDocumentUploadViewTests(TestCase):
    def setUp(cls) -> None:
        cls.business_area = create_afghanistan()
        cls.client = APIClient()
        cls.user = UserFactory(username="Hope_USER", password="GoodJod")
        role, created = Role.objects.update_or_create(
            name="TestName", defaults={"permissions": [Permissions.PM_UPLOAD_SUPPORTING_DOCUMENT.value]}
        )
        user_role, _ = RoleAssignment.objects.get_or_create(user=cls.user, role=role, business_area=cls.business_area)
        cls.payment_plan = PaymentPlanFactory(
            status=PaymentPlan.Status.OPEN,
        )

        cls.url = reverse(
            "api:payments:supporting-documents-list",
            kwargs={
                "business_area_slug": "afghanistan",
                "program_slug": cls.payment_plan.program.slug,
                "payment_plan_id": str(cls.payment_plan.id),
            },
        )
        cls.file = SimpleUploadedFile("test_file.pdf", b"abc", content_type="application/pdf")

    def tearDown(self) -> None:
        for document in PaymentPlanSupportingDocument.objects.all():
            if default_storage.exists(document.file.name):
                default_storage.delete(document.file.name)
        PaymentPlanSupportingDocument.objects.all().delete()

    def test_post_successful_upload(self) -> None:
        self.client.force_authenticate(user=self.user)
        self.assertEqual(PaymentPlanSupportingDocument.objects.count(), 0)
        data = {"file": self.file, "title": "Test Document"}
        response = self.client.post(self.url, data, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(PaymentPlanSupportingDocument.objects.count(), 1)
        self.assertIn("id", response.data)
        self.assertIn("uploaded_at", response.data)
        self.assertEqual(response.data["file"], "test_file.pdf")
        self.assertEqual(response.data["title"], "Test Document")
        self.assertEqual(response.data["created_by"], self.user.pk)

    def test_post_invalid_upload(self) -> None:
        self.client.force_authenticate(user=self.user)
        invalid_file = SimpleUploadedFile("test.exe", b"bbb", content_type="application/octet-stream")
        data = {"file": invalid_file, "title": "Test Document"}
        response = self.client.post(self.url, data, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("file", response.data)


class PaymentPlanSupportingDocumentViewTests(TestCase):
    def setUp(cls) -> None:
        cls.business_area = create_afghanistan()
        cls.client = APIClient()
        cls.user = UserFactory(username="Hope_USER", password="GoodJod")
        role, created = Role.objects.update_or_create(
            name="TestName",
            defaults={
                "permissions": [
                    Permissions.PM_DELETE_SUPPORTING_DOCUMENT.value,
                    Permissions.PM_DOWNLOAD_SUPPORTING_DOCUMENT.value,
                ]
            },
        )
        user_role, _ = RoleAssignment.objects.get_or_create(user=cls.user, role=role, business_area=cls.business_area)
        cls.payment_plan = PaymentPlanFactory(
            status=PaymentPlan.Status.OPEN,
        )
        cls.document = PaymentPlanSupportingDocument.objects.create(
            payment_plan=cls.payment_plan, title="Test Document333", file=SimpleUploadedFile("test.pdf", b"aaa")
        )

        cls.url = reverse(
            "api:payments:supporting-documents-detail",
            kwargs={
                "business_area_slug": "afghanistan",
                "program_slug": cls.payment_plan.program.slug,
                "payment_plan_id": str(cls.payment_plan.id),
                "file_id": str(cls.document.id),
            },
        )

    def test_delete_document_success(self) -> None:
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_get_document_success(self) -> None:
        url = reverse(
            "api:payments:supporting-documents-download",
            kwargs={
                "business_area_slug": "afghanistan",
                "program_slug": self.payment_plan.program.slug,
                "payment_plan_id": self.payment_plan.pk,
                "file_id": self.document.id,
            },
        )

        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response, FileResponse)
        self.assertEqual(response["Content-Disposition"], f"attachment; filename={self.document.file.name}")
