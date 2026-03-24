from datetime import datetime
import io
from pathlib import Path
from typing import Any
from unittest import mock

from django.urls import reverse
import openpyxl
import pytest

from extras.test_utils.factories import (
    BusinessAreaFactory,
    FundsCommitmentGroupFactory,
    FundsCommitmentItemFactory,
    PartnerFactory,
    PaymentFactory,
    PaymentPlanFactory,
    ProgramCycleFactory,
    ProgramFactory,
    RoleAssignmentFactory,
    RoleFactory,
    UserFactory,
)
from hope.apps.account.permissions import Permissions
from hope.apps.payment.services.qcf_reports_service import QCFReportsService
from hope.apps.payment.services.western_union_ftp import WesternUnionFTPClient
from hope.apps.payment.utils import get_link
from hope.models import (
    PaymentPlan,
    Program,
    User,
    WesternUnionInvoice,
    WesternUnionInvoicePayment,
    WesternUnionPaymentPlanReport,
)

pytestmark = pytest.mark.django_db


class WUClientMock(WesternUnionFTPClient):
    HOST = "fakehost"
    PORT = 2222
    USERNAME = "user"
    PASSWORD = "pass"

    def __init__(self) -> None:
        self.client = mock.MagicMock()  # type: ignore


@pytest.fixture
def business_area() -> Any:
    return BusinessAreaFactory(slug="afghanistan")


@pytest.fixture
def user_and_role(business_area: Any) -> dict[str, Any]:
    partner_unicef = PartnerFactory(name="UNICEF")
    partner_unicef_hq = PartnerFactory(name="UNICEF HQ", parent=partner_unicef)
    user = UserFactory(partner=partner_unicef_hq)
    role = RoleFactory(
        name="RECEIVE_PARSED_WU_QCF",
        permissions=[Permissions.RECEIVE_PARSED_WU_QCF.value],
    )
    role_assignment = RoleAssignmentFactory(user=user, role=role, business_area=business_area)
    return {
        "user": user,
        "role_assignment": role_assignment,
    }


@pytest.fixture
def program_active(business_area: Any) -> Program:
    return ProgramFactory(status=Program.ACTIVE, business_area=business_area)


@pytest.fixture
def cycle(program_active: Program) -> Any:
    return ProgramCycleFactory(program=program_active, title="Cycle QCF")


@pytest.fixture
def qcf_context(
    business_area: Any,
    program_active: Program,
    cycle: Any,
    user_and_role: dict[str, Any],
) -> dict[str, Any]:
    payment_plan = PaymentPlanFactory(
        program_cycle=cycle,
        created_by=user_and_role["user"],
        status=PaymentPlan.Status.ACCEPTED,
        business_area=business_area,
    )

    fcg1 = FundsCommitmentGroupFactory(funds_commitment_number="1")
    FundsCommitmentItemFactory(
        funds_commitment_group=fcg1,
        office=None,
        rec_serial_number=1,
        funds_commitment_item="001",
        payment_plan=payment_plan,
    )
    fcg2 = FundsCommitmentGroupFactory(funds_commitment_number="2")
    FundsCommitmentItemFactory(
        funds_commitment_group=fcg2,
        office=None,
        rec_serial_number=2,
        funds_commitment_item="002",
        payment_plan=payment_plan,
    )

    p1 = PaymentFactory(parent=payment_plan, fsp_auth_code="0486455966", program=program_active)
    p2 = PaymentFactory(parent=payment_plan, fsp_auth_code="669", program=program_active)
    p3 = PaymentFactory(parent=payment_plan, fsp_auth_code=None, program=program_active)

    p1.unicef_id = "RCPT-0520-25-0.000.145"
    p1.save(update_fields=["unicef_id"])
    p2.unicef_id = "RCPT-0520-25-0.000.144"
    p2.save(update_fields=["unicef_id"])
    p3.unicef_id = "RCPT-0520-25-0.000.135"
    p3.save(update_fields=["unicef_id"])

    return {
        "payment_plan": payment_plan,
        "program": program_active,
        "p1": p1,
        "p2": p2,
        "p3": p3,
        "user": user_and_role["user"],
        "role_assignment": user_and_role["role_assignment"],
    }


