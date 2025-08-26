import logging
from tempfile import NamedTemporaryFile

import openpyxl
from django.conf import settings
from django.contrib.admin.options import get_content_type_for_model
from django.core.files import File
from django.urls import reverse
from openpyxl.worksheet.datavalidation import DataValidation

from hope.models.file_temp import FileTemp
from hope.apps.core.utils import encode_id_base64
from hope.models import PaymentVerification, PaymentVerificationPlan
from hope.apps.payment.xlsx.base_xlsx_export_service import XlsxExportBaseService


logger = logging.getLogger(__name__)


class XlsxVerificationExportService(XlsxExportBaseService):
    text_template = "payment/verification_plan_xlsx_file_generated_email.txt"
    html_template = "payment/verification_plan_xlsx_file_generated_email.html"

    _HEADERS = (
        "payment_record_id",
        "payment_record_ca_id",
        "received",
        "head_of_household",
        "phone_no",
        "phone_no_alternative",
        "admin1",
        "admin2",
        "admin3",
        "admin4",
        "village",
        "address",
        "household_id",
        "household_unicef_id",
        "delivered_amount",
        "received_amount",
    )
    _PEOPLE_HEADERS = (
        "payment_record_id",
        "payment_record_ca_id",
        "received",
        "full_name",
        "phone_no",
        "phone_no_alternative",
        "admin1",
        "admin2",
        "admin3",
        "admin4",
        "village",
        "address",
        "delivered_amount",
        "received_amount",
    )
    PAYMENT_RECORD_ID_COLUMN_INDEX = 0
    PAYMENT_RECORD_ID_LETTER = "A"
    RECEIVED_COLUMN_INDEX = 2
    RECEIVED_COLUMN_LETTER = "C"
    RECEIVED_AMOUNT_COLUMN_INDEX = 15
    RECEIVED_AMOUNT_COLUMN_LETTER = "P"
    RECEIVED_AMOUNT_COLUMN_LETTER_PEOPLE = "N"
    VERIFICATION_SHEET = "Payment Verifications"
    META_SHEET = "Meta"
    VERSION_CELL_NAME_COORDINATES = "A1"
    VERSION_CELL_COORDINATES = "B1"
    VERSION_CELL_NAME = "FILE_TEMPLATE_VERSION"
    VERSION = "1.2"
    TRUE_FALSE_MAPPING = {True: "YES", False: "NO"}

    def _get_headers(self) -> tuple:
        if self.is_social_worker_program:
            return XlsxVerificationExportService._PEOPLE_HEADERS
        return XlsxVerificationExportService._HEADERS

    def __init__(self, payment_verification_plan: PaymentVerificationPlan) -> None:
        self.payment_verification_plan = payment_verification_plan
        self.is_social_worker_program = payment_verification_plan.payment_plan.program.is_social_worker_program
        self.payment_record_verifications = payment_verification_plan.payment_record_verifications.all()
        self.HEADERS = self._get_headers()

    def _create_workbook(self) -> openpyxl.Workbook:
        wb = openpyxl.Workbook()
        ws_verifications = wb.active
        ws_verifications.title = XlsxVerificationExportService.VERIFICATION_SHEET
        self.wb = wb
        self.ws_export_list = ws_verifications
        self.ws_meta = wb.create_sheet(XlsxVerificationExportService.META_SHEET)
        return wb

    def _add_version(self) -> None:
        self.ws_meta[XlsxVerificationExportService.VERSION_CELL_NAME_COORDINATES] = (
            XlsxVerificationExportService.VERSION_CELL_NAME
        )
        self.ws_meta[XlsxVerificationExportService.VERSION_CELL_COORDINATES] = XlsxVerificationExportService.VERSION

    def _to_received_column(self, payment_record_verification: PaymentVerification) -> str | None:
        status = payment_record_verification.status
        if payment_record_verification.status == PaymentVerification.STATUS_PENDING:
            return None
        if status == PaymentVerification.STATUS_NOT_RECEIVED:
            return XlsxVerificationExportService.TRUE_FALSE_MAPPING[False]
        return XlsxVerificationExportService.TRUE_FALSE_MAPPING[True]

    def _add_payment_record_verification_row(self, payment_record_verification: PaymentVerification) -> None:
        if self.is_social_worker_program:
            self._add_payment_record_verification_row_for_people(payment_record_verification)
        else:
            self._add_payment_record_verification_row_for_household(payment_record_verification)

    def _add_payment_record_verification_row_for_people(self, payment_record_verification: PaymentVerification) -> None:
        household = payment_record_verification.payment.household
        head_of_household = payment_record_verification.payment.head_of_household
        payment_record_verification_row = (
            str(payment_record_verification.payment_id),
            str(payment_record_verification.payment.unicef_id) if payment_record_verification.payment else "",
            self._to_received_column(payment_record_verification),
            str(head_of_household.full_name) if head_of_household else "",
            str(head_of_household.phone_no) if head_of_household else "",
            str(head_of_household.phone_no_alternative) if head_of_household else "",
            str(household.admin1.name) if household.admin1 else "",
            str(household.admin2.name) if household.admin2 else "",
            str(household.admin3.name) if household.admin3 else "",
            str(household.admin4.name) if household.admin4 else "",
            str(household.village),
            str(household.address),
            payment_record_verification.payment.delivered_quantity,
            payment_record_verification.received_amount,
        )
        self.ws_export_list.append(payment_record_verification_row)

    def _add_payment_record_verification_row_for_household(
        self, payment_record_verification: PaymentVerification
    ) -> None:
        household = payment_record_verification.payment.household
        head_of_household = payment_record_verification.payment.head_of_household
        payment_record_verification_row = (
            str(payment_record_verification.payment.id),
            str(payment_record_verification.payment.unicef_id) if payment_record_verification.payment else "",
            self._to_received_column(payment_record_verification),
            str(head_of_household.full_name) if head_of_household else "",
            str(head_of_household.phone_no) if head_of_household else "",
            str(head_of_household.phone_no_alternative) if head_of_household else "",
            str(household.admin1.name) if household.admin1 else "",
            str(household.admin2.name) if household.admin2 else "",
            str(household.admin3.name) if household.admin3 else "",
            str(household.admin4.name) if household.admin4 else "",
            str(household.village),
            str(household.address),
            str(payment_record_verification.payment.household_id),
            str(household.unicef_id),
            payment_record_verification.payment.delivered_quantity,
            payment_record_verification.received_amount,
        )
        self.ws_export_list.append(payment_record_verification_row)

    def _add_payment_record_verifications(self) -> None:
        for payment_record_verification in self.payment_record_verifications:
            self._add_payment_record_verification_row(payment_record_verification)

    def _add_data_validation(self) -> None:
        self.dv_received = DataValidation(type="list", formula1='"YES,NO"', allow_blank=False)
        self.dv_received.add(f"B2:B{len(self.ws_export_list['B'])}")
        self.ws_export_list.add_data_validation(self.dv_received)
        self.ws_export_list["B2" : f"B{len(self.ws_export_list['B'])}"]

    def generate_workbook(self) -> openpyxl.Workbook:
        self._create_workbook()
        self._add_version()
        self._add_headers()
        self._add_payment_record_verifications()
        self._add_data_validation()
        self._adjust_column_width_from_col(self.ws_export_list)  # min_row, min_col, max_col
        return self.wb

    def save_xlsx_file(self, user: "User") -> None:
        filename = f"payment_verification_{self.payment_verification_plan.unicef_id}.xlsx"
        self.generate_workbook()
        with NamedTemporaryFile() as tmp:
            xlsx_obj = FileTemp(
                object_id=self.payment_verification_plan.pk,
                content_type=get_content_type_for_model(self.payment_verification_plan),
                created_by=user,
            )
            self.wb.save(tmp.name)
            tmp.seek(0)
            xlsx_obj.file.save(filename, File(tmp))

    def get_email_context(self, user: "User") -> dict:
        protocol = "https" if settings.SOCIAL_AUTH_REDIRECT_IS_HTTPS else "http"
        payment_verification_id = encode_id_base64(self.payment_verification_plan.id, "PaymentVerificationPlan")
        api = reverse("download-payment-verification-plan", args=[payment_verification_id])
        link = f"{protocol}://{settings.FRONTEND_HOST}{api}"

        msg = "Verification Plan xlsx file was generated and below You have the link to download this file."
        return {
            "first_name": getattr(user, "first_name", ""),
            "last_name": getattr(user, "last_name", ""),
            "email": getattr(user, "email", ""),
            "message": msg,
            "link": link,
            "title": "Verification Plan XLSX file generated",
        }
