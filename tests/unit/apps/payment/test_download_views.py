from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
import pytest
from rest_framework.exceptions import ValidationError

from extras.test_utils.factories import (
    FileTempFactory,
    FollowUpInstructionFactory,
    PaymentListFactory,
    PaymentPlanFactory,
    PaymentVerificationPlanFactory,
    PaymentVerificationSummaryFactory,
    ProgramCycleFactory,
    ProgramFactory,
    UserFactory,
)
from hope.apps.account.permissions import Permissions
from hope.apps.payment.views import (
    download_follow_up_instruction_summary_pdf,
    download_follow_up_instruction_xlsx,
    download_payment_list,
    download_payment_plan_summary_pdf,
    download_payment_plan_xlsx,
    download_payment_verification_plan,
)
from hope.models import PaymentList, PaymentVerificationPlan

pytestmark = pytest.mark.django_db


@pytest.fixture
def user():
    return UserFactory()


@pytest.fixture
def payment_list_locked():
    return PaymentListFactory(
        status=PaymentList.Status.LOCKED,
    )


@pytest.fixture
def payment_list_accepted():
    return PaymentListFactory(
        status=PaymentList.Status.ACCEPTED,
    )


@pytest.fixture
def payment_list_with_entitlement_file(payment_list_locked, user):
    export_file_entitlement = FileTempFactory(
        file=SimpleUploadedFile("payment-list.xlsx", b"data"),
        created_by=user,
    )
    payment_list_locked.export_file_entitlement = export_file_entitlement
    payment_list_locked.save()
    return payment_list_locked


@pytest.fixture
def payment_verification_plan(payment_list_accepted):
    PaymentVerificationSummaryFactory(payment_list=payment_list_accepted)
    return PaymentVerificationPlanFactory(
        payment_list=payment_list_accepted,
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
        payment_verification_plan.payment_list.business_area,
        program=payment_verification_plan.payment_list.program,
    )

    request = rf.get(reverse("download-payment-verification-plan", args=[payment_verification_plan.id]))
    request.user = user

    response = download_payment_verification_plan(request, str(payment_verification_plan.id))

    assert response.status_code == 302
    assert response.url == payment_verification_file.file.url
    payment_verification_file.refresh_from_db()
    assert payment_verification_file.was_downloaded is True


def test_download_payment_verification_plan_refuses_permission_in_other_program(
    rf, create_user_role_with_permissions, payment_verification_plan, payment_verification_file, user
):
    other_program = ProgramFactory(business_area=payment_verification_plan.payment_list.business_area)
    create_user_role_with_permissions(
        user, [Permissions.PAYMENT_VERIFICATION_EXPORT], other_program.business_area, program=other_program
    )
    request = rf.get(reverse("download-payment-verification-plan", args=[payment_verification_plan.id]))
    request.user = user

    with pytest.raises(PermissionDenied):
        download_payment_verification_plan(request, str(payment_verification_plan.id))


def test_download_payment_verification_plan_non_xlsx_channel_raises(
    rf,
    create_user_role_with_permissions,
    payment_list_accepted,
    user,
):
    PaymentVerificationSummaryFactory(payment_list=payment_list_accepted)
    verification_plan = PaymentVerificationPlanFactory(
        payment_list=payment_list_accepted,
        verification_channel=PaymentVerificationPlan.VERIFICATION_CHANNEL_MANUAL,
    )
    create_user_role_with_permissions(
        user,
        [Permissions.PAYMENT_VERIFICATION_EXPORT],
        payment_list_accepted.business_area,
        program=payment_list_accepted.program,
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
        payment_verification_plan.payment_list.business_area,
        program=payment_verification_plan.payment_list.program,
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
        payment_verification_plan.payment_list.business_area,
        program=payment_verification_plan.payment_list.program,
    )

    request = rf.get(reverse("download-payment-verification-plan", args=[payment_verification_plan.id]))
    request.user = user

    response = download_payment_verification_plan(request, str(payment_verification_plan.id))

    assert response.status_code == 302
    assert response.url == payment_verification_file.file.url


def test_download_payment_list_requires_permission(rf, payment_list_with_entitlement_file, user):
    request = rf.get(reverse("download-payment-list", args=[payment_list_with_entitlement_file.id]))
    request.user = user

    with pytest.raises(PermissionDenied) as excinfo:
        download_payment_list(request, str(payment_list_with_entitlement_file.id))

    assert excinfo.value.args[0]["required_permissions"] == [Permissions.PM_VIEW_LIST.value]


