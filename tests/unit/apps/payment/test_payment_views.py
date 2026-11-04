from unittest.mock import PropertyMock, patch

from django.contrib.contenttypes.models import ContentType
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
import pytest

from extras.test_utils.factories import (
    FileTempFactory,
    PaymentListFactory,
    PaymentVerificationPlanFactory,
    PaymentVerificationSummaryFactory,
    UserFactory,
)
from hope.apps.account.permissions import Permissions
from hope.apps.payment.views import (
    download_payment_list,
    download_payment_verification_plan,
)
from hope.models import PaymentList, PaymentVerificationPlan

pytestmark = pytest.mark.django_db


@pytest.fixture
def user():
    return UserFactory()


@pytest.fixture
def payment_list_locked():
    return PaymentListFactory(status=PaymentList.Status.LOCKED)


@pytest.fixture
def payment_list_accepted():
    return PaymentListFactory(status=PaymentList.Status.ACCEPTED)


@pytest.fixture
def payment_list_with_export_file(payment_list_locked, user):
    export_file = FileTempFactory(
        file=SimpleUploadedFile("payment-list.xlsx", b"data"),
        created_by=user,
    )
    payment_list_locked.export_file_entitlement = export_file
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


def test_download_payment_verification_plan_raises_value_error_when_link_is_none(
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

    with patch(
        "hope.models.PaymentVerificationPlan.xlsx_payment_verification_plan_file_link",
        new_callable=PropertyMock,
        return_value=None,
    ):
        with pytest.raises(ValueError, match="Payment verification plan XLSX file link must not be None"):
            download_payment_verification_plan(request, str(payment_verification_plan.id))


def test_download_payment_list_raises_value_error_when_link_is_none(
    rf,
    create_user_role_with_permissions,
    payment_list_with_export_file,
    user,
):
    create_user_role_with_permissions(
        user,
        [Permissions.PM_VIEW_LIST],
        payment_list_with_export_file.business_area,
        program=payment_list_with_export_file.program,
    )

    request = rf.get(reverse("download-payment-list", args=[payment_list_with_export_file.id]))
    request.user = user

    with patch(
        "hope.models.PaymentList.entitlement_export_file_link",
        new_callable=PropertyMock,
        return_value=None,
    ):
        with pytest.raises(ValueError, match="Payment list entitlement export file link must not be None"):
            download_payment_list(request, str(payment_list_with_export_file.id))
