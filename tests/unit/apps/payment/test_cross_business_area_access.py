from typing import Any

from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
import pytest
from rest_framework import status
from rest_framework.test import APIClient

from extras.test_utils.factories import (
    BusinessAreaFactory,
    CurrencyFactory,
    PaymentFactory,
    PaymentPlanFactory,
    PaymentPlanPurposeFactory,
    PaymentPlanSupportingDocumentFactory,
    PaymentVerificationPlanFactory,
    PaymentVerificationSummaryFactory,
    ProgramFactory,
    UserFactory,
)
from hope.apps.account.permissions import Permissions
from hope.models import (
    BusinessArea,
    Payment,
    PaymentPlan,
    PaymentPlanGroup,
    PaymentPlanPurpose,
    PaymentPlanSupportingDocument,
    PaymentVerificationPlan,
    User,
)

pytestmark = pytest.mark.django_db


@pytest.fixture
def attacker_business_area() -> BusinessArea:
    return BusinessAreaFactory(slug="afghanistan")


@pytest.fixture
def victim_business_area() -> BusinessArea:
    return BusinessAreaFactory(slug="ukraine")


@pytest.fixture
def attacker_payment_plan(attacker_business_area: BusinessArea) -> PaymentPlan:
    return PaymentPlanFactory(
        status=PaymentPlan.Status.OPEN,
        program_cycle__program=ProgramFactory(business_area=attacker_business_area),
    )


@pytest.fixture
def victim_payment_plan(victim_business_area: BusinessArea) -> PaymentPlan:
    return PaymentPlanFactory(
        status=PaymentPlan.Status.ACCEPTED,
        program_cycle__program=ProgramFactory(business_area=victim_business_area),
    )


@pytest.fixture
def victim_target_population(victim_business_area: BusinessArea) -> PaymentPlan:
    return PaymentPlanFactory(
        status=PaymentPlan.Status.DRAFT,
        program_cycle__program=ProgramFactory(business_area=victim_business_area),
        currency=CurrencyFactory(),
    )


@pytest.fixture
def attacker_purpose(attacker_payment_plan: PaymentPlan) -> PaymentPlanPurpose:
    purpose = PaymentPlanPurposeFactory()
    attacker_payment_plan.program.payment_plan_purposes.add(purpose)
    return purpose


@pytest.fixture
def victim_document(victim_payment_plan: PaymentPlan) -> PaymentPlanSupportingDocument:
    return PaymentPlanSupportingDocumentFactory(payment_plan=victim_payment_plan)


@pytest.fixture
def victim_payment(victim_payment_plan: PaymentPlan) -> Payment:
    return PaymentFactory(parent=victim_payment_plan)


@pytest.fixture
def victim_verification_plan(victim_payment_plan: PaymentPlan) -> PaymentVerificationPlan:
    PaymentVerificationSummaryFactory(payment_plan=victim_payment_plan)
    return PaymentVerificationPlanFactory(payment_plan=victim_payment_plan)


@pytest.fixture
def attacker(
    attacker_business_area: BusinessArea,
    attacker_payment_plan: PaymentPlan,
    create_user_role_with_permissions: Any,
) -> User:
    user = UserFactory()
    create_user_role_with_permissions(
        user,
        [
            Permissions.PM_VIEW_LIST,
            Permissions.PM_VIEW_DETAILS,
            Permissions.PM_CREATE,
            Permissions.PM_UPLOAD_SUPPORTING_DOCUMENT,
            Permissions.PM_DOWNLOAD_SUPPORTING_DOCUMENT,
            Permissions.PM_DELETE_SUPPORTING_DOCUMENT,
            Permissions.TARGETING_VIEW_LIST,
            Permissions.TARGETING_VIEW_DETAILS,
            Permissions.TARGETING_REMOVE,
            Permissions.TARGETING_DUPLICATE,
            Permissions.PAYMENT_VERIFICATION_VIEW_LIST,
            Permissions.PAYMENT_VERIFICATION_VIEW_DETAILS,
            Permissions.PAYMENT_VERIFICATION_DELETE,
            Permissions.PAYMENT_VERIFICATION_ACTIVATE,
            Permissions.PM_PAYMENT_PLAN_GROUP_CREATE,
        ],
        attacker_business_area,
        program=attacker_payment_plan.program,
    )
    return user