def test_download_payment_list_redirects_with_permission(
    rf,
    create_user_role_with_permissions,
    payment_list_with_entitlement_file,
    user,
):
    create_user_role_with_permissions(
        user,
        [Permissions.PM_VIEW_LIST],
        payment_list_with_entitlement_file.business_area,
        program=payment_list_with_entitlement_file.program,
    )

    request = rf.get(reverse("download-payment-list", args=[payment_list_with_entitlement_file.id]))
    request.user = user

    response = download_payment_list(request, str(payment_list_with_entitlement_file.id))

    assert response.status_code == 302
    assert response.url == payment_list_with_entitlement_file.entitlement_export_file_link


def test_download_payment_list_refuses_permission_in_other_program(
    rf, create_user_role_with_permissions, payment_list_with_entitlement_file, user
):
    other_program = ProgramFactory(business_area=payment_list_with_entitlement_file.business_area)
    create_user_role_with_permissions(
        user, [Permissions.PM_VIEW_LIST], other_program.business_area, program=other_program
    )
    request = rf.get(reverse("download-payment-list", args=[payment_list_with_entitlement_file.id]))
    request.user = user

    with pytest.raises(PermissionDenied):
        download_payment_list(request, str(payment_list_with_entitlement_file.id))


def test_download_payment_list_wrong_status_raises(rf, create_user_role_with_permissions, user):
    payment_list = PaymentListFactory(status=PaymentList.Status.FINISHED)
    create_user_role_with_permissions(
        user, [Permissions.PM_VIEW_LIST], payment_list.business_area, program=payment_list.program
    )

    request = rf.get(reverse("download-payment-list", args=[payment_list.id]))
    request.user = user

    with pytest.raises(
        ValidationError,
        match="Export XLSX is possible only for Payment List within status LOCK.",
    ):
        download_payment_list(request, str(payment_list.id))


def test_download_payment_list_missing_file_raises(rf, create_user_role_with_permissions, user):
    payment_list = PaymentListFactory(status=PaymentList.Status.LOCKED)
    create_user_role_with_permissions(
        user, [Permissions.PM_VIEW_LIST], payment_list.business_area, program=payment_list.program
    )

    request = rf.get(reverse("download-payment-list", args=[payment_list.id]))
    request.user = user

    with pytest.raises(FileNotFoundError):
        download_payment_list(request, str(payment_list.id))


def test_download_payment_list_empty_file_raises(rf, create_user_role_with_permissions, user):
    payment_list = PaymentListFactory(status=PaymentList.Status.LOCKED)
    payment_list.export_file_entitlement = FileTempFactory(file="", created_by=user)
    payment_list.save()
    create_user_role_with_permissions(
        user, [Permissions.PM_VIEW_LIST], payment_list.business_area, program=payment_list.program
    )

    request = rf.get(reverse("download-payment-list", args=[payment_list.id]))
    request.user = user

    with pytest.raises(ValueError, match="Payment list entitlement export file link must not be None"):
        download_payment_list(request, str(payment_list.id))


@pytest.fixture
def group_with_export_file(user):
    cycle = ProgramCycleFactory()
    file_temp = FileTempFactory(
        file=SimpleUploadedFile("payment-list.xlsx", b"data"),
        created_by=user,
    )
    return PaymentPlanFactory(cycle=cycle, export_file_delivery=file_temp)


def test_download_payment_plan_xlsx_requires_permission(rf, group_with_export_file, user):
    group = group_with_export_file
    request = rf.get(reverse("download-payment-plan-xlsx", args=[str(group.id)]))
    request.user = user

    with pytest.raises(PermissionDenied) as excinfo:
        download_payment_plan_xlsx(request, str(group.id))

    assert excinfo.value.args[0]["required_permissions"] == [Permissions.PM_PAYMENT_PLAN_EXPORT_XLSX.value]


def test_download_payment_plan_xlsx_redirects_with_permission(
    rf,
    create_user_role_with_permissions,
    group_with_export_file,
    user,
):
    group = group_with_export_file
    create_user_role_with_permissions(
        user,
        [Permissions.PM_PAYMENT_PLAN_EXPORT_XLSX],
        group.cycle.program.business_area,
        program=group.cycle.program,
    )
    request = rf.get(reverse("download-payment-plan-xlsx", args=[str(group.id)]))
    request.user = user

    response = download_payment_plan_xlsx(request, str(group.id))

    assert response.status_code == 302
    assert response.url == group.export_file_delivery.file.url


