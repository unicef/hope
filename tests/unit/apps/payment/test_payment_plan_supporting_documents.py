from typing import Any

from django.core.files.uploadedfile import SimpleUploadedFile
from django.http import FileResponse
from django.urls import reverse
import pytest
from rest_framework import status
from rest_framework.test import APIClient, APIRequestFactory

from extras.test_utils.factories import (
    BusinessAreaFactory,
    PaymentPlanFactory,
    PaymentPlanSupportingDocumentFactory,
    UserFactory,
)
from hope.apps.account.permissions import Permissions
from hope.apps.payment.api.serializers import PaymentPlanSupportingDocumentSerializer
from hope.models import PaymentPlan, PaymentPlanSupportingDocument, User

pytestmark = pytest.mark.django_db


@pytest.fixture
def business_area() -> Any:
    return BusinessAreaFactory(slug="afghanistan")


@pytest.fixture
def payment_plan(business_area: Any) -> PaymentPlan:
    return PaymentPlanFactory(
        status=PaymentPlan.Status.OPEN,
        business_area=business_area,
    )


@pytest.fixture
def user() -> User:
    return UserFactory()


@pytest.fixture
def api_client() -> APIClient:
    return APIClient()


@pytest.fixture
def upload_file() -> SimpleUploadedFile:
    return SimpleUploadedFile("test.pdf", b"123", content_type="application/pdf")


@pytest.fixture
def serializer_context(payment_plan: PaymentPlan, user: User) -> dict[str, Any]:
    factory = APIRequestFactory()
    request = factory.post("")
    request.user = user
    request.parser_context = {"kwargs": {"payment_plan_pk": str(payment_plan.id)}}
    return {"payment_plan": payment_plan, "request": request}


@pytest.fixture
def upload_user(
    user: User,
    business_area: Any,
    payment_plan: PaymentPlan,
    create_user_role_with_permissions: Any,
) -> User:
    create_user_role_with_permissions(
        user,
        [Permissions.PM_UPLOAD_SUPPORTING_DOCUMENT],
        business_area,
        program=payment_plan.program,
    )
    return user


@pytest.fixture
def delete_download_user(
    business_area: Any,
    payment_plan: PaymentPlan,
    create_user_role_with_permissions: Any,
) -> User:
    user = UserFactory()
    create_user_role_with_permissions(
        user,
        [
            Permissions.PM_DELETE_SUPPORTING_DOCUMENT,
            Permissions.PM_DOWNLOAD_SUPPORTING_DOCUMENT,
        ],
        business_area,
        program=payment_plan.program,
    )
    return user


@pytest.fixture
def supporting_documents_list_url(business_area: Any, payment_plan: PaymentPlan) -> str:
    return reverse(
        "api:payments:supporting-documents-list",
        kwargs={
            "business_area_slug": business_area.slug,
            "program_slug": payment_plan.program.slug,
            "payment_plan_pk": str(payment_plan.id),
        },
    )


@pytest.fixture
def supporting_documents_detail_url(business_area: Any, payment_plan: PaymentPlan, document: Any) -> str:
    return reverse(
        "api:payments:supporting-documents-detail",
        kwargs={
            "business_area_slug": business_area.slug,
            "program_slug": payment_plan.program.slug,
            "payment_plan_pk": str(payment_plan.id),
            "file_id": str(document.id),
        },
    )


@pytest.fixture
def supporting_documents_download_url(business_area: Any, payment_plan: PaymentPlan, document: Any) -> str:
    return reverse(
        "api:payments:supporting-documents-download",
        kwargs={
            "business_area_slug": business_area.slug,
            "program_slug": payment_plan.program.slug,
            "payment_plan_pk": payment_plan.pk,
            "file_id": document.id,
        },
    )


@pytest.fixture
def document(payment_plan: PaymentPlan) -> PaymentPlanSupportingDocument:
    return PaymentPlanSupportingDocumentFactory(
        payment_plan=payment_plan,
    )


def test_validate_file_size_success(serializer_context: dict[str, Any], upload_file: SimpleUploadedFile) -> None:
    document_data = {"file": upload_file, "title": "test"}
    serializer = PaymentPlanSupportingDocumentSerializer(data=document_data, context=serializer_context)
    serializer.is_valid()
    assert serializer.errors == {}


