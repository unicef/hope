from typing import Any

from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.http import FileResponse
from django.urls import reverse
import pytest
from rest_framework import status
from rest_framework.test import APIClient, APIRequestFactory

from extras.test_utils.factories import (
    AccountAttachmentFactory,
    AccountFactory,
    BusinessAreaFactory,
    IndividualFactory,
    ProgramFactory,
    UserFactory,
)
from hope.apps.account.permissions import Permissions
from hope.apps.payment.api.serializers import AccountAttachmentUploadSerializer
from hope.models import Account, AccountAttachment, MergeStatusModel, Program, User

pytestmark = pytest.mark.django_db


@pytest.fixture
def business_area() -> Any:
    return BusinessAreaFactory(slug="afghanistan")


@pytest.fixture
def program(business_area: Any) -> Program:
    return ProgramFactory(business_area=business_area)


@pytest.fixture
def account(business_area: Any, program: Program) -> Account:
    individual = IndividualFactory(household=None, business_area=business_area, program=program)
    return AccountFactory(individual=individual, rdi_merge_status=MergeStatusModel.MERGED)


@pytest.fixture
def api_client() -> APIClient:
    return APIClient()


@pytest.fixture
def serializer_context(account: Account, program: Program) -> dict[str, Any]:
    factory = APIRequestFactory()
    request = factory.post("")
    request.user = UserFactory()
    request.parser_context = {"kwargs": {"account_pk": str(account.id), "individual_pk": str(account.individual_id)}}
    return {"request": request, "program": program}


@pytest.fixture
def attachment_user(business_area: Any, program: Program, create_user_role_with_permissions: Any) -> User:
    user = UserFactory()
    create_user_role_with_permissions(
        user,
        [Permissions.POPULATION_VIEW_INDIVIDUAL_DELIVERY_MECHANISMS_SECTION],
        business_area,
        program=program,
    )
    return user


@pytest.fixture
def user_without_permission(business_area: Any, program: Program, create_user_role_with_permissions: Any) -> User:
    user = UserFactory()
    create_user_role_with_permissions(
        user,
        [Permissions.POPULATION_VIEW_INDIVIDUALS_DETAILS],
        business_area,
        program=program,
    )
    return user


@pytest.fixture
def attachment(account: Account) -> AccountAttachment:
    return AccountAttachmentFactory(account=account)


@pytest.fixture
def other_program_account(business_area: Any) -> Account:
    other_program = ProgramFactory(business_area=business_area)
    individual = IndividualFactory(household=None, business_area=business_area, program=other_program)
    return AccountFactory(individual=individual, rdi_merge_status=MergeStatusModel.MERGED)


@pytest.fixture
def accounts_list_url(business_area: Any, program: Program, account: Account) -> str:
    return reverse(
        "api:households:accounts-list",
        kwargs={
            "business_area_slug": business_area.slug,
            "program_code": program.code,
            "individual_pk": str(account.individual_id),
        },
    )


@pytest.fixture
def other_individual_account(business_area: Any, program: Program) -> Account:
    individual = IndividualFactory(household=None, business_area=business_area, program=program)
    return AccountFactory(individual=individual, rdi_merge_status=MergeStatusModel.MERGED)


@pytest.fixture
def second_account(account: Account) -> Account:
    return AccountFactory(individual=account.individual, rdi_merge_status=MergeStatusModel.MERGED)


@pytest.fixture
def second_account_attachment(second_account: Account) -> AccountAttachment:
    return AccountAttachmentFactory(account=second_account)


@pytest.fixture
def attachments_list_url(business_area: Any, program: Program, account: Account) -> str:
    return reverse(
        "api:households:account-attachments-list",
        kwargs={
            "business_area_slug": business_area.slug,
            "program_code": program.code,
            "individual_pk": str(account.individual_id),
            "account_pk": str(account.id),
        },
    )


@pytest.fixture
def attachments_detail_url(
    business_area: Any, program: Program, account: Account, attachment: AccountAttachment
) -> str:
    return reverse(
        "api:households:account-attachments-detail",
        kwargs={
            "business_area_slug": business_area.slug,
            "program_code": program.code,
            "individual_pk": str(account.individual_id),
            "account_pk": str(account.id),
            "file_id": str(attachment.id),
        },
    )


