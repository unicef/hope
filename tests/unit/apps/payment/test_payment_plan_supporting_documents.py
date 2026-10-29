from typing import Any

from django.core.files.uploadedfile import SimpleUploadedFile
from django.http import FileResponse
from django.urls import reverse
import pytest
from rest_framework import serializers, status
from rest_framework.test import APIClient, APIRequestFactory

from extras.test_utils.factories import (
    BusinessAreaFactory,
    PaymentPlanGroupFactory,
    PaymentPlanSupportingDocumentFactory,
    ProgramCycleFactory,
    ProgramFactory,
    UserFactory,
)
from extras.test_utils.factories.payment import FollowUpInstructionFactory
from hope.apps.account.permissions import Permissions
from hope.apps.payment.api.serializers import PaymentPlanSupportingDocumentSerializer
from hope.models import (
    FollowUpInstruction,
    LogEntry,
    PaymentPlanGroup,
    PaymentPlanSupportingDocument,
    Program,
    User,
)

pytestmark = pytest.mark.django_db


@pytest.fixture
def business_area() -> Any:
    return BusinessAreaFactory(slug="afghanistan")


@pytest.fixture
def program(business_area: Any) -> Program:
    return ProgramFactory(business_area=business_area)


@pytest.fixture
def group(program: Program) -> PaymentPlanGroup:
    return PaymentPlanGroupFactory(cycle=ProgramCycleFactory(program=program))


@pytest.fixture
def instruction(program: Program) -> FollowUpInstruction:
    return FollowUpInstructionFactory(program=program)


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
def serializer_context(group: PaymentPlanGroup, user: User) -> dict[str, Any]:
    request = APIRequestFactory().post("")
    request.user = user
    return {"owner": {"payment_plan_group": group}, "request": request}


@pytest.fixture
def upload_user(user: User, business_area: Any, program: Program, create_user_role_with_permissions: Any) -> User:
    create_user_role_with_permissions(user, [Permissions.PM_UPLOAD_SUPPORTING_DOCUMENT], business_area, program=program)
    return user


@pytest.fixture
def delete_download_user(business_area: Any, program: Program, create_user_role_with_permissions: Any) -> User:
    user = UserFactory()
    create_user_role_with_permissions(
        user,
        [Permissions.PM_DELETE_SUPPORTING_DOCUMENT, Permissions.PM_DOWNLOAD_SUPPORTING_DOCUMENT],
        business_area,
        program=program,
    )
    return user


@pytest.fixture
def detail_user(business_area: Any, program: Program, create_user_role_with_permissions: Any) -> User:
    user = UserFactory()
    create_user_role_with_permissions(
        user,
        [Permissions.PM_PAYMENT_PLAN_GROUP_VIEW_DETAIL, Permissions.PM_VIEW_DETAILS],
        business_area,
        program=program,
    )
    return user


@pytest.fixture
def group_document(group: PaymentPlanGroup) -> PaymentPlanSupportingDocument:
    return PaymentPlanSupportingDocumentFactory(payment_plan_group=group, title="Group contract")


@pytest.fixture
def instruction_document(instruction: FollowUpInstruction) -> PaymentPlanSupportingDocument:
    return PaymentPlanSupportingDocumentFactory(follow_up_instruction=instruction, title="Instruction contract")


@pytest.fixture
def group_documents_url(business_area: Any, program: Program, group: PaymentPlanGroup) -> str:
    return reverse(
        "api:payments:payment-plan-group-supporting-documents-list",
        kwargs={
            "business_area_slug": business_area.slug,
            "program_code": program.code,
            "payment_plan_group_pk": str(group.id),
        },
    )


@pytest.fixture
def group_document_url(
    business_area: Any, program: Program, group: PaymentPlanGroup, group_document: PaymentPlanSupportingDocument
) -> str:
    return reverse(
        "api:payments:payment-plan-group-supporting-documents-detail",
        kwargs={
            "business_area_slug": business_area.slug,
            "program_code": program.code,
            "payment_plan_group_pk": str(group.id),
            "file_id": str(group_document.id),
        },
    )


@pytest.fixture
def group_document_download_url(
    business_area: Any, program: Program, group: PaymentPlanGroup, group_document: PaymentPlanSupportingDocument
) -> str:
    return reverse(
        "api:payments:payment-plan-group-supporting-documents-download",
        kwargs={
            "business_area_slug": business_area.slug,
            "program_code": program.code,
            "payment_plan_group_pk": str(group.id),
            "file_id": str(group_document.id),
        },
    )