def test_validate_file_size_failure(serializer_context: dict[str, Any], upload_file: SimpleUploadedFile) -> None:
    upload_file.size = PaymentPlanSupportingDocument.FILE_SIZE_LIMIT + 1
    document_data = {"file": upload_file, "title": "test"}
    serializer = PaymentPlanSupportingDocumentSerializer(data=document_data, context=serializer_context)
    assert not serializer.is_valid()
    assert "file" in serializer.errors
    assert serializer.errors["file"][0] == "File size must be ≤ 10MB."


def test_validate_file_extension_success(serializer_context: dict[str, Any]) -> None:
    valid_file = SimpleUploadedFile("test.jpg", b"abc", content_type="image/jpeg")
    document_data = {"file": valid_file, "title": "test"}
    serializer = PaymentPlanSupportingDocumentSerializer(data=document_data, context=serializer_context)
    assert serializer.is_valid()


def test_validate_file_extension_failure(serializer_context: dict[str, Any]) -> None:
    invalid_file = SimpleUploadedFile("test.exe", b"abc", content_type="application/octet-stream")
    document_data = {"file": invalid_file, "title": "test"}
    serializer = PaymentPlanSupportingDocumentSerializer(data=document_data, context=serializer_context)
    assert not serializer.is_valid()
    assert "file" in serializer.errors
    assert serializer.errors["file"][0] == "Unsupported file type."


def test_validate_file_limit_failure(payment_plan: PaymentPlan, serializer_context: dict[str, Any]) -> None:
    PaymentPlanSupportingDocumentFactory.create_batch(
        PaymentPlanSupportingDocument.FILE_LIMIT + 1,
        payment_plan=payment_plan,
    )
    serializer = PaymentPlanSupportingDocumentSerializer(
        data={"file": SimpleUploadedFile("test.pdf", b"123", content_type="application/pdf"), "title": "test"},
        context=serializer_context,
    )
    assert not serializer.is_valid()
    assert "non_field_errors" in serializer.errors
    assert (
        serializer.errors["non_field_errors"][0]
        == f"Payment plan already has the maximum of {PaymentPlanSupportingDocument.FILE_LIMIT} supporting documents."
    )


def test_post_successful_upload(
    api_client: APIClient,
    supporting_documents_list_url: str,
    upload_user: User,
) -> None:
    api_client.force_authenticate(user=upload_user)
    assert PaymentPlanSupportingDocument.objects.count() == 0
    data = {"file": SimpleUploadedFile("test_file.pdf", b"abc", content_type="application/pdf"), "title": "Test"}
    response = api_client.post(supporting_documents_list_url, data, format="multipart")

    assert response.status_code == status.HTTP_201_CREATED
    assert PaymentPlanSupportingDocument.objects.count() == 1
    assert "id" in response.data
    assert "uploaded_at" in response.data
    assert "test_file" in response.data["file"]
    assert response.data["title"] == "Test"
    assert response.data["created_by"] == upload_user.pk


def test_post_invalid_upload(
    api_client: APIClient,
    supporting_documents_list_url: str,
    upload_user: User,
) -> None:
    api_client.force_authenticate(user=upload_user)
    invalid_file = SimpleUploadedFile("test.exe", b"bbb", content_type="application/octet-stream")
    data = {"file": invalid_file, "title": "Test Document"}
    response = api_client.post(supporting_documents_list_url, data, format="multipart")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "file" in response.data


def test_delete_document_success(
    api_client: APIClient,
    supporting_documents_detail_url: str,
    delete_download_user: User,
) -> None:
    api_client.force_authenticate(user=delete_download_user)
    response = api_client.delete(supporting_documents_detail_url)
    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_get_document_success(
    api_client: APIClient,
    supporting_documents_download_url: str,
    delete_download_user: User,
    document: PaymentPlanSupportingDocument,
) -> None:
    api_client.force_authenticate(user=delete_download_user)
    response = api_client.get(supporting_documents_download_url)

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response, FileResponse)
    assert response["Content-Disposition"] == f"attachment; filename={document.file.name}"