@pytest.fixture
def attachments_download_url(
    business_area: Any, program: Program, account: Account, attachment: AccountAttachment
) -> str:
    return reverse(
        "api:households:account-attachments-download",
        kwargs={
            "business_area_slug": business_area.slug,
            "program_code": program.code,
            "individual_pk": str(account.individual_id),
            "account_pk": str(account.id),
            "file_id": str(attachment.id),
        },
    )


def test_validate_file_size_failure(serializer_context: dict[str, Any]) -> None:
    upload_file = SimpleUploadedFile("test.jpg", b"abc", content_type="image/jpeg")
    upload_file.size = AccountAttachment.FILE_SIZE_LIMIT + 1
    serializer = AccountAttachmentUploadSerializer(
        data={"file": upload_file, "title": "test"}, context=serializer_context
    )

    assert not serializer.is_valid()
    assert serializer.errors["file"][0] == "File size must be ≤ 10MB."


def test_validate_file_extension_failure(serializer_context: dict[str, Any]) -> None:
    invalid_file = SimpleUploadedFile("test.exe", b"abc", content_type="application/octet-stream")
    serializer = AccountAttachmentUploadSerializer(
        data={"file": invalid_file, "title": "test"}, context=serializer_context
    )

    assert not serializer.is_valid()
    assert serializer.errors["file"][0] == "Unsupported file type."


def test_validate_file_limit_failure(account: Account, serializer_context: dict[str, Any]) -> None:
    AccountAttachmentFactory.create_batch(AccountAttachment.FILE_LIMIT, account=account)
    serializer = AccountAttachmentUploadSerializer(
        data={"file": SimpleUploadedFile("test.jpg", b"abc", content_type="image/jpeg"), "title": "test"},
        context=serializer_context,
    )

    assert not serializer.is_valid()
    assert (
        serializer.errors["non_field_errors"][0]
        == f"Account already has the maximum of {AccountAttachment.FILE_LIMIT} attachments."
    )


def test_post_uploads_attachment(
    api_client: APIClient, attachments_list_url: str, attachment_user: User, account: Account
) -> None:
    api_client.force_authenticate(user=attachment_user)
    data = {"file": SimpleUploadedFile("wallet.jpg", b"abc", content_type="image/jpeg"), "title": "Wallet"}

    response = api_client.post(attachments_list_url, data, format="multipart")

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["title"] == "Wallet"
    assert response.data["created_by"] == attachment_user.pk
    assert "wallet" in response.data["file"]
    assert account.attachments.count() == 1


def test_post_without_title_stores_empty_title(
    api_client: APIClient, attachments_list_url: str, attachment_user: User, account: Account
) -> None:
    api_client.force_authenticate(user=attachment_user)
    data = {"file": SimpleUploadedFile("wallet.jpg", b"abc", content_type="image/jpeg")}

    response = api_client.post(attachments_list_url, data, format="multipart")

    assert response.status_code == status.HTTP_201_CREATED
    assert account.attachments.get().title == ""


def test_post_rejects_unsupported_file_type(
    api_client: APIClient, attachments_list_url: str, attachment_user: User
) -> None:
    api_client.force_authenticate(user=attachment_user)
    data = {"file": SimpleUploadedFile("wallet.exe", b"abc", content_type="application/octet-stream")}

    response = api_client.post(attachments_list_url, data, format="multipart")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "file" in response.data


def test_post_denied_without_permission(
    api_client: APIClient, attachments_list_url: str, user_without_permission: User
) -> None:
    api_client.force_authenticate(user=user_without_permission)
    data = {"file": SimpleUploadedFile("wallet.jpg", b"abc", content_type="image/jpeg")}

    response = api_client.post(attachments_list_url, data, format="multipart")

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_delete_removes_attachment(api_client: APIClient, attachments_detail_url: str, attachment_user: User) -> None:
    api_client.force_authenticate(user=attachment_user)

    response = api_client.delete(attachments_detail_url)

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not AccountAttachment.objects.exists()


def test_delete_denied_without_permission(
    api_client: APIClient, attachments_detail_url: str, user_without_permission: User
) -> None:
    api_client.force_authenticate(user=user_without_permission)

    response = api_client.delete(attachments_detail_url)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert AccountAttachment.objects.exists()


def test_download_returns_file(
    api_client: APIClient, attachments_download_url: str, attachment_user: User, attachment: AccountAttachment
) -> None:
    api_client.force_authenticate(user=attachment_user)

    response = api_client.get(attachments_download_url)

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response, FileResponse)
    assert response["Content-Disposition"] == f"attachment; filename={attachment.file.name}"


