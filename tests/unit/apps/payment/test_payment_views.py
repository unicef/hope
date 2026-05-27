from unittest.mock import PropertyMock, patch

from django.contrib.contenttypes.models import ContentType
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
    download_payment_verification_plan,
)
from hope.models import PaymentPlan, PaymentVerificationPlan

pytestmark = pytest.mark.django_db


@pytest.fixture
def user():
    return UserFactory()


@pytest.fixture
def payment_plan_locked():
    return PaymentPlanFactory(status=PaymentPlan.Status.LOCKED)


@pytest.fixture
def payment_plan_accepted():
    return PaymentPlanFactory(status=PaymentPlan.Status.ACCEPTED)


@pytest.fixture
def payment_plan_with_export_file(payment_plan_locked, user):
    export_file = FileTempFactory(
        file=SimpleUploadedFile("payment-list.xlsx", b"data"),
        created_by=user,
    )
    payment_plan_locked.export_file_entitlement = export_file
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
        payment_verification_plan.payment_plan.business_area,
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


def test_download_payment_plan_payment_list_raises_value_error_when_link_is_none(
    rf,
    create_user_role_with_permissions,
    payment_plan_with_export_file,
    user,
):
    create_user_role_with_permissions(
        user,
        [Permissions.PM_VIEW_LIST],
        payment_plan_with_export_file.business_area,
    )

    request = rf.get(reverse("download-payment-plan-payment-list", args=[payment_plan_with_export_file.id]))
    request.user = user

    with patch(
        "hope.models.PaymentPlan.payment_list_export_file_link",
        new_callable=PropertyMock,
        return_value=None,
    ):
        with pytest.raises(ValueError, match="Payment plan export file link must not be None"):
            download_payment_plan_payment_list(request, str(payment_plan_with_export_file.id))
