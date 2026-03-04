from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
import pytest

from extras.test_utils.factories import (
    FileTempFactory,
    PaymentPlanFactory,
    PaymentVerificationPlanFactory,
    PaymentVerificationSummaryFactory,
    UserFactory,
)
from hope.apps.account.permissions import Permissions
from hope.apps.payment.views import (
    download_payment_plan_payment_list,
    download_payment_plan_summary_pdf,
    download_payment_verification_plan,
)
from hope.models import PaymentPlan, PaymentVerificationPlan

pytestmark = pytest.mark.django_db


@pytest.fixture
def user():
    return UserFactory()


@pytest.fixture
def payment_plan_locked():
    return PaymentPlanFactory(
        status=PaymentPlan.Status.LOCKED,
    )


@pytest.fixture
def payment_plan_accepted():
    return PaymentPlanFactory(
        status=PaymentPlan.Status.ACCEPTED,
    )


@pytest.fixture
def payment_plan_with_entitlement_file(payment_plan_locked, user):
    export_file_entitlement = FileTempFactory(
        file=SimpleUploadedFile("payment-list.xlsx", b"data"),
        created_by=user,
    )
    payment_plan_locked.export_file_entitlement = export_file_entitlement
    payment_plan_locked.save()
    return payment_plan_locked


@pytest.fixture
def payment_verification_plan(payment_plan_accepted):
    PaymentVerificationSummaryFactory(payment_plan=payment_plan_accepted)
    return PaymentVerificationPlanFactory(
        payment_plan=payment_plan_accepted,
        verification_channel=PaymentVerificationPlan.VERIFICATION_CHANNEL_XLSX,
    )


@pytest.fixture
def payment_verification_file(user, payment_verification_plan):
    return FileTempFactory(
        object_id=payment_verification_plan.pk,
        content_type=ContentType.objects.get_for_model(PaymentVerificationPlan),
        created_by=user,
        file=SimpleUploadedFile("verification.xlsx", b"data"),
    )


def test_download_payment_verification_plan_requires_permission(rf, payment_verification_plan, user):
    request = rf.get(reverse("download-payment-verification-plan", args=[payment_verification_plan.id]))
    request.user = user

    with pytest.raises(PermissionDenied) as excinfo:
        download_payment_verification_plan(request, str(payment_verification_plan.id))

    assert excinfo.value.args[0]["required_permissions"] == [Permissions.PAYMENT_VERIFICATION_EXPORT.value]


def test_download_payment_verification_plan_redirects_with_permission(
    rf,
    create_user_role_with_permissions,
    payment_verification_plan,
    payment_verification_file,
    user,
):
    create_user_role_with_permissions(
        user,
        [Permissions.PAYMENT_VERIFICATION_EXPORT],
        payment_verification_plan.payment_plan.business_area,
    )

    request = rf.get(reverse("download-payment-verification-plan", args=[payment_verification_plan.id]))
    request.user = user

    response = download_payment_verification_plan(request, str(payment_verification_plan.id))

    assert response.status_code == 302
    assert response.url == payment_verification_file.file.url
    payment_verification_file.refresh_from_db()
    assert payment_verification_file.was_downloaded is True


def test_download_payment_plan_payment_list_requires_permission(rf, payment_plan_with_entitlement_file, user):
    request = rf.get(reverse("download-payment-plan-payment-list", args=[payment_plan_with_entitlement_file.id]))
    request.user = user

    with pytest.raises(PermissionDenied) as excinfo:
        download_payment_plan_payment_list(request, str(payment_plan_with_entitlement_file.id))

    assert excinfo.value.args[0]["required_permissions"] == [Permissions.PM_VIEW_LIST.value]


def test_download_payment_plan_payment_list_redirects_with_permission(
    rf,
    create_user_role_with_permissions,
    payment_plan_with_entitlement_file,
    user,
):
    create_user_role_with_permissions(
        user, [Permissions.PM_VIEW_LIST], payment_plan_with_entitlement_file.business_area
    )

    request = rf.get(reverse("download-payment-plan-payment-list", args=[payment_plan_with_entitlement_file.id]))
    request.user = user

    response = download_payment_plan_payment_list(request, str(payment_plan_with_entitlement_file.id))

    assert response.status_code == 302
    assert response.url == payment_plan_with_entitlement_file.payment_list_export_file_link


def test_download_payment_plan_summary_pdf_requires_permission(rf, payment_plan_accepted, user):
    request = rf.get(reverse("download-payment-plan-summary-pdf", args=[payment_plan_accepted.id]))
    request.user = user

    with pytest.raises(PermissionDenied) as excinfo:
        download_payment_plan_summary_pdf(request, str(payment_plan_accepted.id))

    assert excinfo.value.args[0]["required_permissions"] == [Permissions.PM_EXPORT_PDF_SUMMARY.value]


def test_download_payment_plan_summary_pdf_redirects_with_permission(
    rf,
    create_user_role_with_permissions,
    payment_plan_accepted,
    user,
):
    create_user_role_with_permissions(user, [Permissions.PM_EXPORT_PDF_SUMMARY], payment_plan_accepted.business_area)

    payment_plan_accepted.export_pdf_file_summary = FileTempFactory(
        file=SimpleUploadedFile("summary.pdf", b"data"),
        created_by=user,
    )
    payment_plan_accepted.save()

    request = rf.get(reverse("download-payment-plan-summary-pdf", args=[payment_plan_accepted.id]))
    request.user = user

    response = download_payment_plan_summary_pdf(request, str(payment_plan_accepted.id))

    assert response.status_code == 302
    assert response.url == payment_plan_accepted.export_pdf_file_summary.file.url
