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
    download_payment_plan_group_batch,
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


def test_download_payment_plan_payment_list_wrong_status_raises(rf, create_user_role_with_permissions, user):
    payment_plan = PaymentPlanFactory(status=PaymentPlan.Status.OPEN)
    create_user_role_with_permissions(user, [Permissions.PM_VIEW_LIST], payment_plan.business_area)

    request = rf.get(reverse("download-payment-plan-payment-list", args=[payment_plan.id]))
    request.user = user

    with pytest.raises(
        ValidationError,
        match="Export XLSX is possible only for Payment Plan within status LOCK, ACCEPTED or FINISHED.",
    ):
        download_payment_plan_payment_list(request, str(payment_plan.id))


def test_download_payment_plan_payment_list_empty_file_raises(rf, create_user_role_with_permissions, user):
    payment_plan = PaymentPlanFactory(status=PaymentPlan.Status.LOCKED)
    payment_plan.export_file_entitlement = FileTempFactory(file="", created_by=user)
    payment_plan.save()
    create_user_role_with_permissions(user, [Permissions.PM_VIEW_LIST], payment_plan.business_area)

    request = rf.get(reverse("download-payment-plan-payment-list", args=[payment_plan.id]))
    request.user = user

    with pytest.raises(ValueError, match="Payment plan export file link must not be None"):
        download_payment_plan_payment_list(request, str(payment_plan.id))


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


def test_download_payment_plan_summary_pdf_missing_file_raises(
    rf,
    create_user_role_with_permissions,
    payment_plan_accepted,
    user,
):
    create_user_role_with_permissions(user, [Permissions.PM_EXPORT_PDF_SUMMARY], payment_plan_accepted.business_area)

    request = rf.get(reverse("download-payment-plan-summary-pdf", args=[payment_plan_accepted.id]))
    request.user = user

    with pytest.raises(FileNotFoundError):
        download_payment_plan_summary_pdf(request, str(payment_plan_accepted.id))


@pytest.fixture
def group_with_batch_file(user):
    cycle = ProgramCycleFactory()
    group = PaymentPlanGroupFactory(cycle=cycle)
    file_temp = FileTempFactory(
        file=SimpleUploadedFile("batch-1.xlsx", b"data"),
        created_by=user,
    )
    PaymentPlanFactory(
        payment_plan_group=group,
        program_cycle=cycle,
        business_area=cycle.program.business_area,
        status=PaymentPlan.Status.ACCEPTED,
        export_tag=1,
        export_file_delivery=file_temp,
    )
    return {"group": group, "file": file_temp}


def test_download_payment_plan_group_batch_requires_permission(rf, group_with_batch_file, user):
    group = group_with_batch_file["group"]
    request = rf.get(reverse("download-payment-plan-group-batch", args=[str(group.id), 1]))
    request.user = user

    with pytest.raises(PermissionDenied) as excinfo:
        download_payment_plan_group_batch(request, str(group.id), 1)

    assert excinfo.value.args[0]["required_permissions"] == [Permissions.PM_PAYMENT_PLAN_GROUP_EXPORT_XLSX.value]


def test_download_payment_plan_group_batch_redirects_with_permission(
    rf,
    create_user_role_with_permissions,
    group_with_batch_file,
    user,
):
    group = group_with_batch_file["group"]
    create_user_role_with_permissions(
        user,
        [Permissions.PM_PAYMENT_PLAN_GROUP_EXPORT_XLSX],
        group.cycle.program.business_area,
        program=group.cycle.program,
    )
    request = rf.get(reverse("download-payment-plan-group-batch", args=[str(group.id), 1]))
    request.user = user

    response = download_payment_plan_group_batch(request, str(group.id), 1)

    assert response.status_code == 302
    assert response.url == group_with_batch_file["file"].file.url


def test_download_payment_plan_group_batch_missing_file_raises(
    rf,
    create_user_role_with_permissions,
    user,
):
    cycle = ProgramCycleFactory()
    group = PaymentPlanGroupFactory(cycle=cycle)
    PaymentPlanFactory(
        payment_plan_group=group,
        program_cycle=cycle,
        business_area=cycle.program.business_area,
        status=PaymentPlan.Status.ACCEPTED,
        export_tag=1,
        export_file_delivery=None,
    )
    create_user_role_with_permissions(
        user,
        [Permissions.PM_PAYMENT_PLAN_GROUP_EXPORT_XLSX],
        cycle.program.business_area,
        program=cycle.program,
    )
    request = rf.get(reverse("download-payment-plan-group-batch", args=[str(group.id), 1]))
    request.user = user

    with pytest.raises(FileNotFoundError):
        download_payment_plan_group_batch(request, str(group.id), 1)
