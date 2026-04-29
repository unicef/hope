from __future__ import annotations

from collections import defaultdict
import csv
import dataclasses
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from enum import IntEnum
import io
import logging
import re
from tempfile import NamedTemporaryFile
from typing import IO
import zipfile

from django.contrib.admin.options import get_content_type_for_model
from django.core.exceptions import ObjectDoesNotExist
from django.core.files import File
from django.core.files.base import ContentFile
from django.db import DatabaseError, transaction
from django.template.loader import render_to_string
from django.urls import reverse
import openpyxl
from openpyxl.styles import Font
from pypdf import PdfReader

from hope.apps.account.models import User
from hope.apps.account.permissions import Permissions
from hope.apps.payment.celery_tasks import send_qcf_report_email_notifications_async_task
from hope.apps.payment.services.western_union_ftp import WesternUnionFTPClient
from hope.apps.payment.utils import get_link
from hope.models import (
    FileTemp,
    Payment,
    PaymentPlan,
    WesternUnionData,
    WesternUnionInvoice,
    WesternUnionInvoicePayment,
    WesternUnionPaymentPlanReport,
)

logger = logging.getLogger(__name__)


@dataclasses.dataclass
class InvoiceParseResult:
    date: date
    net_amount: Decimal
    charges: Decimal


@dataclasses.dataclass
class DataParseResult:
    date: date
    advice_name: str
    principal_amount: Decimal


@dataclasses.dataclass
class QCFReportPaymentRowData:
    payment_unicef_id: str | None
    mtcn: str
    mtcns_match: bool
    hope_mtcn: str | None
    payment_plan_unicef_id: str | None
    programme: str
    fc: str
    principal_amount: float
    charges_amount: float
    fee_amount: float
    ad_name_value: str


@dataclasses.dataclass
class QCFReportPaymentPlanData:
    payment_plan_unicef_id: str | None
    principal_total: float = dataclasses.field(init=False)
    charges_total: float = dataclasses.field(init=False)
    refunds_total: float = dataclasses.field(init=False)
    fees_total: float = dataclasses.field(init=False)
    payments_data: list[QCFReportPaymentRowData]

    def __post_init__(self) -> None:
        self.principal_total = sum(p.principal_amount for p in self.payments_data if p.principal_amount >= 0) or 0
        self.charges_total = sum(p.charges_amount for p in self.payments_data) or 0
        self.refunds_total = sum(p.principal_amount for p in self.payments_data if p.principal_amount < 0) or 0
        self.fees_total = sum(p.fee_amount for p in self.payments_data) or 0


