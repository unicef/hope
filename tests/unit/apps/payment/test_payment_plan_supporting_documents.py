import base64
from io import BytesIO

from django.core.files.uploadedfile import InMemoryUploadedFile, SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.response import Response
from rest_framework.test import APIClient

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.account.models import Role, UserRole
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.payment.api.serializers import (
    PaymentPlanSupportingDocumentSerializer,
)
from hct_mis_api.apps.payment.fixtures import PaymentPlanFactory
from hct_mis_api.apps.payment.models import PaymentPlan, PaymentPlanSupportingDocument


class PaymentPlanSupportingDocumentSerializerTests(TestCase):
    def setUp(cls) -> None:
        create_afghanistan()
        cls.payment_plan = PaymentPlanFactory(
            status=PaymentPlan.Status.OPEN,
        )
        cls.context = {"payment_plan": cls.payment_plan}
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
        user_role, _ = UserRole.objects.get_or_create(user=cls.user, role=role, business_area=cls.business_area)
        cls.payment_plan = PaymentPlanFactory(
            status=PaymentPlan.Status.OPEN,
        )
        program_id_base64 = base64.b64encode(f"ProgramNode:{str(cls.payment_plan.program.id)}".encode()).decode()
        payment_plan_id_base64 = base64.b64encode(f"PaymentPlanNode:{str(cls.payment_plan.id)}".encode()).decode()

        cls.url = reverse(
            "api:payment-plan:supporting_documents-list",
            kwargs={
                "business_area": "afghanistan",
                "program_id": program_id_base64,
                "payment_plan_id": payment_plan_id_base64,
            },
        )
        cls.file = SimpleUploadedFile("test.pdf", b"abc", content_type="application/pdf")

    def test_post_successful_upload(self) -> None:
        self.client.force_authenticate(user=self.user)
        self.assertEqual(PaymentPlanSupportingDocument.objects.count(), 0)
        data = {"file": self.file, "title": "Test Document"}
        response = self.client.post(self.url, data, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("id", response.data)
        self.assertEqual(PaymentPlanSupportingDocument.objects.count(), 1)

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
        user_role, _ = UserRole.objects.get_or_create(user=cls.user, role=role, business_area=cls.business_area)
        cls.payment_plan = PaymentPlanFactory(
            status=PaymentPlan.Status.OPEN,
        )
        cls.document = PaymentPlanSupportingDocument.objects.create(
            payment_plan=cls.payment_plan, title="Test Document333", file=SimpleUploadedFile("test.pdf", b"aaa")
        )
        cls.program_id_base64 = base64.b64encode(f"ProgramNode:{str(cls.payment_plan.program.id)}".encode()).decode()
        cls.payment_plan_id_base64 = base64.b64encode(f"PaymentPlanNode:{str(cls.payment_plan.id)}".encode()).decode()
        cls.supporting_document_id_base64 = base64.b64encode(
            f"PaymentPlanSupportingDocumentNode:{str(cls.document.id)}".encode()
        ).decode()

        cls.url = reverse(
            "api:payment-plan:supporting_documents-detail",
            kwargs={
                "business_area": "afghanistan",
                "program_id": cls.program_id_base64,
                "payment_plan_id": cls.payment_plan_id_base64,
                "file_id": cls.supporting_document_id_base64,
            },
        )

    def test_delete_document_success(self) -> None:
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_get_document_success(self) -> None:
        url = reverse(
            "api:payment-plan:supporting_documents-download",
            kwargs={
                "business_area": "afghanistan",
                "program_id": self.program_id_base64,
                "payment_plan_id": self.payment_plan_id_base64,
                "file_id": self.supporting_document_id_base64,
            },
        )

        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response, Response)
