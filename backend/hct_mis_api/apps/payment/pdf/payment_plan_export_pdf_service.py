import logging
from typing import TYPE_CHECKING, Any, Dict, Optional

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.urls import reverse

from hct_mis_api.apps.core.utils import encode_id_base64
from hct_mis_api.apps.payment.models import PaymentPlan
from hct_mis_api.apps.utils.pdf_generator import generate_pdf_from_html

if TYPE_CHECKING:
    from hct_mis_api.apps.account.models import User


logger = logging.getLogger(__name__)


class PaymentPlanPDFExportSevice:
    text_template = "payment/pdf_file_generated_email.txt"
    html_template = "payment/pdf_file_generated_email.html"

    def __init__(self, payment_plan: PaymentPlan):
        self.payment_plan = payment_plan
        self.web_link: str = ""

    @staticmethod
    def get_link(api_url: Optional[str] = None) -> str:
        protocol = "https" if settings.SOCIAL_AUTH_REDIRECT_IS_HTTPS else "http"
        link = f"{protocol}://{settings.FRONTEND_HOST}{api_url}"
        if api_url:
            return link
        return ""

    def generate_web_link(self) -> None:
        payment_plan_id = encode_id_base64(self.payment_plan.id, "PaymentPlan")
        path_name = "download-payment-plan-summary-pdf"
        self.web_link = self.get_link(reverse(path_name, args=[payment_plan_id]))

    def send_email(self, context: Dict) -> None:
        text_body = render_to_string(self.text_template, context=context)
        html_body = render_to_string(self.html_template, context=context)

        email = EmailMultiAlternatives(
            subject=context["title"],
            from_email=settings.EMAIL_HOST_USER,
            to=[context["email"]],
            body=text_body,
        )
        email.attach_alternative(html_body, "text/html")
        result = email.send()
        if not result:
            logger.error(f"Email couldn't be send to {context['email']}")

    def get_email_context(self, user: "User") -> Dict:
        msg = "Payment Plan Summary PDF file(s) have been generated, and below you will find the link to download the file(s)."

        context = {
            "first_name": getattr(user, "first_name", ""),
            "last_name": getattr(user, "last_name", ""),
            "email": getattr(user, "email", ""),
            "message": msg,
            "link": self.web_link,
            "title": "Payment Plan Payment List files generated",
        }

        return context

    def generate_pdf_summary(self) -> Any:
        self.generate_web_link()
        # TODO: update template and table with data
        data = {}
        template_name = "payment/payment_plan_summary_pdf_template.html"
        filename = f"PaymentPlanSummary-{self.payment_plan.unicef_id}.pdf"
        pdf_context_data = {"data": data, "title": self.payment_plan.unicef_id, "link": self.web_link}
        # TODO: update web link now is download link

        pdf = generate_pdf_from_html(
            template_name=template_name,
            data=pdf_context_data,
        )
        return pdf, filename