@pytest.fixture
def api_client(attacker: User) -> APIClient:
    client = APIClient()
    client.force_authenticate(user=attacker)
    return client


@pytest.fixture
def upload_file() -> SimpleUploadedFile:
    return SimpleUploadedFile("test.pdf", b"123", content_type="application/pdf")


@pytest.fixture
def api_client_without_role() -> APIClient:
    client = APIClient()
    client.force_authenticate(user=UserFactory())
    return client


@pytest.fixture
def cross_ba_kwargs(attacker_business_area: BusinessArea, attacker_payment_plan: PaymentPlan) -> dict[str, str]:
    """Path segments the attacker is authorized for - the object ids appended to them are not."""
    return {
        "business_area_slug": attacker_business_area.slug,
        "program_code": attacker_payment_plan.program.code,
    }


def test_download_supporting_document_without_permission_is_denied(
    api_client_without_role: APIClient,
    cross_ba_kwargs: dict[str, str],
    victim_document: PaymentPlanSupportingDocument,
) -> None:
    url = reverse(
        "api:payments:supporting-documents-download",
        kwargs={
            **cross_ba_kwargs,
            "payment_plan_pk": str(victim_document.payment_plan.id),
            "file_id": str(victim_document.id),
        },
    )

    response = api_client_without_role.get(url)

    assert response.status_code == status.HTTP_403_FORBIDDEN, response.status_code


def test_download_supporting_document_from_other_business_area_is_denied(
    api_client: APIClient,
    cross_ba_kwargs: dict[str, str],
    victim_document: PaymentPlanSupportingDocument,
) -> None:
    url = reverse(
        "api:payments:supporting-documents-download",
        kwargs={
            **cross_ba_kwargs,
            "payment_plan_pk": str(victim_document.payment_plan.id),
            "file_id": str(victim_document.id),
        },
    )

    response = api_client.get(url)

    assert response.status_code == status.HTTP_404_NOT_FOUND, response.status_code


def test_delete_supporting_document_from_other_business_area_is_denied(
    api_client: APIClient,
    cross_ba_kwargs: dict[str, str],
    victim_document: PaymentPlanSupportingDocument,
) -> None:
    url = reverse(
        "api:payments:supporting-documents-detail",
        kwargs={
            **cross_ba_kwargs,
            "payment_plan_pk": str(victim_document.payment_plan.id),
            "file_id": str(victim_document.id),
        },
    )

    response = api_client.delete(url)

    assert response.status_code == status.HTTP_404_NOT_FOUND, response.status_code
    assert PaymentPlanSupportingDocument.objects.filter(id=victim_document.id).exists()


def test_upload_supporting_document_to_other_business_area_is_denied(
    api_client: APIClient,
    cross_ba_kwargs: dict[str, str],
    victim_payment_plan: PaymentPlan,
    upload_file: SimpleUploadedFile,
) -> None:
    url = reverse(
        "api:payments:supporting-documents-list",
        kwargs={**cross_ba_kwargs, "payment_plan_pk": str(victim_payment_plan.id)},
    )

    response = api_client.post(url, {"title": "cross ba", "file": upload_file}, format="multipart")

    assert response.status_code == status.HTTP_404_NOT_FOUND, response.status_code
    assert not victim_payment_plan.documents.exists()


def test_retrieve_payment_plan_from_other_business_area_is_denied(
    api_client: APIClient, cross_ba_kwargs: dict[str, str], victim_payment_plan: PaymentPlan
) -> None:
    url = reverse("api:payments:payment-plans-detail", kwargs={**cross_ba_kwargs, "pk": str(victim_payment_plan.id)})

    response = api_client.get(url)

    assert response.status_code == status.HTTP_404_NOT_FOUND, response.status_code


def test_retrieve_target_population_from_other_business_area_is_denied(
    api_client: APIClient, cross_ba_kwargs: dict[str, str], victim_payment_plan: PaymentPlan
) -> None:
    url = reverse(
        "api:payments:target-populations-detail", kwargs={**cross_ba_kwargs, "pk": str(victim_payment_plan.id)}
    )

    response = api_client.get(url)

    assert response.status_code == status.HTTP_404_NOT_FOUND, response.status_code


