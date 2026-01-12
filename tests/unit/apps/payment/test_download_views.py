from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
import pytest

from extras.test_utils.factories.account import BusinessAreaFactory, UserFactory
from extras.test_utils.factories.payment import (
    PaymentPlanFactory,
    PaymentVerificationPlanFactory,
    PaymentVerificationSummaryFactory,
)
from hope.apps.account.permissions import Permissions
from hope.apps.payment.views import (
    download_payment_plan_payment_list,
    download_payment_plan_summary_pdf,
    download_payment_verification_plan,
)
from hope.models import PaymentPlan, PaymentVerificationPlan
from hope.models.file_temp import FileTemp

pytestmark = pytest.mark.django_db


class TestDownloadPaymentViews:
    def test_download_payment_verification_plan_requires_permission(self, rf):
        BusinessAreaFactory()
        payment_plan = PaymentPlanFactory()
        PaymentVerificationSummaryFactory(payment_plan=payment_plan)
        pvp = PaymentVerificationPlanFactory(payment_plan=payment_plan)
        user = UserFactory()

        request = rf.get(reverse("download-payment-verification-plan", args=[pvp.id]))
        request.user = user

        with pytest.raises(PermissionDenied) as excinfo:
            download_payment_verification_plan(request, str(pvp.id))

        assert excinfo.value.args[0]["required_permissions"] == [Permissions.PAYMENT_VERIFICATION_EXPORT.value]

    def test_download_payment_verification_plan_redirects_with_permission(self, rf, create_user_role_with_permissions):
        BusinessAreaFactory()
        payment_plan = PaymentPlanFactory()
        PaymentVerificationSummaryFactory(payment_plan=payment_plan)
        pvp = PaymentVerificationPlanFactory(
            payment_plan=payment_plan, verification_channel=PaymentVerificationPlan.VERIFICATION_CHANNEL_XLSX
        )
        user = UserFactory()
        create_user_role_with_permissions(
            user, [Permissions.PAYMENT_VERIFICATION_EXPORT], pvp.payment_plan.business_area
        )

        filetemp = FileTemp.objects.create(
            object_id=pvp.pk,
            content_type=ContentType.objects.get_for_model(PaymentVerificationPlan),
            created_by=user,
            file=SimpleUploadedFile("verification.xlsx", b"data"),
        )

        request = rf.get(reverse("download-payment-verification-plan", args=[pvp.id]))
        request.user = user

        response = download_payment_verification_plan(request, str(pvp.id))

        assert response.status_code == 302
        assert response.url == filetemp.file.url
        filetemp.refresh_from_db()
        assert filetemp.was_downloaded is True

    def test_download_payment_plan_payment_list_requires_permission(self, rf):
        ba = BusinessAreaFactory()
        payment_plan = PaymentPlanFactory(business_area=ba, status=PaymentPlan.Status.LOCKED)
        user = UserFactory()

        request = rf.get(reverse("download-payment-plan-payment-list", args=[payment_plan.id]))
        request.user = user

        with pytest.raises(PermissionDenied) as excinfo:
            download_payment_plan_payment_list(request, str(payment_plan.id))

        assert excinfo.value.args[0]["required_permissions"] == [Permissions.PM_VIEW_LIST.value]

    def test_download_payment_plan_payment_list_redirects_with_permission(self, rf, create_user_role_with_permissions):
        ba = BusinessAreaFactory()
        payment_plan = PaymentPlanFactory(business_area=ba, status=PaymentPlan.Status.LOCKED)
        user = UserFactory()
        create_user_role_with_permissions(user, [Permissions.PM_VIEW_LIST], ba)

        payment_plan.export_file_entitlement = FileTemp.objects.create(
            file=SimpleUploadedFile("payment-list.xlsx", b"data"),
            created_by=user,
        )
        payment_plan.save()

        request = rf.get(reverse("download-payment-plan-payment-list", args=[payment_plan.id]))
        request.user = user

        response = download_payment_plan_payment_list(request, str(payment_plan.id))

        assert response.status_code == 302
        assert response.url == payment_plan.payment_list_export_file_link

    def test_download_payment_plan_summary_pdf_requires_permission(self, rf):
        ba = BusinessAreaFactory()
        payment_plan = PaymentPlanFactory(business_area=ba, status=PaymentPlan.Status.IN_REVIEW)
        user = UserFactory()

        request = rf.get(reverse("download-payment-plan-summary-pdf", args=[payment_plan.id]))
        request.user = user

        with pytest.raises(PermissionDenied) as excinfo:
            download_payment_plan_summary_pdf(request, str(payment_plan.id))

        assert excinfo.value.args[0]["required_permissions"] == [Permissions.PM_EXPORT_PDF_SUMMARY.value]

    def test_download_payment_plan_summary_pdf_redirects_with_permission(self, rf, create_user_role_with_permissions):
        ba = BusinessAreaFactory()
        payment_plan = PaymentPlanFactory(business_area=ba, status=PaymentPlan.Status.ACCEPTED)
        user = UserFactory()
        create_user_role_with_permissions(user, [Permissions.PM_EXPORT_PDF_SUMMARY], ba)

        payment_plan.export_pdf_file_summary = FileTemp.objects.create(
            file=SimpleUploadedFile("summary.pdf", b"data"),
            created_by=user,
        )
        payment_plan.save()

        request = rf.get(reverse("download-payment-plan-summary-pdf", args=[payment_plan.id]))
        request.user = user

        response = download_payment_plan_summary_pdf(request, str(payment_plan.id))

        assert response.status_code == 302
        assert response.url == payment_plan.export_pdf_file_summary.file.url