class QCFReportsService:
    class QCFReportsServiceError(Exception):
        pass

    class InvoiceFieldIndex(IntEnum):
        RECORD_TYPE = 0
        MTCN = 1
        PAYMENT_UNICEF_ID = 9
        PRINCIPAL_AMOUNT = 10
        CHARGES_AMOUNT = 11
        FEE_AMOUNT = 12
        TRANSACTION_STATUS = 18

        @classmethod
        def last_required_index(cls) -> int:
            return max(member.value for member in cls)

    class InvoiceRecordType:
        DETAIL = "1"
        FOOTER = "9"

    class InvoiceFooterFieldIndex(IntEnum):
        RECORD_TYPE = 0
        TOTAL_NUMBER_OF_TRANSACTIONS = 1
        TOTAL_PRINCIPAL = 2
        TOTAL_CHARGES = 3
        TOTAL_TRANSACTION_FEE = 4

        @classmethod
        def last_required_index(cls) -> int:
            return max(member.value for member in cls)

    FILENAME_DATE_FORMAT = "%Y%m%d"
    FILENAME_DATE_PATTERN = re.compile(r"(\d{8})(?=[^0-9]*\.[^.]+$)")
    DATA_PDF_PRINCIPAL_PATTERN = re.compile(r"Principal\s+([\d,]+\.\d{2})", re.MULTILINE)

    def __init__(self) -> None:
        self._ftp_client: WesternUnionFTPClient | None = None

    @property
    def ftp_client(self) -> WesternUnionFTPClient:
        if self._ftp_client is None:
            self._ftp_client = WesternUnionFTPClient()
        return self._ftp_client

    def process_files_since(self, date_from: datetime) -> None:
        self.import_invoice_files_since(date_from)
        self.import_data_files_since(date_from)
        self.reconcile_pending_records()

    def import_invoice_files_since(self, date_from: datetime) -> None:
        files = self.ftp_client.get_invoice_files_since(date_from)
        for filename, file_like in files:
            if WesternUnionInvoice.objects.filter(name=filename).exists():
                continue

            try:
                self.import_invoice_file(filename, file_like)
            except (
                QCFReportsService.QCFReportsServiceError,
                DatabaseError,
                ObjectDoesNotExist,
                OSError,
                ValueError,
                zipfile.BadZipFile,
            ):
                logger.exception("Failed to import Western Union invoice file %s", filename)

    def import_data_files_since(self, date_from: datetime) -> None:
        files = self.ftp_client.get_data_files_since(date_from)
        for filename, file_like in files:
            if WesternUnionData.objects.filter(name=filename).exists():
                continue

            try:
                self.import_data_file(filename, file_like)
            except (
                QCFReportsService.QCFReportsServiceError,
                DatabaseError,
                ObjectDoesNotExist,
                OSError,
                ValueError,
                zipfile.BadZipFile,
            ):
                logger.exception("Failed to import Western Union data file %s", filename)

    def import_invoice_file(self, filename: str, file_like: io.BytesIO) -> None:
        invoice = WesternUnionInvoice.objects.create(name=filename)

        try:
            self.attach_file(invoice, filename, file_like)
            file_like.seek(0)
            parse_result = self.parse_invoice_file(filename, file_like)
            invoice.date = parse_result.date
            invoice.net_amount = parse_result.net_amount
            invoice.charges = parse_result.charges
            invoice.status = WesternUnionInvoice.STATUS_PENDING
            invoice.error_msg = ""
            invoice.save(update_fields=["date", "net_amount", "charges", "status", "error_msg"])
        except (
            QCFReportsService.QCFReportsServiceError,
            DatabaseError,
            ObjectDoesNotExist,
            OSError,
            ValueError,
            zipfile.BadZipFile,
        ) as exc:
            self.mark_record_error(invoice, exc)

    def import_data_file(self, filename: str, file_like: io.BytesIO) -> None:
        data_file = WesternUnionData.objects.create(name=filename)

        try:
            self.attach_file(data_file, filename, file_like)
            file_like.seek(0)
            parse_result = self.parse_data_file(filename, file_like)
            data_file.date = parse_result.date
            data_file.advice_name = parse_result.advice_name
            data_file.principal_amount = parse_result.principal_amount
            data_file.status = WesternUnionData.STATUS_PENDING
            data_file.error_msg = ""
            data_file.save(update_fields=["date", "advice_name", "principal_amount", "status", "error_msg"])
        except (
            QCFReportsService.QCFReportsServiceError,
            DatabaseError,
            ObjectDoesNotExist,
            OSError,
            ValueError,
            zipfile.BadZipFile,
        ) as exc:
            self.mark_record_error(data_file, exc)

    def reconcile_pending_records(self) -> None:
        pending_invoices = WesternUnionInvoice.objects.filter(
            status=WesternUnionInvoice.STATUS_PENDING,
        ).exclude(
            net_amount__isnull=True,
        )

        for invoice in pending_invoices.order_by("date", "id"):
            try:
                self.reconcile_invoice(invoice)
            except (
                QCFReportsService.QCFReportsServiceError,
                DatabaseError,
                ObjectDoesNotExist,
                OSError,
                ValueError,
                zipfile.BadZipFile,
            ):
                logger.exception("Failed to reconcile Western Union invoice %s", invoice.name)

    def reconcile_invoice(self, invoice: WesternUnionInvoice) -> None:
        candidates = list(
            WesternUnionData.objects.filter(
                status=WesternUnionData.STATUS_PENDING,
                principal_amount=invoice.net_amount,
            ).exclude(principal_amount__isnull=True)
        )
        if not candidates:
            return

        matched_data = self.pick_best_data_match(invoice, candidates)
        if matched_data is None:
            return

        try:
            with transaction.atomic():
                payment_plan_id_payments_lines_map = self.extract_invoice_payment_rows(invoice)
                if not payment_plan_id_payments_lines_map:
                    raise self.QCFReportsServiceError(f"No invoice payment rows found for {invoice.name}")

                self.link_payments_from_invoice_rows(invoice, payment_plan_id_payments_lines_map)
                self.generate_reports_for_invoice(invoice, matched_data, payment_plan_id_payments_lines_map)
                invoice.matched_data = matched_data
                invoice.status = WesternUnionInvoice.STATUS_COMPLETED
                invoice.error_msg = ""
                matched_data.status = WesternUnionData.STATUS_COMPLETED
                matched_data.error_msg = ""
                invoice.save(update_fields=["matched_data", "status", "error_msg"])
                matched_data.save(update_fields=["status", "error_msg"])
        except (
            QCFReportsService.QCFReportsServiceError,
            DatabaseError,
            ObjectDoesNotExist,
            OSError,
            ValueError,
            zipfile.BadZipFile,
        ) as exc:
            self.mark_record_error(invoice, exc)

    def pick_best_data_match(
        self,
        invoice: WesternUnionInvoice,
        candidates: list[WesternUnionData],
    ) -> WesternUnionData | None:
        if len(candidates) == 1:
            return candidates[0]

        return min(
            candidates,
            key=lambda candidate: (
                abs((invoice.date - candidate.date).days) if invoice.date and candidate.date else 10**9,
                candidate.date or date.max,
                candidate.id,
            ),
        )

    def link_payments_from_invoice_rows(
        self,
        invoice: WesternUnionInvoice,
        payment_plan_id_payments_lines_map: dict[str, list[tuple[Payment, list[str]]]],
    ) -> None:
        WesternUnionInvoicePayment.objects.filter(western_union_invoice=invoice).delete()

        payments_to_link = [
            WesternUnionInvoicePayment(
                western_union_invoice=invoice,
                payment=payment,
                transaction_status=fields[self.InvoiceFieldIndex.TRANSACTION_STATUS],
            )
            for payment_raw_data in payment_plan_id_payments_lines_map.values()
            for payment, fields in payment_raw_data
        ]
        if not payments_to_link:
            raise self.QCFReportsServiceError(f"No payments found for Western Union invoice {invoice.name}")

        WesternUnionInvoicePayment.objects.bulk_create(payments_to_link)

    def generate_reports_for_invoice(
        self,
        invoice: WesternUnionInvoice,
        data_file: WesternUnionData,
        payment_plan_id_payments_lines_map: dict[str, list[tuple[Payment, list[str]]]],
    ) -> None:
        ad_name_value = data_file.advice_name or ""
        for payment_plan_id, payment_raw_data in payment_plan_id_payments_lines_map.items():
            payment_plan = PaymentPlan.objects.get(id=payment_plan_id)
            report_name, report = self.generate_report(payment_plan, payment_raw_data, ad_name_value)

            wu_qcf_report = WesternUnionPaymentPlanReport.objects.create(
                qcf_file=invoice,
                payment_plan=payment_plan,
            )

            with NamedTemporaryFile() as tmp:
                file_temp = FileTemp.objects.create(
                    object_id=str(wu_qcf_report.pk),
                    content_type=get_content_type_for_model(wu_qcf_report),
                )
                report.save(tmp.name)
                tmp.seek(0)
                file_temp.file.save(report_name, File(tmp))
                wu_qcf_report.report_file = file_temp
                wu_qcf_report.save()

            transaction.on_commit(
                lambda wu_qcf_report_id=str(wu_qcf_report.id): send_qcf_report_email_notifications_async_task(
                    wu_qcf_report_id
                )
            )

    def extract_invoice_payment_rows(self, invoice: WesternUnionInvoice) -> dict[str, list[tuple[Payment, list[str]]]]:
        if invoice.file is None:
            raise self.QCFReportsServiceError(f"Western Union invoice {invoice.name} has no file")

        payment_plan_id_payments_lines_map: dict[str, list[tuple[Payment, list[str]]]] = defaultdict(list)

        invoice.file.file.open("rb")
        try:
            lines = self.read_rows_from_file_like(invoice.name, invoice.file.file)
        finally:
            invoice.file.file.close()

        for fields in self.extract_data_rows(lines, invoice.name):
            payment_unicef_id = self.normalize_payment_unicef_id(fields[self.InvoiceFieldIndex.PAYMENT_UNICEF_ID])
            try:
                payment = Payment.objects.get(unicef_id=payment_unicef_id)
            except Payment.DoesNotExist:
                logger.error("%s: payment %s does not exist", invoice.name, payment_unicef_id)
                continue

            payment_plan_id_payments_lines_map[str(payment.parent_id)].append((payment, fields))

        return payment_plan_id_payments_lines_map

    def attach_file(self, record: WesternUnionInvoice | WesternUnionData, filename: str, file_like: io.BytesIO) -> None:
        content_file = ContentFile(file_like.read(), name=filename)
        file_temp = FileTemp.objects.create(
            object_id=str(record.pk),
            content_type=get_content_type_for_model(record),
        )
        file_temp.file.save(filename, content_file)
        record.file = file_temp
        record.save(update_fields=["file"])

    def mark_record_error(self, record: WesternUnionInvoice | WesternUnionData, exc: Exception) -> None:
        record.status = record.STATUS_ERROR
        record.error_msg = str(exc)
        record.save(update_fields=["status", "error_msg"])
        logger.exception("Western Union file processing failed for %s", record.name, exc_info=exc)

    def parse_invoice_file(self, filename: str, file_like: IO[bytes]) -> InvoiceParseResult:
        rows = self.read_rows_from_file_like(filename, file_like)
        parsed_date = self.parse_date_from_filename(filename)
        footer_row = self.extract_footer_row(rows, filename)

        net_amount = self.to_decimal(footer_row[self.InvoiceFooterFieldIndex.TOTAL_PRINCIPAL])
        charges = self.to_decimal(footer_row[self.InvoiceFooterFieldIndex.TOTAL_CHARGES])
        return InvoiceParseResult(date=parsed_date, net_amount=net_amount, charges=charges)

    def parse_data_file(self, filename: str, file_like: IO[bytes]) -> DataParseResult:
        parsed_date = self.parse_date_from_filename(filename)
        advice_name, pdf_bytes = self.extract_pdf_from_archive(filename, file_like.read())
        pdf_text = self.extract_text_from_pdf(filename, pdf_bytes)
        principal_amount = self.parse_principal_amount_from_pdf_text(pdf_text, filename)
        if not advice_name:
            raise self.QCFReportsServiceError(f"No advice filename found in data file {filename}")

        return DataParseResult(date=parsed_date, advice_name=advice_name, principal_amount=principal_amount)

    def parse_date_from_filename(self, filename: str) -> date:
        match = self.FILENAME_DATE_PATTERN.search(filename)
        if not match:
            raise self.QCFReportsServiceError(f"Could not parse date from filename {filename}")

        return datetime.strptime(match.group(1), self.FILENAME_DATE_FORMAT).date()

    def read_rows_from_file_like(self, filename: str, file_like: IO[bytes]) -> list[list[str]]:
        file_bytes = file_like.read()
        if not file_bytes:
            raise self.QCFReportsServiceError(f"File {filename} is empty")

        if zipfile.is_zipfile(io.BytesIO(file_bytes)):
            return self.read_rows_from_zip(filename, file_bytes)

        return self.decode_rows(filename, file_bytes)

    def read_rows_from_zip(self, filename: str, file_bytes: bytes) -> list[list[str]]:
        with zipfile.ZipFile(io.BytesIO(file_bytes)) as archive:
            candidate_files = [
                zip_info
                for zip_info in archive.infolist()
                if not zip_info.is_dir() and zip_info.filename.lower().endswith(".cf")
            ]

            if not candidate_files:
                raise self.QCFReportsServiceError(f"No supported text files found in archive {filename}")

            for zip_info in candidate_files:
                with archive.open(zip_info) as extracted_file:
                    try:
                        return self.decode_rows(zip_info.filename, extracted_file.read())
                    except self.QCFReportsServiceError:
                        logger.warning("Skipping unsupported archive member %s in %s", zip_info.filename, filename)

        raise self.QCFReportsServiceError(f"Could not parse any supported archive member in {filename}")

    def extract_pdf_from_archive(self, filename: str, file_bytes: bytes) -> tuple[str, bytes]:
        with zipfile.ZipFile(io.BytesIO(file_bytes)) as archive:
            candidate_files = [
                zip_info
                for zip_info in archive.infolist()
                if not zip_info.is_dir() and zip_info.filename.lower().endswith(".pdf")
            ]
            if not candidate_files:
                raise self.QCFReportsServiceError(f"No PDF advice file found in archive {filename}")
            if len(candidate_files) > 1:
                raise self.QCFReportsServiceError(f"More than one PDF advice file found in archive {filename}")

            zip_info = candidate_files[0]
            advice_name = zip_info.filename.rsplit("/", 1)[-1].rsplit(".", 1)[0]
            return advice_name, archive.read(zip_info)

    def extract_text_from_pdf(self, filename: str, pdf_bytes: bytes) -> str:
        try:
            pages = PdfReader(io.BytesIO(pdf_bytes)).pages
        except (OSError, TypeError, ValueError) as exc:
            raise self.QCFReportsServiceError(
                f"Could not extract text from Western Union AD PDF in {filename}: {exc}"
            ) from exc

        pdf_text = "\n".join(page.extract_text() or "" for page in pages)
        if not pdf_text.strip():
            raise self.QCFReportsServiceError(f"No text extracted from Western Union AD PDF in {filename}")
        return pdf_text

    def decode_rows(self, filename: str, file_bytes: bytes) -> list[list[str]]:
        try:
            decoded_content = file_bytes.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise self.QCFReportsServiceError(f"Could not decode file {filename} as UTF-8") from exc

        return list(csv.reader(io.StringIO(decoded_content)))

    def extract_data_rows(self, rows: list[list[str]], filename: str) -> list[list[str]]:
        if not rows:
            raise self.QCFReportsServiceError(f"Invoice file {filename} has no rows")

        data_rows = [
            row
            for row in rows[1:]
            if row and row[self.InvoiceFieldIndex.RECORD_TYPE].strip().strip('"') == self.InvoiceRecordType.DETAIL
        ]
        if not data_rows:
            raise self.QCFReportsServiceError(f"Invoice file {filename} has no data rows")

        if any(len(row) <= self.InvoiceFieldIndex.last_required_index() for row in data_rows):
            raise self.QCFReportsServiceError(f"Invalid invoice data row length in file {filename}")

        return data_rows

    def extract_footer_row(self, rows: list[list[str]], filename: str) -> list[str]:
        footer_rows = [row for row in rows[1:] if row and row[0].strip().strip('"') == self.InvoiceRecordType.FOOTER]
        if not footer_rows:
            raise self.QCFReportsServiceError(f"Invoice file {filename} has no footer row")
        if len(footer_rows) > 1:
            raise self.QCFReportsServiceError(f"Invoice file {filename} has more than one footer row")

        footer_row = footer_rows[0]
        if len(footer_row) <= self.InvoiceFooterFieldIndex.last_required_index():
            raise self.QCFReportsServiceError(f"Invalid invoice footer row length in file {filename}")

        return footer_row

    def normalize_payment_unicef_id(self, payment_reference: str) -> str:
        normalized_reference = payment_reference.strip().strip('"')
        if normalized_reference.startswith("RC"):
            return normalized_reference
        if normalized_reference.startswith("PT-"):
            return f"RC{normalized_reference}"
        raise self.QCFReportsServiceError(f"Unsupported payment reference {payment_reference}")

    def to_decimal(self, value: str) -> Decimal:
        try:
            return Decimal(str(value).strip().strip('"'))
        except InvalidOperation as exc:
            raise self.QCFReportsServiceError(f"Could not parse decimal value {value}") from exc

    def parse_principal_amount_from_pdf_text(self, pdf_text: str, filename: str) -> Decimal:
        match = self.DATA_PDF_PRINCIPAL_PATTERN.search(pdf_text)
        if not match:
            raise self.QCFReportsServiceError(f"Could not parse principal amount from AD PDF in {filename}")
        return self.to_decimal(match.group(1).replace(",", ""))

    def generate_report(
        self,
        payment_plan: PaymentPlan,
        payment_raw_data: list[tuple[Payment, list[str]]],
        ad_name_value: str | None = None,
    ) -> tuple[str, openpyxl.Workbook]:
        no_of_qcf_reports_for_pp = WesternUnionPaymentPlanReport.objects.filter(payment_plan=payment_plan).count()
        report_filename = (
            f"QCF_{payment_plan.business_area.slug}_{payment_plan.unicef_id}_{no_of_qcf_reports_for_pp + 1}.xlsx"
        )

        funds_commitments_str = ", ".join(
            f"{number}/{item}"
            for number, item in payment_plan.funds_commitments.all().values_list(
                "funds_commitment_group__funds_commitment_number", "funds_commitment_item"
            )
        )
        payments_data: list[QCFReportPaymentRowData] = []
        for payment, fields in payment_raw_data:
            if len(fields) <= self.InvoiceFieldIndex.last_required_index():
                raise self.QCFReportsServiceError(
                    f"Invoice row for payment {payment.unicef_id} is missing required report fields"
                )
            report_mtcn = fields[self.InvoiceFieldIndex.MTCN]
            mtcn_match: bool = str(report_mtcn) == str(payment.fsp_auth_code)

            payments_data.append(
                QCFReportPaymentRowData(
                    payment_unicef_id=payment.unicef_id,
                    mtcn=fields[self.InvoiceFieldIndex.MTCN],
                    mtcns_match=mtcn_match,
                    hope_mtcn=payment.fsp_auth_code,
                    payment_plan_unicef_id=payment_plan.unicef_id,
                    programme=payment_plan.program_cycle.program.name,
                    fc=funds_commitments_str,
                    principal_amount=float(fields[self.InvoiceFieldIndex.PRINCIPAL_AMOUNT]),
                    charges_amount=float(fields[self.InvoiceFieldIndex.CHARGES_AMOUNT]),
                    fee_amount=float(fields[self.InvoiceFieldIndex.FEE_AMOUNT]),
                    ad_name_value=ad_name_value or "",
                )
            )

        report_data = QCFReportPaymentPlanData(
            payment_plan_unicef_id=payment_plan.unicef_id, payments_data=payments_data
        )

        return report_filename, self.generate_report_xlsx(report_data)

    def generate_report_xlsx(self, report_data: QCFReportPaymentPlanData) -> openpyxl.Workbook:
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = f"QCF Report - {report_data.payment_plan_unicef_id}"

        headers = [
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
        ws.append(headers)
        for cell in ws[1]:
            cell.font = Font(bold=True)

        for payment_data in report_data.payments_data:
            ws.append(
                [
                    payment_data.payment_unicef_id,
                    payment_data.mtcn,
                    payment_data.mtcns_match,
                    payment_data.hope_mtcn,
                    payment_data.payment_plan_unicef_id,
                    payment_data.programme,
                    payment_data.fc,
                    payment_data.principal_amount,
                    payment_data.charges_amount,
                    payment_data.fee_amount,
                    payment_data.ad_name_value,
                ]
            )

        ws.append([])

        ws.append(["Principal Total", "", "", "", report_data.principal_total])
        ws.append(["Charges Total", "", "", "", report_data.charges_total])
        ws.append(["Refunds Total", "", "", "", report_data.refunds_total])

        last_row = ws.max_row
        for row in range(last_row - 3, last_row + 1):
            ws[f"A{row}"].font = Font(bold=True)

        return wb

    def send_notification_emails(self, report: WesternUnionPaymentPlanReport) -> None:
        business_area = report.payment_plan.business_area
        users = [
            user for user in User.objects.all() if user.has_perm(Permissions.RECEIVE_PARSED_WU_QCF.name, business_area)
        ]
        if users:
            text_template = "payment/qcf_report_email.txt"
            html_template = "payment/qcf_report_email.html"

            path_name = "download-payment-plan-invoice-report-pdf"
            payment_plan = report.payment_plan

            report_id = str(report.id)
            payment_plan_id = str(payment_plan.id)
            program_code = report.payment_plan.program.code

            payment_plan_link = get_link(
                f"/{payment_plan.business_area.slug}/programs/{program_code}/payment-module/payment-plans/{payment_plan_id}"
            )
            download_link = get_link(reverse(path_name, args=[report_id]))

        for user in users:
            context = {
                "first_name": getattr(user, "first_name", ""),
                "last_name": getattr(user, "last_name", ""),
                "email": getattr(user, "email", ""),
                "message": f"Payment Plan: {payment_plan_link}",
                "title": f"Payment Plan {report.report_file.file.name} Western Union QCF Report",
                "link": f"Western Union QCF Report file: {download_link}",
            }
            user.email_user(
                subject=context["title"],
                html_body=render_to_string(html_template, context=context),
                text_body=render_to_string(text_template, context=context),
            )