def test_retrieve_payment_verification_from_other_business_area_is_denied(
    api_client: APIClient, cross_ba_kwargs: dict[str, str], victim_payment_plan: PaymentPlan
) -> None:
    url = reverse(
        "api:payments:payment-verifications-detail", kwargs={**cross_ba_kwargs, "pk": str(victim_payment_plan.id)}
    )

    response = api_client.get(url)

    assert response.status_code == status.HTTP_404_NOT_FOUND, response.status_code


def test_delete_payment_verification_plan_from_other_business_area_is_denied(
    api_client: APIClient,
    cross_ba_kwargs: dict[str, str],
    victim_verification_plan: PaymentVerificationPlan,
) -> None:
    url = reverse(
        "api:payments:payment-verifications-delete-payment-verification-plan",
        kwargs={
            **cross_ba_kwargs,
            "pk": str(victim_verification_plan.payment_plan.id),
            "verification_plan_id": str(victim_verification_plan.id),
        },
    )

    response = api_client.post(url, {}, format="json")

    assert response.status_code == status.HTTP_404_NOT_FOUND, response.status_code
    assert PaymentVerificationPlan.objects.filter(id=victim_verification_plan.id).exists()


def test_activate_verification_plan_from_other_business_area_under_own_plan_is_denied(
    api_client: APIClient,
    cross_ba_kwargs: dict[str, str],
    attacker_payment_plan: PaymentPlan,
    victim_verification_plan: PaymentVerificationPlan,
) -> None:
    url = reverse(
        "api:payments:payment-verifications-activate-payment-verification-plan",
        kwargs={
            **cross_ba_kwargs,
            "pk": str(attacker_payment_plan.id),
            "verification_plan_id": str(victim_verification_plan.id),
        },
    )

    response = api_client.post(url, {}, format="json")

    assert response.status_code == status.HTTP_404_NOT_FOUND, response.status_code
    victim_verification_plan.refresh_from_db()
    assert victim_verification_plan.status == PaymentVerificationPlan.STATUS_PENDING


def test_list_verification_records_from_other_business_area_is_denied(
    api_client: APIClient, cross_ba_kwargs: dict[str, str], victim_payment_plan: PaymentPlan
) -> None:
    url = reverse(
        "api:payments:verification-records-list",
        kwargs={**cross_ba_kwargs, "payment_verification_pk": str(victim_payment_plan.id)},
    )

    response = api_client.get(url)

    assert response.status_code == status.HTTP_404_NOT_FOUND, response.status_code