@pytest.fixture
def instruction_documents_url(business_area: Any, program: Program, instruction: FollowUpInstruction) -> str:
    return reverse(
        "api:payments:follow-up-instruction-supporting-documents-list",
        kwargs={
            "business_area_slug": business_area.slug,
            "program_code": program.code,
            "follow_up_instruction_pk": str(instruction.id),
        },
    )


@pytest.fixture
def instruction_document_url(
    business_area: Any,
    program: Program,
    instruction: FollowUpInstruction,
    instruction_document: PaymentPlanSupportingDocument,
) -> str:
    return reverse(
        "api:payments:follow-up-instruction-supporting-documents-detail",
        kwargs={
            "business_area_slug": business_area.slug,
            "program_code": program.code,
            "follow_up_instruction_pk": str(instruction.id),
            "file_id": str(instruction_document.id),
        },
    )


@pytest.fixture
def instruction_document_download_url(
    business_area: Any,
    program: Program,
    instruction: FollowUpInstruction,
    instruction_document: PaymentPlanSupportingDocument,
) -> str:
    return reverse(
        "api:payments:follow-up-instruction-supporting-documents-download",
        kwargs={
            "business_area_slug": business_area.slug,
            "program_code": program.code,
            "follow_up_instruction_pk": str(instruction.id),
            "file_id": str(instruction_document.id),
        },
    )


@pytest.fixture
def group_detail_url(business_area: Any, program: Program, group: PaymentPlanGroup) -> str:
    return reverse(
        "api:payments:payment-plan-groups-detail",
        kwargs={"business_area_slug": business_area.slug, "program_code": program.code, "pk": str(group.id)},
    )


@pytest.fixture
def instruction_detail_url(business_area: Any, program: Program, instruction: FollowUpInstruction) -> str:
    return reverse(
        "api:payments:follow-up-instructions-detail",
        kwargs={"business_area_slug": business_area.slug, "program_code": program.code, "pk": str(instruction.id)},
    )


@pytest.fixture
def full_group(group: PaymentPlanGroup) -> PaymentPlanGroup:
    PaymentPlanSupportingDocumentFactory.create_batch(
        PaymentPlanSupportingDocument.FILE_LIMIT, payment_plan_group=group
    )
    return group


def test_validate_file_size_success(serializer_context: dict[str, Any], upload_file: SimpleUploadedFile) -> None:
    serializer = PaymentPlanSupportingDocumentSerializer(
        data={"file": upload_file, "title": "test"}, context=serializer_context
    )

    serializer.is_valid()

    assert serializer.errors == {}


def test_validate_file_size_failure(serializer_context: dict[str, Any], upload_file: SimpleUploadedFile) -> None:
    upload_file.size = PaymentPlanSupportingDocument.FILE_SIZE_LIMIT + 1
    serializer = PaymentPlanSupportingDocumentSerializer(
        data={"file": upload_file, "title": "test"}, context=serializer_context
    )

    assert not serializer.is_valid()
    assert serializer.errors["file"][0] == "File size must be ≤ 10MB."


def test_validate_file_missing_size_failure(
    serializer_context: dict[str, Any], upload_file: SimpleUploadedFile
) -> None:
    upload_file.size = None
    serializer = PaymentPlanSupportingDocumentSerializer(data={}, context=serializer_context)

    with pytest.raises(serializers.ValidationError) as exc_info:
        serializer.validate_file(upload_file)

    assert exc_info.value.detail[0] == "File size is not available."


def test_validate_file_extension_success(serializer_context: dict[str, Any]) -> None:
    serializer = PaymentPlanSupportingDocumentSerializer(
        data={"file": SimpleUploadedFile("test.jpg", b"abc", content_type="image/jpeg"), "title": "test"},
        context=serializer_context,
    )

    assert serializer.is_valid()


def test_validate_file_extension_failure(serializer_context: dict[str, Any]) -> None:
    serializer = PaymentPlanSupportingDocumentSerializer(
        data={
            "file": SimpleUploadedFile("test.exe", b"abc", content_type="application/octet-stream"),
            "title": "test",
        },
        context=serializer_context,
    )

    assert not serializer.is_valid()
    assert serializer.errors["file"][0] == "Unsupported file type."


def test_validate_file_limit_failure(full_group: PaymentPlanGroup, serializer_context: dict[str, Any]) -> None:
    serializer = PaymentPlanSupportingDocumentSerializer(
        data={"file": SimpleUploadedFile("test.pdf", b"123", content_type="application/pdf"), "title": "test"},
        context=serializer_context,
    )

    assert not serializer.is_valid()
    assert (
        serializer.errors["non_field_errors"][0]
        == f"Payment plan already has the maximum of {PaymentPlanSupportingDocument.FILE_LIMIT} supporting documents."
    )


