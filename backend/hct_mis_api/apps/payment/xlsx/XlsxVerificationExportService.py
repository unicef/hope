import logging
import openpyxl

from tempfile import NamedTemporaryFile
from django.core.files import File

from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.template.loader import render_to_string
from django.urls import reverse
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

from hct_mis_api.apps.core.utils import encode_id_base64
from hct_mis_api.apps.payment.models import PaymentVerification, XlsxCashPlanPaymentVerificationFile


logger = logging.getLogger(__name__)


class XlsxVerificationExportService:
    HEADERS = (
        "payment_record_id",
        "payment_record_ca_id",
        "received",
        "head_of_household",
        "admin1",
        "admin2",
        "village",
        "address",
        "household_id",
        "household_unicef_id",
        "delivered_amount",
        "received_amount",
    )
    PAYMENT_RECORD_ID_COLUMN_INDEX = 0
    PAYMENT_RECORD_ID_LETTER = "A"
    RECEIVED_COLUMN_INDEX = 2
    RECEIVED_COLUMN_LETTER = "C"
    RECEIVED_AMOUNT_COLUMN_INDEX = 11
    RECEIVED_AMOUNT_COLUMN_LETTER = "L"
    VERIFICATION_SHEET = "Payment Verifications"
    META_SHEET = "Meta"
    VERSION_CELL_NAME_COORDINATES = "A1"
    VERSION_CELL_COORDINATES = "B1"
    VERSION_CELL_NAME = "FILE_TEMPLATE_VERSION"
    VERSION = "1.2"
    TRUE_FALSE_MAPPING = {True: "YES", False: "NO"}

    def __init__(self, cashplan_payment_verification):
        self.cashplan_payment_verification = cashplan_payment_verification
        self.payment_record_verifications = cashplan_payment_verification.payment_record_verifications.all()

    def _create_workbook(self) -> openpyxl.Workbook:
        wb = openpyxl.Workbook()
        ws_verifications = wb.active
        ws_verifications.title = XlsxVerificationExportService.VERIFICATION_SHEET
        self.wb = wb
        self.ws_verifications = ws_verifications
        self.ws_meta = wb.create_sheet(XlsxVerificationExportService.META_SHEET)
        return wb

    def _add_version(self):
        self.ws_meta[
            XlsxVerificationExportService.VERSION_CELL_NAME_COORDINATES
        ] = XlsxVerificationExportService.VERSION_CELL_NAME
        self.ws_meta[XlsxVerificationExportService.VERSION_CELL_COORDINATES] = XlsxVerificationExportService.VERSION

    def _add_headers(self):
        headers_row = XlsxVerificationExportService.HEADERS
        self.ws_verifications.append(headers_row)

    def _to_received_column(self, payment_record_verification):
        status = payment_record_verification.status
        if payment_record_verification.status == PaymentVerification.STATUS_PENDING:
            return None
        if status == PaymentVerification.STATUS_NOT_RECEIVED:
            return XlsxVerificationExportService.TRUE_FALSE_MAPPING[False]
        return XlsxVerificationExportService.TRUE_FALSE_MAPPING[True]

    def _add_payment_record_verification_row(self, payment_record_verification):
        household = payment_record_verification.payment_record.household
        head_of_household = payment_record_verification.payment_record.head_of_household

        payment_record_verification_row = (
            str(payment_record_verification.payment_record_id),
            str(payment_record_verification.payment_record.ca_id),
            self._to_received_column(payment_record_verification),
            str(head_of_household.full_name) if head_of_household else "",
            str(household.admin1.title) if household.admin1 else "",
            str(household.admin2.title) if household.admin2 else "",
            str(household.village),
            str(household.address),
            str(payment_record_verification.payment_record.household_id),
            str(household.unicef_id),
            payment_record_verification.payment_record.delivered_quantity,
            payment_record_verification.received_amount,
        )
        self.ws_verifications.append(payment_record_verification_row)

    def _add_payment_record_verifications(self):
        for payment_record_verification in self.payment_record_verifications:
            self._add_payment_record_verification_row(payment_record_verification)

    def _add_data_validation(self):
        self.dv_received = DataValidation(type="list", formula1=f'"YES,NO"', allow_blank=False)
        self.dv_received.add(f"B2:B{len(self.ws_verifications['B'])}")
        self.ws_verifications.add_data_validation(self.dv_received)
        self.ws_verifications["B2":f"B{len(self.ws_verifications['B'])}"]

    def generate_workbook(self):
        self._create_workbook()
        self._add_version()
        self._add_headers()
        self._add_payment_record_verifications()
        self._add_data_validation()
        self._adjust_column_width_from_col(self.ws_verifications, 0, 1, 8)
        return self.wb

    def generate_file(self, filename):
        self.generate_workbook()
        self.wb.save(filename=filename)

    def save_xlsx_file(self, user):
        filename = f"payment_verification_{self.cashplan_payment_verification.unicef_id}.xlsx"
        self.generate_workbook()
        with NamedTemporaryFile() as tmp:
            xlsx_obj = XlsxCashPlanPaymentVerificationFile(
                created_by=user,
                cash_plan_payment_verification=self.cashplan_payment_verification
            )
            self.wb.save(tmp.name)
            tmp.seek(0)
            xlsx_obj.file.save(
                filename,
                File(tmp)
            )

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

    @staticmethod
    def send_email(user, cash_plan_payment_verification_id):
        protocol = "http" if settings.IS_DEV else "https"
        payment_verification_id = encode_id_base64(cash_plan_payment_verification_id, "CashPlanPaymentVerification")
        api = reverse("download-cash-plan-payment-verification", args=[payment_verification_id])
        link = f"{protocol}://{settings.FRONTEND_HOST}{api}"

        msg = "Verification Plan xlsx file was generated and below You have the link to download this file."
        context = {
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "message": msg,
            "link": link
        }
        text_body = render_to_string(
            "payment/verification_plan_xlsx_file_generated_email.txt", context=context
        )
        html_body = render_to_string(
            "payment/verification_plan_xlsx_file_generated_email.html", context=context
        )

        email = EmailMultiAlternatives(
            subject=f"Verification Plan XLSX file generated",
            from_email=settings.EMAIL_HOST_USER,
            to=[context["email"]],
            body=text_body,
        )
        email.attach_alternative(html_body, "text/html")
        result = email.send()
        if not result:
            logger.error(f"Email couldn't be send to {context['email']}")