def test_create_payment_plan_from_other_business_area_target_population_is_denied(
    api_client: APIClient, cross_ba_kwargs: dict[str, str], victim_target_population: PaymentPlan
) -> None:
    url = reverse("api:payments:payment-plans-list", kwargs=cross_ba_kwargs)

    response = api_client.post(
        url,
        {
            "target_population_id": str(victim_target_population.id),
            "dispersion_start_date": "2050-01-01",
            "dispersion_end_date": "2050-02-01",
            "currency": "PLN",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND, response.status_code


def test_copy_target_population_into_other_business_area_cycle_is_denied(
    api_client: APIClient,
    cross_ba_kwargs: dict[str, str],
    attacker_payment_plan: PaymentPlan,
    victim_payment_plan: PaymentPlan,
    attacker_purpose: PaymentPlanPurpose,
) -> None:
    url = reverse(
        "api:payments:target-populations-copy", kwargs={**cross_ba_kwargs, "pk": str(attacker_payment_plan.id)}
    )

    response = api_client.post(
        url,
        {
            "name": "copied across business areas",
            "program_cycle_id": str(victim_payment_plan.program_cycle_id),
            "payment_plan_group_id": str(victim_payment_plan.payment_plan_group_id),
            "payment_plan_purposes": [str(attacker_purpose.id)],
        },
        format="json",
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND, response.status_code
    assert not PaymentPlan.objects.filter(name="copied across business areas").exists()


def test_retrieve_payment_from_other_business_area_is_denied(
    api_client: APIClient, cross_ba_kwargs: dict[str, str], victim_payment: Payment
) -> None:
    url = reverse(
        "api:payments:payments-detail",
        kwargs={
            **cross_ba_kwargs,
            "payment_plan_pk": str(victim_payment.parent_id),
            "payment_id": str(victim_payment.id),
        },
    )

    response = api_client.get(url)

    assert response.status_code == status.HTTP_404_NOT_FOUND, response.status_code


@pytest.fixture
def attacker_second_payment_plan(attacker_payment_plan: PaymentPlan) -> PaymentPlan:
    return PaymentPlanFactory(
        status=PaymentPlan.Status.ACCEPTED,
        program_cycle__program=attacker_payment_plan.program,
    )


@pytest.fixture
def attacker_second_plan_payment(attacker_second_payment_plan: PaymentPlan) -> Payment:
    return PaymentFactory(parent=attacker_second_payment_plan)


@pytest.fixture
def attacker_second_plan_verification_plan(attacker_second_payment_plan: PaymentPlan) -> PaymentVerificationPlan:
    PaymentVerificationSummaryFactory(payment_plan=attacker_second_payment_plan)
    return PaymentVerificationPlanFactory(payment_plan=attacker_second_payment_plan)


def test_retrieve_payment_under_mismatched_payment_plan_path_is_denied(
    api_client: APIClient,
    cross_ba_kwargs: dict[str, str],
    attacker_payment_plan: PaymentPlan,
    attacker_second_plan_payment: Payment,
) -> None:
    url = reverse(
        "api:payments:payments-detail",
        kwargs={
            **cross_ba_kwargs,
            "payment_plan_pk": str(attacker_payment_plan.id),
            "payment_id": str(attacker_second_plan_payment.id),
        },
    )

    response = api_client.get(url)

    assert response.status_code == status.HTTP_404_NOT_FOUND, response.status_code


def test_retrieve_verification_record_under_mismatched_payment_plan_path_is_denied(
    api_client: APIClient,
    cross_ba_kwargs: dict[str, str],
    attacker_payment_plan: PaymentPlan,
    attacker_second_plan_payment: Payment,
) -> None:
    url = reverse(
        "api:payments:verification-records-detail",
        kwargs={
            **cross_ba_kwargs,
            "payment_verification_pk": str(attacker_payment_plan.id),
            "pk": str(attacker_second_plan_payment.id),
        },
    )

    response = api_client.get(url)

    assert response.status_code == status.HTTP_404_NOT_FOUND, response.status_code


def test_delete_verification_plan_of_another_payment_plan_is_denied(
    api_client: APIClient,
    cross_ba_kwargs: dict[str, str],
    attacker_payment_plan: PaymentPlan,
    attacker_second_plan_verification_plan: PaymentVerificationPlan,
) -> None:
    url = reverse(
        "api:payments:payment-verifications-delete-payment-verification-plan",
        kwargs={
            **cross_ba_kwargs,
            "pk": str(attacker_payment_plan.id),
            "verification_plan_id": str(attacker_second_plan_verification_plan.id),
        },
    )

    response = api_client.post(url, {}, format="json")

    assert response.status_code == status.HTTP_404_NOT_FOUND, response.status_code
    assert PaymentVerificationPlan.objects.filter(id=attacker_second_plan_verification_plan.id).exists()


def test_activate_verification_plan_of_another_payment_plan_is_denied(
    api_client: APIClient,
    cross_ba_kwargs: dict[str, str],
    attacker_payment_plan: PaymentPlan,
    attacker_second_plan_verification_plan: PaymentVerificationPlan,
) -> None:
    url = reverse(
        "api:payments:payment-verifications-activate-payment-verification-plan",
        kwargs={
            **cross_ba_kwargs,
            "pk": str(attacker_payment_plan.id),
            "verification_plan_id": str(attacker_second_plan_verification_plan.id),
        },
    )

    response = api_client.post(url, {}, format="json")

    assert response.status_code == status.HTTP_404_NOT_FOUND, response.status_code
    attacker_second_plan_verification_plan.refresh_from_db()
    assert attacker_second_plan_verification_plan.status == PaymentVerificationPlan.STATUS_PENDING


def test_create_payment_plan_group_in_cycle_of_other_business_area_is_denied(
    api_client: APIClient,
    cross_ba_kwargs: dict[str, str],
    victim_payment_plan: PaymentPlan,
) -> None:
    victim_cycle = victim_payment_plan.program_cycle
    url = reverse("api:payments:payment-plan-groups-list", kwargs=cross_ba_kwargs)

    response = api_client.post(url, {"name": "cross ba group", "cycle": str(victim_cycle.id)}, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST, response.status_code
    assert not PaymentPlanGroup.objects.filter(cycle=victim_cycle, name="cross ba group").exists()
