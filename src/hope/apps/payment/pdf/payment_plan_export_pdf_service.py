import logging
from typing import Any

from django.conf import settings
from django.db.models import Count, Q, Sum
from django.urls import reverse

from hope.apps.core.utils import encode_id_base64
from hope.models import Approval, Payment, PaymentPlan
from hope.apps.utils.pdf_generator import generate_pdf_from_html


logger = logging.getLogger(__name__)


class PaymentPlanPDFExportService:
    text_template = "payment/pdf_file_generated_email.txt"
    html_template = "payment/pdf_file_generated_email.html"

    def __init__(self, payment_plan: PaymentPlan):
        self.payment_plan = payment_plan
        self.download_link: str = ""
        self.payment_plan_link: str = ""
        self.is_social_worker_program = payment_plan.program.is_social_worker_program

    @staticmethod
    def get_link(api_url: str | None = None) -> str:
        protocol = "https" if settings.SOCIAL_AUTH_REDIRECT_IS_HTTPS else "http"
        link = f"{protocol}://{settings.FRONTEND_HOST}{api_url}"
        if api_url:
            return link
        return ""

    def generate_web_links(self) -> None:
        payment_plan_id = encode_id_base64(self.payment_plan.id, "PaymentPlan")
        program_id = encode_id_base64(self.payment_plan.program.id, "Program")
        path_name = "download-payment-plan-summary-pdf"
        self.download_link = self.get_link(reverse(path_name, args=[payment_plan_id]))
        self.payment_plan_link = self.get_link(
            f"/{self.payment_plan.business_area.slug}/programs/{program_id}/payment-module/payment-plans/{str(payment_plan_id)}"
        )

    def get_email_context(self, user: "User") -> dict:
        msg = "Payment Plan Summary PDF file(s) have been generated, and below you will find the link to download the file(s)."

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
        if self.is_social_worker_program:
            template_name = "payment/people_payment_plan_summary_pdf_template.html"
        else:
            template_name = "payment/payment_plan_summary_pdf_template.html"
        filename = f"PaymentPlanSummary-{self.payment_plan.unicef_id}.pdf"
        fsp = self.payment_plan.financial_service_provider
        delivery_mechanism = self.payment_plan.delivery_mechanism

        approval_process = self.payment_plan.approval_process.first()
        approval = approval_process.approvals.filter(type=Approval.APPROVAL).first()
        authorization = approval_process.approvals.filter(type=Approval.AUTHORIZATION).first()
        release = approval_process.approvals.filter(type=Approval.FINANCE_RELEASE).first()

        reconciliation_qs = self.payment_plan.eligible_payments.aggregate(
            pending=Count("id", filter=Q(status__in=Payment.PENDING_STATUSES)),
            pending_usd=Sum(
                "entitlement_quantity_usd",
                filter=Q(status__in=Payment.PENDING_STATUSES),
            ),
            pending_local=Sum("entitlement_quantity", filter=Q(status__in=Payment.PENDING_STATUSES)),
            reconciled=Count("id", filter=~Q(status__in=Payment.PENDING_STATUSES)),
            reconciled_usd=Sum("delivered_quantity_usd", filter=~Q(status__in=Payment.PENDING_STATUSES)),
            reconciled_local=Sum("delivered_quantity", filter=~Q(status__in=Payment.PENDING_STATUSES)),
        )

        pdf_context_data = {
            "title": self.payment_plan.unicef_id,
            "payment_plan": self.payment_plan,
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