@mock.patch(
    "hope.apps.payment.services.qcf_reports_service.WesternUnionFTPClient",
    WUClientMock,
)
def test_process_files_since_with_real_zip(
    qcf_context: dict[str, Any],
    client: Any,
) -> None:
    filename = "QCF-123-XYZ-20250101.zip"
    ad_filename = "AD-123-XYZ-20250101.zip"
    test_file_path = Path(__file__).parent / "test_file" / filename
    ad_test_file_path = Path(__file__).parent / "test_file" / ad_filename

    fake_file_like = io.BytesIO(test_file_path.read_bytes())
    ad_fake_file_like = io.BytesIO(ad_test_file_path.read_bytes())

    with (
        mock.patch.object(
            WesternUnionFTPClient,
            "get_files_since",
            return_value=[(filename, fake_file_like)],
        ),
        mock.patch.object(
            WesternUnionFTPClient,
            "get_files_by_name",
            return_value=[(ad_filename, ad_fake_file_like)],
        ),
    ):
        service = QCFReportsService()
        service.process_files_since(datetime(2025, 1, 1))

        assert WesternUnionInvoice.objects.count() == 1
        qcf_file = WesternUnionInvoice.objects.first()
        assert qcf_file.name == filename
        assert WesternUnionInvoice.objects.count() == 1
        assert str(qcf_file) == qcf_file.name

        assert WesternUnionInvoicePayment.objects.filter(transaction_status="2").count() == 3

        assert WesternUnionPaymentPlanReport.objects.count() == 1
        report = WesternUnionPaymentPlanReport.objects.first()
        assert report.qcf_file == qcf_file
        assert report.payment_plan == qcf_context["payment_plan"]
        assert str(report) == f"{report.payment_plan.name} - sent: {report.sent}"

        report_file = report.report_file
        assert report_file is not None

        file_field = report_file.file
        file_field.open("rb")
        wb = openpyxl.load_workbook(file_field)
        ws = wb.active

        assert ws.title == f"QCF Report - {report.payment_plan.unicef_id}"

        expected_headers = [
            "Payment ID",
            "MTCN",
            "MTCNs match",
            "HOPE MTCN",
            "Payment Plan ID",
            "Programme",
            "FC",
            "Principal Amount",
            "Charges Amount",
            "Fee Amount",
            "Advice Filename",
        ]
        actual_headers = [cell.value for cell in ws[1]]
        assert actual_headers == expected_headers

        row_values = [cell.value for cell in ws[2]]
        assert row_values == [
            qcf_context["p1"].unicef_id,
            "0486455966",
            True,
            "0486455966",
            qcf_context["p1"].parent.unicef_id,
            qcf_context["program"].name,
            "1/001, 2/002",
            262.55,
            7.88,
            0,
            "ADVCP_E_C_0007_PIIC_25911592304_18_NOV_2025",
        ]

        row_values = [cell.value for cell in ws[3]]
        assert row_values == [
            qcf_context["p2"].unicef_id,
            "1131933875",
            False,
            "669",
            qcf_context["p2"].parent.unicef_id,
            qcf_context["program"].name,
            "1/001, 2/002",
            262.55,
            7.88,
            0,
            "ADVCP_E_C_0007_PIIC_25911592304_18_NOV_2025",
        ]

        row_values = [cell.value for cell in ws[4]]
        assert row_values == [
            qcf_context["p3"].unicef_id,
            "1389434830",
            False,
            None,
            qcf_context["p3"].parent.unicef_id,
            qcf_context["program"].name,
            "1/001, 2/002",
            665.22,
            19.96,
            0,
            "ADVCP_E_C_0007_PIIC_25911592304_18_NOV_2025",
        ]

        last_row = ws.max_row
        principal_total = ws[f"E{last_row - 2}"].value
        charges_total = ws[f"E{last_row - 1}"].value
        refunds_total = ws[f"E{last_row}"].value

        assert principal_total == 1190.32
        assert charges_total == 35.72
        assert refunds_total == 0

        with mock.patch.object(User, "email_user") as mock_email_user:
            with mock.patch("hope.apps.payment.services.qcf_reports_service.render_to_string") as mock_render_to_string:
                service.send_notification_emails(report)  # type: ignore
                mock_email_user.assert_called_once()
                assert mock_render_to_string.call_count == 2
                args, kwargs = mock_render_to_string.call_args
                context = kwargs["context"]
                program_slug = report.payment_plan.program.slug
                payment_plan_id = report.payment_plan.id
                plan_path = (
                    f"/{report.payment_plan.business_area.slug}/"
                    f"programs/{program_slug}/payment-module/payment-plans/{payment_plan_id}"
                )
                plan_link = get_link(plan_path)
                report_link = get_link(
                    reverse(
                        "download-payment-plan-invoice-report-pdf",
                        args=[report.id],
                    )
                )

                assert context == {
                    "first_name": getattr(qcf_context["user"], "first_name", ""),
                    "last_name": getattr(qcf_context["user"], "last_name", ""),
                    "email": getattr(qcf_context["user"], "email", ""),
                    "message": f"Payment Plan: {plan_link}",
                    "title": f"Payment Plan {report.report_file.file.name} Western Union QCF Report",
                    "link": f"Western Union QCF Report file: {report_link}",
                }

        download_link = reverse(
            "download-payment-plan-invoice-report-pdf",
            args=[report.id],
        )

        client.force_login(qcf_context["user"], "django.contrib.auth.backends.ModelBackend")
        response = client.get(download_link)
        assert response.status_code == 302
        assert f"/api/uploads/{report.report_file.file.name}" in response.url

        qcf_context["role_assignment"].delete()
        client.force_login(qcf_context["user"], "django.contrib.auth.backends.ModelBackend")
        response = client.get(download_link)
        assert response.status_code == 403
