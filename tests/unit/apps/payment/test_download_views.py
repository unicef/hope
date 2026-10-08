from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
import pytest
from rest_framework.exceptions import ValidationError

from extras.test_utils.factories import (
    FileTempFactory,
    PaymentPlanFactory,
    PaymentPlanGroupFactory,
    PaymentVerificationPlanFactory,
    PaymentVerificationSummaryFactory,
    ProgramCycleFactory,
    UserFactory,
)
from hope.apps.account.permissions import Permissions
from hope.apps.payment.views import (
    download_payment_plan_group_summary_pdf,
    download_payment_plan_group_xlsx,
    download_payment_plan_payment_list,
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


def test_download_payment_verification_plan_non_xlsx_channel_raises(
    rf,
    create_user_role_with_permissions,
    payment_plan_accepted,
    user,
):
    PaymentVerificationSummaryFactory(payment_plan=payment_plan_accepted)
    verification_plan = PaymentVerificationPlanFactory(
        payment_plan=payment_plan_accepted,
        verification_channel=PaymentVerificationPlan.VERIFICATION_CHANNEL_MANUAL,
    )
    create_user_role_with_permissions(
        user,
        [Permissions.PAYMENT_VERIFICATION_EXPORT],
        payment_plan_accepted.business_area,
    )

    request = rf.get(reverse("download-payment-verification-plan", args=[verification_plan.id]))
    request.user = user

    with pytest.raises(ValidationError, match="You can only download verification file when XLSX channel is selected"):
        download_payment_verification_plan(request, str(verification_plan.id))


def test_download_payment_verification_plan_missing_file_raises(
    rf,
    create_user_role_with_permissions,
    payment_verification_plan,
    user,
):
    create_user_role_with_permissions(
        user,
        [Permissions.PAYMENT_VERIFICATION_EXPORT],
        payment_verification_plan.payment_plan.business_area,
    )

    request = rf.get(reverse("download-payment-verification-plan", args=[payment_verification_plan.id]))
    request.user = user

    with pytest.raises(FileNotFoundError):
        download_payment_verification_plan(request, str(payment_verification_plan.id))


def test_download_payment_verification_plan_already_downloaded_redirects(
    rf,
    create_user_role_with_permissions,
    payment_verification_plan,
    payment_verification_file,
    user,
):
    payment_verification_file.was_downloaded = True
    payment_verification_file.save()
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
    assert response.url == payment_plan_with_entitlement_file.entitlement_export_file_link


def test_download_payment_plan_payment_list_wrong_status_raises(rf, create_user_role_with_permissions, user):
    payment_plan = PaymentPlanFactory(status=PaymentPlan.Status.FINISHED)
    create_user_role_with_permissions(user, [Permissions.PM_VIEW_LIST], payment_plan.business_area)

    request = rf.get(reverse("download-payment-plan-payment-list", args=[payment_plan.id]))
    request.user = user

    with pytest.raises(
        ValidationError,
        match="Export XLSX is possible only for Payment Plan within status LOCK.",
    ):
        download_payment_plan_payment_list(request, str(payment_plan.id))


def test_download_payment_plan_payment_list_missing_file_raises(rf, create_user_role_with_permissions, user):
    payment_plan = PaymentPlanFactory(status=PaymentPlan.Status.LOCKED)
    create_user_role_with_permissions(user, [Permissions.PM_VIEW_LIST], payment_plan.business_area)

    request = rf.get(reverse("download-payment-plan-payment-list", args=[payment_plan.id]))
    request.user = user

    with pytest.raises(FileNotFoundError):
        download_payment_plan_payment_list(request, str(payment_plan.id))


def test_download_payment_plan_payment_list_empty_file_raises(rf, create_user_role_with_permissions, user):
    payment_plan = PaymentPlanFactory(status=PaymentPlan.Status.LOCKED)
    payment_plan.export_file_entitlement = FileTempFactory(file="", created_by=user)
    payment_plan.save()
    create_user_role_with_permissions(user, [Permissions.PM_VIEW_LIST], payment_plan.business_area)

    request = rf.get(reverse("download-payment-plan-payment-list", args=[payment_plan.id]))
    request.user = user

    with pytest.raises(ValueError, match="Payment plan entitlement export file link must not be None"):
        download_payment_plan_payment_list(request, str(payment_plan.id))


@pytest.fixture
def group_with_export_file(user):
    cycle = ProgramCycleFactory()
    file_temp = FileTempFactory(
        file=SimpleUploadedFile("payment-list.xlsx", b"data"),
        created_by=user,
    )
    return PaymentPlanGroupFactory(cycle=cycle, export_file_delivery=file_temp)


def test_download_payment_plan_group_xlsx_requires_permission(rf, group_with_export_file, user):
    group = group_with_export_file
    request = rf.get(reverse("download-payment-plan-group-xlsx", args=[str(group.id)]))
    request.user = user

    with pytest.raises(PermissionDenied) as excinfo:
        download_payment_plan_group_xlsx(request, str(group.id))

    assert excinfo.value.args[0]["required_permissions"] == [Permissions.PM_PAYMENT_PLAN_GROUP_EXPORT_XLSX.value]


def test_download_payment_plan_group_xlsx_redirects_with_permission(
    rf,
    create_user_role_with_permissions,
    group_with_export_file,
    user,
):
    group = group_with_export_file
    create_user_role_with_permissions(
        user,
        [Permissions.PM_PAYMENT_PLAN_GROUP_EXPORT_XLSX],
        group.cycle.program.business_area,
        program=group.cycle.program,
    )
    request = rf.get(reverse("download-payment-plan-group-xlsx", args=[str(group.id)]))
    request.user = user

    response = download_payment_plan_group_xlsx(request, str(group.id))

    assert response.status_code == 302
    assert response.url == group.export_file_delivery.file.url


def test_download_payment_plan_group_xlsx_missing_file_raises(
    rf,
    create_user_role_with_permissions,
    user,
):
    cycle = ProgramCycleFactory()
    group = PaymentPlanGroupFactory(cycle=cycle)
    create_user_role_with_permissions(
        user,
        [Permissions.PM_PAYMENT_PLAN_GROUP_EXPORT_XLSX],
        cycle.program.business_area,
        program=cycle.program,
    )
    request = rf.get(reverse("download-payment-plan-group-xlsx", args=[str(group.id)]))
    request.user = user

    with pytest.raises(FileNotFoundError):
        download_payment_plan_group_xlsx(request, str(group.id))


@pytest.fixture
def group_with_summary_pdf(user):
    group = PaymentPlanGroupFactory(cycle=ProgramCycleFactory())
    group.export_pdf_file_summary = FileTempFactory(file=SimpleUploadedFile("summary.pdf", b"data"), created_by=user)
    group.save(update_fields=["export_pdf_file_summary"])
    return group


def test_download_payment_plan_group_summary_pdf_requires_permission(rf, group_with_summary_pdf, user):
    request = rf.get(reverse("download-payment-plan-group-summary-pdf", args=[group_with_summary_pdf.id]))
    request.user = user

    with pytest.raises(PermissionDenied) as excinfo:
        download_payment_plan_group_summary_pdf(request, str(group_with_summary_pdf.id))

    assert excinfo.value.args[0]["required_permissions"] == [Permissions.PM_EXPORT_PDF_SUMMARY.value]


def test_download_payment_plan_group_summary_pdf_redirects_with_permission(
    rf, create_user_role_with_permissions, group_with_summary_pdf, user
):
    create_user_role_with_permissions(user, [Permissions.PM_EXPORT_PDF_SUMMARY], group_with_summary_pdf.business_area)
    request = rf.get(reverse("download-payment-plan-group-summary-pdf", args=[group_with_summary_pdf.id]))
    request.user = user

    response = download_payment_plan_group_summary_pdf(request, str(group_with_summary_pdf.id))

    assert response.status_code == 302
    assert response.url == group_with_summary_pdf.export_pdf_file_summary.file.url


def test_download_payment_plan_group_summary_pdf_missing_file_raises(rf, create_user_role_with_permissions, user):
    group = PaymentPlanGroupFactory(cycle=ProgramCycleFactory())
    create_user_role_with_permissions(user, [Permissions.PM_EXPORT_PDF_SUMMARY], group.business_area)
    request = rf.get(reverse("download-payment-plan-group-summary-pdf", args=[group.id]))
    request.user = user

    with pytest.raises(FileNotFoundError):
        download_payment_plan_group_summary_pdf(request, str(group.id))
