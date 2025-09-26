import logging
from typing import TYPE_CHECKING, Any

from django.db.models import Count, F, Q, Sum
from django.urls import reverse

from hope.apps.core.utils import encode_id_base64
from hope.apps.payment.models import Approval, Payment, PaymentPlan
from hope.apps.payment.utils import get_link
from hope.apps.utils.pdf_generator import generate_pdf_from_html

if TYPE_CHECKING:
    from hope.apps.account.models import User


logger = logging.getLogger(__name__)


class PaymentPlanPDFExportService:
    text_template = "payment/pdf_file_generated_email.txt"
    html_template = "payment/pdf_file_generated_email.html"

    def __init__(self, payment_plan: PaymentPlan):
        self.payment_plan = payment_plan
        self.download_link: str = ""
        self.payment_plan_link: str = ""
        self.is_social_worker_program = payment_plan.program.is_social_worker_program

    def generate_web_links(self) -> None:
        payment_plan_id = encode_id_base64(self.payment_plan.id, "PaymentPlan")
        program_id = encode_id_base64(self.payment_plan.program.id, "Program")
        path_name = "download-payment-plan-summary-pdf"
        self.download_link = get_link(reverse(path_name, args=[payment_plan_id]))
        self.payment_plan_link = get_link(
            f"/{self.payment_plan.business_area.slug}/programs/{program_id}/payment-module/payment-plans/{str(payment_plan_id)}"
        )

    def get_email_context(self, user: "User") -> dict:
        msg = (
            "Payment Plan Summary PDF file(s) have been generated, "
            "and below you will find the link to download the file(s)."
        )

        return {
            "first_name": getattr(user, "first_name", ""),
            "last_name": getattr(user, "last_name", ""),
            "email": getattr(user, "email", ""),
            "message": msg,
            "link": self.download_link,
            "title": "Payment Plan Payment List files generated",
        }

    def generate_pdf_summary(self) -> Any:
        self.generate_web_links()
        template_name = "payment/payment_plan_summary_pdf_template.html"
        filename = f"PaymentPlanSummary-{self.payment_plan.unicef_id}.pdf"
        fsp = self.payment_plan.financial_service_provider
        delivery_mechanism = self.payment_plan.delivery_mechanism

        approval_process = self.payment_plan.approval_process.first()
        approval = approval_process.approvals.filter(type=Approval.APPROVAL).first()
        authorization = approval_process.approvals.filter(type=Approval.AUTHORIZATION).first()
        release = approval_process.approvals.filter(type=Approval.FINANCE_RELEASE).first()

        failed_base = Q(status__in=Payment.FAILED_STATUSES + Payment.NOT_DELIVERED_STATUSES)
        failed_partial_qs = self.payment_plan.eligible_payments.filter(status=Payment.STATUS_DISTRIBUTION_PARTIAL)
        failed_partial_local = (
            failed_partial_qs.aggregate(total=Sum(F("entitlement_quantity") - F("delivered_quantity")))["total"] or 0
        )
        failed_partial_usd = (
            failed_partial_qs.aggregate(total=Sum(F("entitlement_quantity_usd") - F("delivered_quantity_usd")))["total"]
            or 0
        )

        reconciliation_qs = self.payment_plan.eligible_payments.aggregate(
            pending=Count("id", filter=Q(status__in=Payment.PENDING_STATUSES)),
            reconciled=Count("id", filter=Q(status__in=Payment.DELIVERED_STATUSES)),  # Redeemed
            reconciled_usd=Sum("delivered_quantity_usd", filter=Q(status__in=Payment.DELIVERED_STATUSES)),
            reconciled_local=Sum("delivered_quantity", filter=Q(status__in=Payment.DELIVERED_STATUSES)),
            failed_usd=Sum("entitlement_quantity_usd", filter=failed_base),
            failed_local=Sum("entitlement_quantity", filter=failed_base),
        )

        # Normalize None → 0
        for key in ["reconciled_usd", "reconciled_local", "failed_usd", "failed_local"]:
            reconciliation_qs[key] = reconciliation_qs[key] or 0

        # Add partials in Python (cannot mix inside aggregate)
        reconciliation_qs["failed_usd"] += failed_partial_usd
        reconciliation_qs["failed_local"] += failed_partial_local

        pdf_context_data = {
            "title": self.payment_plan.unicef_id,
            "payment_plan": self.payment_plan,
            "is_social_worker_program": self.is_social_worker_program,
            "fsp": fsp,
            "delivery_mechanism_per_payment_plan": delivery_mechanism,
            "approval_process": self.payment_plan.approval_process.first(),
            "payment_plan_link": self.payment_plan_link,
            "approval": approval,
            "authorization": authorization,
            "release": release,
            "reconciliation": reconciliation_qs,
        }

        pdf = generate_pdf_from_html(
            template_name=template_name,
            data=pdf_context_data,
        )
        return pdf, filename
