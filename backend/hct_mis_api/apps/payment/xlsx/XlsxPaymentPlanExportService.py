import logging
import openpyxl

from openpyxl.utils import get_column_letter
from tempfile import NamedTemporaryFile

from django.contrib.admin.options import get_content_type_for_model
from django.core.files import File
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.template.loader import render_to_string
from django.urls import reverse

from apps.core.utils import encode_id_base64
from hct_mis_api.apps.core.models import XLSXFileTemp


logger = logging.getLogger(__name__)


class XlsxPaymentPlanExportService:
    TITLE = "Payment Plan - Payment List"
    HEADERS = (
        "payment_id",  # 0
        "household_id",
        "household_size",
        "admin2",
        "collector",
        "payment_channel",  # 5
        "fsp",
        "currency",
        "entitlement",  # 7
    )

    def __init__(self, payment_plan):
        self.payment_plan = payment_plan
        self.payment_list = payment_plan.all_active_payments

    def _create_workbook(self) -> openpyxl.Workbook:
        wb = openpyxl.Workbook()
        ws_payments = wb.active
        ws_payments.title = XlsxPaymentPlanExportService.TITLE
        self.wb = wb
        self.ws_payments = ws_payments
        return wb

    def _add_headers(self):
        self.ws_payments.append(XlsxPaymentPlanExportService.HEADERS)

    def _add_payment_row(self, payment):
        household = payment.household

        payment_row = (
            str(payment.id),
            str(household.unicef_id) if household.unicef_id else "",
            household.size,
            str(household.admin2.title) if household.admin2 else "",
            str(payment.head_of_household.full_name) if payment.head_of_household else "",  # TODO collector
            "TODO payment_channel",  # str(payment.payment_channel)
            str(payment.financial_service_provider.name) if payment.financial_service_provider else "",
            payment.entitlement_quantity,
            payment.entitlement_quantity_usd,
        )
        self.ws_payments.append(payment_row)

    def _add_payment_list(self):
        for payment in self.payment_list:
            self._add_payment_row(payment)

    def generate_workbook(self):
        self._create_workbook()
        self._add_headers()
        self._add_payment_list()
        self._adjust_column_width_from_col(self.ws_payments, 2, 1, 0)
        return self.wb

    def generate_file(self, filename):
        self.generate_workbook()
        self.wb.save(filename=filename)

    def _adjust_column_width_from_col(self, ws, min_row, min_col, max_col):
        column_widths = []

        for i, col in enumerate(ws.iter_cols(min_col=min_col, max_col=max_col, min_row=min_row)):

            for cell in col:
                value = cell.value
                if value is not None:

                    if isinstance(value, str) is False:
                        value = str(value)

                    try:
                        column_widths[i] = max(column_widths[i], len(value))
                    except IndexError:
                        column_widths.append(len(value))

        for i, width in enumerate(column_widths):
            col_name = get_column_letter(min_col + i)
            value = column_widths[i] + 2
            ws.column_dimensions[col_name].width = value

    def save_xlsx_file(self, user):
        filename = f"payment_plan_payment_list_{self.payment_plan.unicef_id}.xlsx"
        self.generate_workbook()
        with NamedTemporaryFile() as tmp:
            xlsx_obj = XLSXFileTemp(
                object_id=self.payment_plan.pk,
                content_type=get_content_type_for_model(self.payment_plan),
                created_by=user,
                type=XLSXFileTemp.EXPORT
            )
            self.wb.save(tmp.name)
            tmp.seek(0)
            xlsx_obj.file.save(filename, File(tmp))

    @staticmethod
    def send_email(user, cash_plan_payment_verification_id):
        protocol = "http" if settings.IS_DEV else "https"
        payment_verification_id = encode_id_base64(cash_plan_payment_verification_id, "PaymentPlan")
        api = reverse("download-payment-plan-payment-list", args=[payment_verification_id])
        link = f"{protocol}://{settings.FRONTEND_HOST}{api}"

        msg = "Verification Plan xlsx file was generated and below You have the link to download this file."
        context = {
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "message": msg,
            "link": link,
            "title": "Payment Plan Payment List XLSX file generated",
        }
        text_body = render_to_string("payment/xlsx_file_generated_email.txt", context=context)
        html_body = render_to_string("payment/xlsx_file_generated_email.html", context=context)

        email = EmailMultiAlternatives(
            subject="Verification Plan XLSX file generated",
            from_email=settings.EMAIL_HOST_USER,
            to=[context["email"]],
            body=text_body,
        )
        email.attach_alternative(html_body, "text/html")
        result = email.send()
        if not result:
            logger.error(f"Email couldn't be send to {context['email']}")
