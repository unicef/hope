import logging
from typing import TYPE_CHECKING

from django.db.models import Count, F, Q, Sum
from django.urls import reverse

from hope.apps.payment.utils import get_link
from hope.apps.utils.pdf_generator import generate_pdf_from_html
from hope.models import Approval, ApprovalProcess, Payment, PaymentPlan, PaymentPlanGroup

if TYPE_CHECKING:
    from django.db.models import QuerySet

    from hope.models import User

logger = logging.getLogger(__name__)


def reconciliation_summary(payments: "QuerySet[Payment]") -> dict:
    """Count and sum redeemed / pending payments; a partial delivery counts its remainder as unredeemed."""
    failed_base = Q(status__in=Payment.FAILED_STATUSES + Payment.NOT_DELIVERED_STATUSES)
    failed_partial_qs = payments.filter(status=Payment.STATUS_DISTRIBUTION_PARTIAL)
    failed_partial_local = (
        failed_partial_qs.aggregate(total=Sum(F("entitlement_quantity") - F("delivered_quantity")))["total"] or 0
    )
    failed_partial_usd = (
        failed_partial_qs.aggregate(total=Sum(F("entitlement_quantity_usd") - F("delivered_quantity_usd")))["total"]
        or 0
    )

    summary = payments.aggregate(
        pending=Count("id", filter=Q(status__in=Payment.PENDING_STATUSES)),
        reconciled=Count("id", filter=Q(status__in=Payment.DELIVERED_STATUSES)),  # Redeemed
        reconciled_usd=Sum("delivered_quantity_usd", filter=Q(status__in=Payment.DELIVERED_STATUSES)),
        reconciled_local=Sum("delivered_quantity", filter=Q(status__in=Payment.DELIVERED_STATUSES)),
        failed_usd=Sum("entitlement_quantity_usd", filter=failed_base),
        failed_local=Sum("entitlement_quantity", filter=failed_base),
    )
    for key in ["reconciled_usd", "reconciled_local", "failed_usd", "failed_local"]:
        summary[key] = summary[key] or 0
    # Partials are added here: an aggregate cannot mix the two expressions.
    summary["failed_usd"] += failed_partial_usd
    summary["failed_local"] += failed_partial_local
    return summary


def approval_chain(approval_process: ApprovalProcess | None) -> dict:
    """Return the approve / authorize / release approvals of a process, each possibly None."""
    approvals = approval_process.approvals if approval_process else Approval.objects.none()
    return {
        "approval": approvals.filter(type=Approval.APPROVAL).first(),
        "authorization": approvals.filter(type=Approval.AUTHORIZATION).first(),
        "release": approvals.filter(type=Approval.FINANCE_RELEASE).first(),
    }


class PaymentPlanPDFExportService:
    text_template = "payment/pdf_file_generated_email.txt"
    html_template = "payment/pdf_file_generated_email.html"

    def __init__(self, payment_plan: PaymentPlan):
        self.payment_plan = payment_plan
        self.download_link: str = ""
        self.payment_plan_link: str = ""
        self.is_social_worker_program = payment_plan.program.is_social_worker_program

    def generate_web_links(self) -> None:
        payment_plan_id = str(self.payment_plan.id)
        program_code = self.payment_plan.program.code
        path_name = "download-payment-plan-summary-pdf"
        self.download_link = get_link(reverse(path_name, args=[payment_plan_id]))
        self.payment_plan_link = get_link(
            f"/{self.payment_plan.business_area.slug}/programs/{program_code}/payment-module/payment-plans/{payment_plan_id}"
        )

    def get_email_context(self, user: "User") -> dict:
        msg = (
            "Payment Plan Summary PDF file(s) have been generated, "
            "and below you will find the link to download the file(s)."
        )

        return {
            "first_name": getattr(user, "first_name", "") or getattr(user, "username", ""),
            "last_name": getattr(user, "last_name", ""),
            "email": getattr(user, "email", ""),
            "message": msg,
            "link": self.download_link,
            "title": "Payment Plan Payment List files generated",
        }

    def generate_pdf_summary(self) -> tuple[bytes, str]:
        self.generate_web_links()
        template_name = "payment/payment_plan_summary_pdf_template.html"
        filename = f"PaymentPlanSummary-{self.payment_plan.unicef_id}.pdf"
        fsp = self.payment_plan.financial_service_provider
        delivery_mechanism = self.payment_plan.delivery_mechanism

        approval_process = self.payment_plan.last_approval_process

        pdf_context_data = {
            "title": self.payment_plan.unicef_id,
            "payment_plan": self.payment_plan,
            "is_social_worker_program": self.is_social_worker_program,
            "fsp": fsp,
            "delivery_mechanism_per_payment_plan": delivery_mechanism,
            "approval_process": approval_process,
            "payment_plan_link": self.payment_plan_link,
            **approval_chain(approval_process),
            "reconciliation": reconciliation_summary(self.payment_plan.eligible_payments),
        }

        pdf = generate_pdf_from_html(
            template_name=template_name,
            data=pdf_context_data,
        )
        return pdf, filename


class PaymentPlanGroupPDFExportService:
    text_template = "payment/pdf_file_generated_email.txt"
    html_template = "payment/pdf_file_generated_email.html"

    def __init__(self, payment_plan_group: PaymentPlanGroup):
        self.payment_plan_group = payment_plan_group
        self.download_link: str = ""
        self.payment_plan_group_link: str = ""
        self.is_social_worker_program = payment_plan_group.program.is_social_worker_program

    def generate_web_links(self) -> None:
        group_id = str(self.payment_plan_group.id)
        program_code = self.payment_plan_group.program.code
        self.download_link = get_link(reverse("download-payment-plan-group-summary-pdf", args=[group_id]))
        self.payment_plan_group_link = get_link(
            f"/{self.payment_plan_group.business_area.slug}/programs/{program_code}/payment-module/groups/{group_id}"
        )

    def get_email_context(self, user: "User") -> dict:
        return {
            "first_name": getattr(user, "first_name", "") or getattr(user, "username", ""),
            "last_name": getattr(user, "last_name", ""),
            "email": getattr(user, "email", ""),
            "message": (
                "Payment Plan Group Summary PDF file has been generated, "
                "and below you will find the link to download the file."
            ),
            "link": self.download_link,
            "title": "Payment Plan Group Summary file generated",
        }

    def generate_pdf_summary(self) -> tuple[bytes, str]:
        self.generate_web_links()
        group = self.payment_plan_group
        payment_plans = list(group.payment_plans.select_related("delivery_mechanism").order_by("unicef_id"))
        totals = group.payment_plans.aggregate(
            households=Sum("total_households_count"),
            individuals=Sum("total_individuals_count"),
            entitled=Sum("total_entitled_quantity"),
            entitled_usd=Sum("total_entitled_quantity_usd"),
        )
        approval_process = group.approval_process.first()
        pdf_context_data = {
            "title": group.unicef_id,
            "payment_plan_group": group,
            "payment_plans": payment_plans,
            "totals": totals,
            "is_social_worker_program": self.is_social_worker_program,
            "fsp": group.financial_service_provider,
            "approval_process": approval_process,
            "payment_plan_group_link": self.payment_plan_group_link,
            **approval_chain(approval_process),
            "reconciliation": reconciliation_summary(
                Payment.objects.filter(parent__payment_plan_group=group).eligible()
            ),
        }
        pdf = generate_pdf_from_html(
            template_name="payment/payment_plan_group_summary_pdf_template.html", data=pdf_context_data
        )
        return pdf, f"PaymentPlanGroupSummary-{group.unicef_id}.pdf"