def test_download_payment_plan_xlsx_missing_file_raises(
    rf,
    create_user_role_with_permissions,
    user,
):
    cycle = ProgramCycleFactory()
    group = PaymentPlanFactory(cycle=cycle)
    create_user_role_with_permissions(
        user,
        [Permissions.PM_PAYMENT_PLAN_EXPORT_XLSX],
        cycle.program.business_area,
        program=cycle.program,
    )
    request = rf.get(reverse("download-payment-plan-xlsx", args=[str(group.id)]))
    request.user = user

    with pytest.raises(FileNotFoundError):
        download_payment_plan_xlsx(request, str(group.id))


@pytest.fixture
def group_with_summary_pdf(user):
    group = PaymentPlanFactory(cycle=ProgramCycleFactory())
    group.export_pdf_file_summary = FileTempFactory(file=SimpleUploadedFile("summary.pdf", b"data"), created_by=user)
    group.save(update_fields=["export_pdf_file_summary"])
    return group


def test_download_payment_plan_summary_pdf_requires_permission(rf, group_with_summary_pdf, user):
    request = rf.get(reverse("download-payment-plan-summary-pdf", args=[group_with_summary_pdf.id]))
    request.user = user

    with pytest.raises(PermissionDenied) as excinfo:
        download_payment_plan_summary_pdf(request, str(group_with_summary_pdf.id))

    assert excinfo.value.args[0]["required_permissions"] == [Permissions.PM_EXPORT_PDF_SUMMARY.value]


def test_download_payment_plan_summary_pdf_redirects_with_permission(
    rf, create_user_role_with_permissions, group_with_summary_pdf, user
):
    create_user_role_with_permissions(
        user,
        [Permissions.PM_EXPORT_PDF_SUMMARY],
        group_with_summary_pdf.business_area,
        program=group_with_summary_pdf.cycle.program,
    )
    request = rf.get(reverse("download-payment-plan-summary-pdf", args=[group_with_summary_pdf.id]))
    request.user = user

    response = download_payment_plan_summary_pdf(request, str(group_with_summary_pdf.id))

    assert response.status_code == 302
    assert response.url == group_with_summary_pdf.export_pdf_file_summary.file.url


def test_download_payment_plan_summary_pdf_refuses_permission_in_other_program(
    rf, create_user_role_with_permissions, group_with_summary_pdf, user
):
    other_program = ProgramFactory(business_area=group_with_summary_pdf.business_area)
    create_user_role_with_permissions(
        user, [Permissions.PM_EXPORT_PDF_SUMMARY], other_program.business_area, program=other_program
    )
    request = rf.get(reverse("download-payment-plan-summary-pdf", args=[group_with_summary_pdf.id]))
    request.user = user

    with pytest.raises(PermissionDenied):
        download_payment_plan_summary_pdf(request, str(group_with_summary_pdf.id))


def test_download_payment_plan_summary_pdf_missing_file_raises(rf, create_user_role_with_permissions, user):
    group = PaymentPlanFactory(cycle=ProgramCycleFactory())
    create_user_role_with_permissions(
        user, [Permissions.PM_EXPORT_PDF_SUMMARY], group.business_area, program=group.cycle.program
    )
    request = rf.get(reverse("download-payment-plan-summary-pdf", args=[group.id]))
    request.user = user

    with pytest.raises(FileNotFoundError):
        download_payment_plan_summary_pdf(request, str(group.id))


@pytest.fixture
def instruction_with_summary_pdf(user):
    instruction = FollowUpInstructionFactory()
    instruction.export_pdf_file_summary = FileTempFactory(
        file=SimpleUploadedFile("summary.pdf", b"data"), created_by=user
    )
    instruction.save(update_fields=["export_pdf_file_summary"])
    return instruction


def test_download_follow_up_instruction_summary_pdf_requires_permission(rf, instruction_with_summary_pdf, user):
    request = rf.get(reverse("download-follow-up-instruction-summary-pdf", args=[instruction_with_summary_pdf.id]))
    request.user = user

    with pytest.raises(PermissionDenied) as excinfo:
        download_follow_up_instruction_summary_pdf(request, str(instruction_with_summary_pdf.id))

    assert excinfo.value.args[0]["required_permissions"] == [Permissions.PM_EXPORT_PDF_SUMMARY.value]