def test_download_denied_without_permission(
    api_client: APIClient, attachments_download_url: str, user_without_permission: User
) -> None:
    api_client.force_authenticate(user=user_without_permission)

    response = api_client.get(attachments_download_url)

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_post_rejects_account_from_another_program(
    api_client: APIClient,
    business_area: Any,
    program: Program,
    other_program_account: Account,
    attachment_user: User,
) -> None:
    api_client.force_authenticate(user=attachment_user)
    url = reverse(
        "api:households:account-attachments-list",
        kwargs={
            "business_area_slug": business_area.slug,
            "program_code": program.code,
            "individual_pk": str(other_program_account.individual_id),
            "account_pk": str(other_program_account.id),
        },
    )

    response = api_client.post(
        url,
        {"file": SimpleUploadedFile("wallet.jpg", b"abc", content_type="image/jpeg")},
        format="multipart",
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert not AccountAttachment.objects.exists()


def test_delete_rejects_attachment_from_another_program(
    api_client: APIClient,
    business_area: Any,
    program: Program,
    other_program_account: Account,
    attachment_user: User,
) -> None:
    other_attachment = AccountAttachmentFactory(account=other_program_account)
    api_client.force_authenticate(user=attachment_user)
    url = reverse(
        "api:households:account-attachments-detail",
        kwargs={
            "business_area_slug": business_area.slug,
            "program_code": program.code,
            "individual_pk": str(other_program_account.individual_id),
            "account_pk": str(other_program_account.id),
            "file_id": str(other_attachment.id),
        },
    )

    response = api_client.delete(url)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert AccountAttachment.objects.filter(pk=other_attachment.pk).exists()


def test_accounts_list_returns_only_the_individuals_accounts(
    api_client: APIClient,
    accounts_list_url: str,
    attachment_user: User,
    account: Account,
    attachment: AccountAttachment,
    other_program_account: Account,
) -> None:
    api_client.force_authenticate(user=attachment_user)

    response = api_client.get(accounts_list_url)

    assert response.status_code == status.HTTP_200_OK
    assert [item["id"] for item in response.data["results"]] == [str(account.id)]
    assert response.data["results"][0]["attachments"][0]["id"] == attachment.id


def test_accounts_list_denied_without_permission(
    api_client: APIClient, accounts_list_url: str, user_without_permission: User
) -> None:
    api_client.force_authenticate(user=user_without_permission)

    response = api_client.get(accounts_list_url)

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_accounts_list_excludes_accounts_of_another_individual_in_the_same_program(
    api_client: APIClient,
    accounts_list_url: str,
    attachment_user: User,
    account: Account,
    other_individual_account: Account,
) -> None:
    api_client.force_authenticate(user=attachment_user)

    response = api_client.get(accounts_list_url)

    assert response.status_code == status.HTTP_200_OK
    assert [item["id"] for item in response.data["results"]] == [str(account.id)]


def test_delete_rejects_attachment_of_another_account_on_the_same_individual(
    api_client: APIClient,
    business_area: Any,
    program: Program,
    account: Account,
    second_account_attachment: AccountAttachment,
    attachment_user: User,
) -> None:
    api_client.force_authenticate(user=attachment_user)
    url = reverse(
        "api:households:account-attachments-detail",
        kwargs={
            "business_area_slug": business_area.slug,
            "program_code": program.code,
            "individual_pk": str(account.individual_id),
            "account_pk": str(account.id),
            "file_id": str(second_account_attachment.id),
        },
    )

    response = api_client.delete(url)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert AccountAttachment.objects.filter(pk=second_account_attachment.pk).exists()


def test_post_returns_400_when_the_model_rejects_the_create(
    api_client: APIClient, attachments_list_url: str, attachment_user: User, mocker
) -> None:
    api_client.force_authenticate(user=attachment_user)
    mocker.patch.object(
        AccountAttachment,
        "clean",
        side_effect=DjangoValidationError("Account already has the maximum of 10 attachments."),
    )
    data = {"file": SimpleUploadedFile("wallet.jpg", b"abc", content_type="image/jpeg")}

    response = api_client.post(attachments_list_url, data, format="multipart")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "maximum of 10 attachments" in str(response.data)