@pytest.mark.enable_activity_log
def test_upload_to_group_attaches_document_to_group_and_logs_it(
    api_client: APIClient, group_documents_url: str, upload_user: User, group: PaymentPlanGroup
) -> None:
    api_client.force_authenticate(user=upload_user)

    response = api_client.post(
        group_documents_url,
        {"file": SimpleUploadedFile("test_file.pdf", b"abc", content_type="application/pdf"), "title": "Test"},
        format="multipart",
    )

    assert response.status_code == status.HTTP_201_CREATED
    document = PaymentPlanSupportingDocument.objects.get()
    assert document.payment_plan_group == group
    assert document.follow_up_instruction is None
    assert document.created_by == upload_user
    assert response.data["title"] == "Test"
    assert "test_file" in response.data["file"]
    log = LogEntry.objects.get(object_id=group.id)
    assert log.changes["supporting_document"] == {"from": None, "to": "Test"}


def test_upload_invalid_file_to_group_is_rejected(
    api_client: APIClient, group_documents_url: str, upload_user: User
) -> None:
    api_client.force_authenticate(user=upload_user)

    response = api_client.post(
        group_documents_url,
        {"file": SimpleUploadedFile("test.exe", b"bbb", content_type="application/octet-stream"), "title": "Test"},
        format="multipart",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "file" in response.data


def test_delete_group_document(
    api_client: APIClient,
    group_document_url: str,
    delete_download_user: User,
    group_document: PaymentPlanSupportingDocument,
) -> None:
    api_client.force_authenticate(user=delete_download_user)

    response = api_client.delete(group_document_url)

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not PaymentPlanSupportingDocument.objects.filter(id=group_document.id).exists()


def test_download_group_document(
    api_client: APIClient,
    group_document_download_url: str,
    delete_download_user: User,
    group_document: PaymentPlanSupportingDocument,
) -> None:
    api_client.force_authenticate(user=delete_download_user)

    response = api_client.get(group_document_download_url)

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response, FileResponse)
    assert response["Content-Disposition"] == f'attachment; filename="{group_document.file.name}"'


def test_upload_to_instruction_attaches_document_to_instruction(
    api_client: APIClient, instruction_documents_url: str, upload_user: User, instruction: FollowUpInstruction
) -> None:
    api_client.force_authenticate(user=upload_user)

    response = api_client.post(
        instruction_documents_url,
        {"file": SimpleUploadedFile("test_file.pdf", b"abc", content_type="application/pdf"), "title": "Test"},
        format="multipart",
    )

    assert response.status_code == status.HTTP_201_CREATED
    document = PaymentPlanSupportingDocument.objects.get()
    assert document.follow_up_instruction == instruction
    assert document.payment_plan_group is None


def test_delete_instruction_document(
    api_client: APIClient,
    instruction_document_url: str,
    delete_download_user: User,
    instruction_document: PaymentPlanSupportingDocument,
) -> None:
    api_client.force_authenticate(user=delete_download_user)

    response = api_client.delete(instruction_document_url)

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not PaymentPlanSupportingDocument.objects.filter(id=instruction_document.id).exists()


def test_download_instruction_document(
    api_client: APIClient,
    instruction_document_download_url: str,
    delete_download_user: User,
    instruction_document: PaymentPlanSupportingDocument,
) -> None:
    api_client.force_authenticate(user=delete_download_user)

    response = api_client.get(instruction_document_download_url)

    assert response.status_code == status.HTTP_200_OK
    assert response["Content-Disposition"] == f'attachment; filename="{instruction_document.file.name}"'


def test_group_detail_returns_its_supporting_documents(
    api_client: APIClient,
    group_detail_url: str,
    detail_user: User,
    group_document: PaymentPlanSupportingDocument,
) -> None:
    api_client.force_authenticate(user=detail_user)

    response = api_client.get(group_detail_url)

    assert response.status_code == status.HTTP_200_OK
    assert [document["title"] for document in response.json()["supporting_documents"]] == ["Group contract"]


def test_instruction_detail_returns_its_supporting_documents(
    api_client: APIClient,
    instruction_detail_url: str,
    detail_user: User,
    instruction_document: PaymentPlanSupportingDocument,
) -> None:
    api_client.force_authenticate(user=detail_user)

    response = api_client.get(instruction_detail_url)

    assert response.status_code == status.HTTP_200_OK
    assert [document["title"] for document in response.json()["supporting_documents"]] == ["Instruction contract"]