def test_download_follow_up_instruction_summary_pdf_redirects_with_permission(
    rf, create_user_role_with_permissions, instruction_with_summary_pdf, user
):
    create_user_role_with_permissions(
        user,
        [Permissions.PM_EXPORT_PDF_SUMMARY],
        instruction_with_summary_pdf.business_area,
        program=instruction_with_summary_pdf.program,
    )
    request = rf.get(reverse("download-follow-up-instruction-summary-pdf", args=[instruction_with_summary_pdf.id]))
    request.user = user

    response = download_follow_up_instruction_summary_pdf(request, str(instruction_with_summary_pdf.id))

    assert response.status_code == 302
    assert response.url == instruction_with_summary_pdf.export_pdf_file_summary.file.url


def test_download_follow_up_instruction_summary_pdf_refuses_permission_in_other_program(
    rf, create_user_role_with_permissions, instruction_with_summary_pdf, user
):
    other_program = ProgramFactory(business_area=instruction_with_summary_pdf.business_area)
    create_user_role_with_permissions(
        user, [Permissions.PM_EXPORT_PDF_SUMMARY], other_program.business_area, program=other_program
    )
    request = rf.get(reverse("download-follow-up-instruction-summary-pdf", args=[instruction_with_summary_pdf.id]))
    request.user = user

    with pytest.raises(PermissionDenied):
        download_follow_up_instruction_summary_pdf(request, str(instruction_with_summary_pdf.id))


@pytest.fixture
def instruction_without_summary_pdf():
    return FollowUpInstructionFactory()


def test_download_follow_up_instruction_summary_pdf_missing_file_raises(
    rf, create_user_role_with_permissions, instruction_without_summary_pdf, user
):
    create_user_role_with_permissions(
        user,
        [Permissions.PM_EXPORT_PDF_SUMMARY],
        instruction_without_summary_pdf.business_area,
        program=instruction_without_summary_pdf.program,
    )
    request = rf.get(reverse("download-follow-up-instruction-summary-pdf", args=[instruction_without_summary_pdf.id]))
    request.user = user

    with pytest.raises(FileNotFoundError):
        download_follow_up_instruction_summary_pdf(request, str(instruction_without_summary_pdf.id))


@pytest.fixture
def instruction_with_export_file(user):
    instruction = FollowUpInstructionFactory()
    instruction.export_file = FileTempFactory(file=SimpleUploadedFile("payment-list.xlsx", b"data"), created_by=user)
    instruction.save(update_fields=["export_file"])
    return instruction


def test_download_follow_up_instruction_xlsx_requires_permission(rf, instruction_with_export_file, user):
    request = rf.get(reverse("download-follow-up-instruction-xlsx", args=[instruction_with_export_file.id]))
    request.user = user

    with pytest.raises(PermissionDenied) as excinfo:
        download_follow_up_instruction_xlsx(request, str(instruction_with_export_file.id))

    assert excinfo.value.args[0]["required_permissions"] == [Permissions.PM_PAYMENT_PLAN_EXPORT_XLSX.value]


def test_download_follow_up_instruction_xlsx_redirects_with_permission(
    rf, create_user_role_with_permissions, instruction_with_export_file, user
):
    create_user_role_with_permissions(
        user,
        [Permissions.PM_PAYMENT_PLAN_EXPORT_XLSX],
        instruction_with_export_file.business_area,
        program=instruction_with_export_file.program,
    )
    request = rf.get(reverse("download-follow-up-instruction-xlsx", args=[instruction_with_export_file.id]))
    request.user = user

    response = download_follow_up_instruction_xlsx(request, str(instruction_with_export_file.id))

    assert response.status_code == 302
    assert response.url == instruction_with_export_file.export_file.file.url


def test_download_follow_up_instruction_xlsx_missing_file_raises(rf, create_user_role_with_permissions, user):
    instruction = FollowUpInstructionFactory()
    create_user_role_with_permissions(
        user,
        [Permissions.PM_PAYMENT_PLAN_EXPORT_XLSX],
        instruction.business_area,
        program=instruction.program,
    )
    request = rf.get(reverse("download-follow-up-instruction-xlsx", args=[instruction.id]))
    request.user = user

    with pytest.raises(FileNotFoundError):
        download_follow_up_instruction_xlsx(request, str(instruction.id))
