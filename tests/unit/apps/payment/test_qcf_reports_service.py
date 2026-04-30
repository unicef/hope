from datetime import date, datetime
from decimal import Decimal
import io
from pathlib import Path
from unittest import mock
import zipfile

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
from hope.apps.payment.utils import get_link
from hope.models import (
    PaymentPlan,
    Program,
    User,
    WesternUnionData,
    WesternUnionInvoice,
    WesternUnionInvoicePayment,
    WesternUnionPaymentPlanReport,
)

pytestmark = pytest.mark.django_db

SAMPLE_DIR = Path(__file__).parent / "test_file"
QCF_FILENAME = "QCF-123-XYZ-20250101.zip"
AD_FILENAME = "AD-123-XYZ-20250101.zip"
ADVICE_NAME = "ADVCP_E_C_0007_PIIC_13321973568_26_MAR_2026"


@pytest.fixture
def business_area():
    return BusinessAreaFactory(slug="afghanistan")


@pytest.fixture
def user_and_role(business_area):
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
def program(business_area) -> Program:
    return ProgramFactory(status=Program.ACTIVE, business_area=business_area)


@pytest.fixture
def cycle(program):
    return ProgramCycleFactory(program=program, title="Cycle QCF")


@pytest.fixture
def qcf_context(business_area, program, cycle, user_and_role):
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

    payment_1 = PaymentFactory(parent=payment_plan, fsp_auth_code="0486455966", program=program)
    payment_2 = PaymentFactory(parent=payment_plan, fsp_auth_code="669", program=program)
    payment_3 = PaymentFactory(parent=payment_plan, fsp_auth_code=None, program=program)

    payment_1.unicef_id = "RCPT-0520-25-0.000.145"
    payment_1.save(update_fields=["unicef_id"])
    payment_2.unicef_id = "RCPT-0520-25-0.000.144"
    payment_2.save(update_fields=["unicef_id"])
    payment_3.unicef_id = "RCPT-0520-25-0.000.135"
    payment_3.save(update_fields=["unicef_id"])

    return {
        "payment_plan": payment_plan,
        "program": program,
        "payment_1": payment_1,
        "payment_2": payment_2,
        "payment_3": payment_3,
        "user": user_and_role["user"],
        "role_assignment": user_and_role["role_assignment"],
    }


@pytest.fixture
def service() -> QCFReportsService:
    return QCFReportsService()


@pytest.fixture
def sample_file():
    def _sample_file(filename: str) -> io.BytesIO:
        return io.BytesIO((SAMPLE_DIR / filename).read_bytes())

    return _sample_file


@pytest.fixture
def build_zip_file():
    def _build_zip_file(member_name: str, member_content: str | bytes) -> io.BytesIO:
        file_like = io.BytesIO()
        with zipfile.ZipFile(file_like, "w") as archive:
            archive.writestr(member_name, member_content)
        file_like.seek(0)
        return file_like

    return _build_zip_file


@pytest.fixture
def matching_service(sample_file) -> QCFReportsService:
    service = QCFReportsService()
    ftp_client = mock.Mock()
    ftp_client.get_invoice_files_since.return_value = [(QCF_FILENAME, sample_file(QCF_FILENAME))]
    ftp_client.get_data_files_since.return_value = [(AD_FILENAME, sample_file(AD_FILENAME))]
    service._ftp_client = ftp_client
    return service


@pytest.fixture
def reconciled_report(matching_service, qcf_context):
    del qcf_context
    matching_service.process_files_since(datetime(2025, 1, 1))
    return WesternUnionPaymentPlanReport.objects.get()


def test_parse_invoice_file_extracts_footer_totals(service: QCFReportsService, sample_file) -> None:
    result = service.parse_invoice_file(QCF_FILENAME, sample_file(QCF_FILENAME))

    assert result.date == date(2025, 1, 1)
    assert result.net_amount == Decimal("1190.32")
    assert result.charges == Decimal("35.72")


def test_extract_invoice_rows_returns_detail_rows_and_footer(service: QCFReportsService, sample_file) -> None:
    rows = service.read_rows_from_file_like(QCF_FILENAME, sample_file(QCF_FILENAME))

    data_rows = service.extract_data_rows(rows, QCF_FILENAME)
    footer_row = service.extract_footer_row(rows, QCF_FILENAME)

    assert len(data_rows) == 3
    assert all(
        row[service.InvoiceFieldIndex.RECORD_TYPE].strip().strip('"') == service.InvoiceRecordType.DETAIL
        for row in data_rows
    )
    assert footer_row[service.InvoiceFooterFieldIndex.RECORD_TYPE].strip().strip('"') == "9"
    assert service.to_decimal(footer_row[service.InvoiceFooterFieldIndex.TOTAL_PRINCIPAL]) == Decimal("1190.32")
    assert service.to_decimal(footer_row[service.InvoiceFooterFieldIndex.TOTAL_CHARGES]) == Decimal("35.72")


def test_parse_data_file_extracts_date_advice_name_and_principal_amount(
    service: QCFReportsService, sample_file
) -> None:
    result = service.parse_data_file(AD_FILENAME, sample_file(AD_FILENAME))

    assert result.date == date(2025, 1, 1)
    assert result.advice_name == ADVICE_NAME
    assert result.principal_amount == Decimal("1190.32")


def test_import_invoice_file_marks_record_error_when_footer_is_missing(
    service: QCFReportsService, build_zip_file
) -> None:
    invalid_invoice = build_zip_file("broken.cf", "header_1,header_2\n1,detail\n")

    service.import_invoice_file("QCF-123-XYZ-20250102.zip", invalid_invoice)

    invoice = WesternUnionInvoice.objects.get(name="QCF-123-XYZ-20250102.zip")
    assert invoice.status == WesternUnionInvoice.STATUS_ERROR
    assert "has no footer row" in invoice.error_msg


def test_import_data_file_marks_record_error_when_pdf_is_missing(service: QCFReportsService, build_zip_file) -> None:
    invalid_data = build_zip_file("broken.txt", "not a pdf")

    service.import_data_file("AD-123-XYZ-20250102.zip", invalid_data)

    data_file = WesternUnionData.objects.get(name="AD-123-XYZ-20250102.zip")
    assert data_file.status == WesternUnionData.STATUS_ERROR
    assert "No PDF advice file found" in data_file.error_msg


def test_import_invoice_files_since_skips_existing_file(matching_service: QCFReportsService) -> None:
    WesternUnionInvoice.objects.create(name=QCF_FILENAME)

    with mock.patch.object(matching_service, "import_invoice_file") as mock_import_invoice_file:
        matching_service.import_invoice_files_since(datetime(2025, 1, 1))

    mock_import_invoice_file.assert_not_called()


def test_import_data_files_since_skips_existing_file(matching_service: QCFReportsService) -> None:
    WesternUnionData.objects.create(name=AD_FILENAME)

    with mock.patch.object(matching_service, "import_data_file") as mock_import_data_file:
        matching_service.import_data_files_since(datetime(2025, 1, 1))

    mock_import_data_file.assert_not_called()


def test_import_invoice_files_since_logs_and_continues_on_failure(matching_service: QCFReportsService) -> None:
    with (
        mock.patch.object(
            matching_service, "import_invoice_file", side_effect=matching_service.QCFReportsServiceError("boom")
        ),
        mock.patch("hope.apps.payment.services.qcf_reports_service.logger.exception") as mock_exception,
    ):
        matching_service.import_invoice_files_since(datetime(2025, 1, 1))

    mock_exception.assert_called_once()


def test_import_data_files_since_logs_and_continues_on_failure(matching_service: QCFReportsService) -> None:
    with (
        mock.patch.object(
            matching_service, "import_data_file", side_effect=matching_service.QCFReportsServiceError("boom")
        ),
        mock.patch("hope.apps.payment.services.qcf_reports_service.logger.exception") as mock_exception,
    ):
        matching_service.import_data_files_since(datetime(2025, 1, 1))

    mock_exception.assert_called_once()


def test_pick_best_data_match_prefers_nearest_date(service: QCFReportsService) -> None:
    invoice = WesternUnionInvoice.objects.create(
        name="QCF-match.zip",
        date=date(2025, 1, 10),
        net_amount=Decimal("10.00"),
        status=WesternUnionInvoice.STATUS_PENDING,
    )
    closer_candidate = WesternUnionData.objects.create(
        name="AD-closer.zip",
        date=date(2025, 1, 9),
        principal_amount=Decimal("10.00"),
        advice_name="ADVICE-CLOSE",
        status=WesternUnionData.STATUS_PENDING,
    )
    farther_candidate = WesternUnionData.objects.create(
        name="AD-farther.zip",
        date=date(2025, 1, 14),
        principal_amount=Decimal("10.00"),
        advice_name="ADVICE-FAR",
        status=WesternUnionData.STATUS_PENDING,
    )

    matched = service.pick_best_data_match(invoice, [farther_candidate, closer_candidate])

    assert matched == closer_candidate


def test_pick_best_data_match_returns_single_candidate(service: QCFReportsService) -> None:
    invoice = WesternUnionInvoice.objects.create(name="QCF-single.zip", net_amount=Decimal("10.00"))
    candidate = WesternUnionData.objects.create(name="AD-single.zip", principal_amount=Decimal("10.00"))

    assert service.pick_best_data_match(invoice, [candidate]) == candidate


def test_reconcile_pending_records_logs_and_continues_on_failure(service: QCFReportsService) -> None:
    invoice = WesternUnionInvoice.objects.create(
        name="QCF-reconcile.zip",
        status=WesternUnionInvoice.STATUS_PENDING,
        net_amount=Decimal("10.00"),
    )

    with (
        mock.patch.object(service, "reconcile_invoice", side_effect=service.QCFReportsServiceError("boom")),
        mock.patch("hope.apps.payment.services.qcf_reports_service.logger.exception") as mock_exception,
    ):
        service.reconcile_pending_records()

    mock_exception.assert_called_once_with("Failed to reconcile Western Union invoice %s", invoice.name)


def test_reconcile_invoice_returns_when_no_candidates(service: QCFReportsService) -> None:
    invoice = WesternUnionInvoice.objects.create(
        name="QCF-no-match.zip",
        status=WesternUnionInvoice.STATUS_PENDING,
        net_amount=Decimal("10.00"),
    )

    with mock.patch.object(service, "extract_invoice_payment_rows") as mock_extract:
        service.reconcile_invoice(invoice)

    mock_extract.assert_not_called()


def test_reconcile_invoice_returns_when_best_match_is_none(service: QCFReportsService) -> None:
    invoice = WesternUnionInvoice.objects.create(
        name="QCF-none.zip",
        status=WesternUnionInvoice.STATUS_PENDING,
        net_amount=Decimal("10.00"),
    )
    WesternUnionData.objects.create(
        name="AD-none.zip",
        status=WesternUnionData.STATUS_PENDING,
        principal_amount=Decimal("10.00"),
    )

    with (
        mock.patch.object(service, "pick_best_data_match", return_value=None),
        mock.patch.object(service, "extract_invoice_payment_rows") as mock_extract,
    ):
        service.reconcile_invoice(invoice)

    mock_extract.assert_not_called()


def test_reconcile_invoice_marks_error_when_no_payment_rows_found(service: QCFReportsService) -> None:
    invoice = WesternUnionInvoice.objects.create(
        name="QCF-empty.zip",
        status=WesternUnionInvoice.STATUS_PENDING,
        net_amount=Decimal("10.00"),
    )
    matched_data = WesternUnionData.objects.create(
        name="AD-empty.zip",
        status=WesternUnionData.STATUS_PENDING,
        principal_amount=Decimal("10.00"),
    )

    with mock.patch.object(service, "extract_invoice_payment_rows", return_value={}):
        service.reconcile_invoice(invoice)

    invoice.refresh_from_db()
    matched_data.refresh_from_db()
    assert invoice.status == WesternUnionInvoice.STATUS_ERROR
    assert "No invoice payment rows found" in invoice.error_msg
    assert matched_data.status == WesternUnionData.STATUS_PENDING


def test_extract_invoice_payment_rows_skips_missing_payments(
    service: QCFReportsService, sample_file, qcf_context
) -> None:
    invoice = WesternUnionInvoice.objects.create(name=QCF_FILENAME)
    service.attach_file(invoice, QCF_FILENAME, sample_file(QCF_FILENAME))

    qcf_context["payment_1"].delete()

    rows_map = service.extract_invoice_payment_rows(invoice)

    assert sum(len(rows) for rows in rows_map.values()) == 2


def test_link_payments_from_invoice_rows_raises_when_no_payments_to_link(service: QCFReportsService) -> None:
    invoice = WesternUnionInvoice.objects.create(name="QCF-no-payments.zip")

    with pytest.raises(
        service.QCFReportsServiceError,
        match="No payments found for Western Union invoice QCF-no-payments.zip",
    ):
        service.link_payments_from_invoice_rows(invoice, {})


def test_extract_invoice_payment_rows_raises_when_invoice_has_no_file(service: QCFReportsService) -> None:
    invoice = WesternUnionInvoice.objects.create(name="QCF-no-file.zip")

    with pytest.raises(
        service.QCFReportsServiceError,
        match="Western Union invoice QCF-no-file.zip has no file",
    ):
        service.extract_invoice_payment_rows(invoice)


def test_process_files_since_imports_matches_and_generates_report(
    matching_service: QCFReportsService, qcf_context
) -> None:
    matching_service.process_files_since(datetime(2025, 1, 1))

    invoice = WesternUnionInvoice.objects.get()
    data_file = WesternUnionData.objects.get()
    report = WesternUnionPaymentPlanReport.objects.get()

    assert invoice.name == QCF_FILENAME
    assert invoice.status == WesternUnionInvoice.STATUS_COMPLETED
    assert invoice.net_amount == Decimal("1190.32")
    assert invoice.charges == Decimal("35.72")
    assert invoice.matched_data == data_file

    assert data_file.name == AD_FILENAME
    assert data_file.status == WesternUnionData.STATUS_COMPLETED
    assert data_file.principal_amount == Decimal("1190.32")
    assert data_file.advice_name == ADVICE_NAME

    assert WesternUnionInvoicePayment.objects.filter(transaction_status="2").count() == 3
    assert report.qcf_file == invoice
    assert report.payment_plan == qcf_context["payment_plan"]

    report.report_file.file.open("rb")
    workbook = openpyxl.load_workbook(report.report_file.file)
    worksheet = workbook.active
    report.report_file.file.close()

    assert worksheet.title == f"QCF Report - {qcf_context['payment_plan'].unicef_id}"
    assert [cell.value for cell in worksheet[1]] == [
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
    assert worksheet["K2"].value == ADVICE_NAME
    last_row = worksheet.max_row
    assert worksheet[f"E{last_row - 2}"].value == 1190.32
    assert worksheet[f"E{last_row - 1}"].value == 35.72
    assert worksheet[f"E{last_row}"].value == 0


def test_send_notification_emails_uses_report_context(reconciled_report, qcf_context) -> None:
    service = QCFReportsService()

    with (
        mock.patch.object(User, "email_user") as mock_email_user,
        mock.patch("hope.apps.payment.services.qcf_reports_service.render_to_string") as mock_render_to_string,
    ):
        service.send_notification_emails(reconciled_report)

    assert mock_email_user.call_count == 1
    assert mock_render_to_string.call_count == 2
    context = mock_render_to_string.call_args.kwargs["context"]

    payment_plan = qcf_context["payment_plan"]
    plan_link = get_link(
        f"/{payment_plan.business_area.slug}/programs/{payment_plan.program.code}/"
        f"payment-module/payment-plans/{payment_plan.id}"
    )
    report_link = get_link(reverse("download-payment-plan-invoice-report-pdf", args=[reconciled_report.id]))

    assert context == {
        "first_name": getattr(qcf_context["user"], "first_name", ""),
        "last_name": getattr(qcf_context["user"], "last_name", ""),
        "email": getattr(qcf_context["user"], "email", ""),
        "message": f"Payment Plan: {plan_link}",
        "title": f"Payment Plan {reconciled_report.report_file.file.name} Western Union QCF Report",
        "link": f"Western Union QCF Report file: {report_link}",
    }


def test_send_notification_emails_skips_when_no_users_have_permission(reconciled_report, qcf_context) -> None:
    service = QCFReportsService()
    qcf_context["role_assignment"].delete()

    with (
        mock.patch.object(User, "email_user") as mock_email_user,
        mock.patch("hope.apps.payment.services.qcf_reports_service.render_to_string") as mock_render_to_string,
    ):
        service.send_notification_emails(reconciled_report)

    mock_email_user.assert_not_called()
    mock_render_to_string.assert_not_called()


def test_parse_date_from_filename_raises_for_invalid_name(service: QCFReportsService) -> None:
    with pytest.raises(service.QCFReportsServiceError, match="Could not parse date from filename invalid.zip"):
        service.parse_date_from_filename("invalid.zip")


def test_read_rows_from_file_like_raises_for_empty_file(service: QCFReportsService) -> None:
    with pytest.raises(service.QCFReportsServiceError, match="File empty.cf is empty"):
        service.read_rows_from_file_like("empty.cf", io.BytesIO())


def test_read_rows_from_file_like_reads_plain_utf8_csv(service: QCFReportsService) -> None:
    rows = service.read_rows_from_file_like("plain.cf", io.BytesIO(b"a,b\n1,2\n"))

    assert rows == [["a", "b"], ["1", "2"]]


def test_read_rows_from_zip_raises_when_archive_has_no_cf_files(service: QCFReportsService, build_zip_file) -> None:
    file_like = build_zip_file("note.txt", "hello")

    with pytest.raises(service.QCFReportsServiceError, match="No supported text files found in archive bad.zip"):
        service.read_rows_from_zip("bad.zip", file_like.getvalue())


def test_read_rows_from_zip_skips_invalid_cf_and_uses_next_candidate(service: QCFReportsService) -> None:
    file_like = io.BytesIO()
    with zipfile.ZipFile(file_like, "w") as archive:
        archive.writestr("bad.cf", b"\xff")
        archive.writestr("good.cf", "a,b\n1,2\n")
    file_like.seek(0)

    rows = service.read_rows_from_zip("mixed.zip", file_like.getvalue())

    assert rows == [["a", "b"], ["1", "2"]]


def test_read_rows_from_zip_raises_when_no_supported_member_can_be_parsed(service: QCFReportsService) -> None:
    file_like = io.BytesIO()
    with zipfile.ZipFile(file_like, "w") as archive:
        archive.writestr("bad.cf", b"\xff")
    file_like.seek(0)

    with pytest.raises(
        service.QCFReportsServiceError,
        match="Could not parse any supported archive member in bad.zip",
    ):
        service.read_rows_from_zip("bad.zip", file_like.getvalue())


def test_extract_pdf_from_archive_raises_when_multiple_pdfs_exist(service: QCFReportsService) -> None:
    file_like = io.BytesIO()
    with zipfile.ZipFile(file_like, "w") as archive:
        archive.writestr("one.pdf", b"1")
        archive.writestr("two.pdf", b"2")
    file_like.seek(0)

    with pytest.raises(
        service.QCFReportsServiceError,
        match="More than one PDF advice file found in archive multi.zip",
    ):
        service.extract_pdf_from_archive("multi.zip", file_like.getvalue())


def test_extract_text_from_pdf_raises_when_reader_fails(service: QCFReportsService) -> None:
    with (
        mock.patch("hope.apps.payment.services.qcf_reports_service.PdfReader", side_effect=ValueError("bad pdf")),
        pytest.raises(
            service.QCFReportsServiceError,
            match="Could not extract text from Western Union AD PDF in file.pdf: bad pdf",
        ),
    ):
        service.extract_text_from_pdf("file.pdf", b"%PDF")


def test_extract_text_from_pdf_raises_when_no_text_is_extracted(service: QCFReportsService) -> None:
    page = mock.Mock()
    page.extract_text.return_value = ""
    pdf_reader = mock.Mock()
    pdf_reader.pages = [page]

    with (
        mock.patch("hope.apps.payment.services.qcf_reports_service.PdfReader", return_value=pdf_reader),
        pytest.raises(
            service.QCFReportsServiceError,
            match="No text extracted from Western Union AD PDF in file.pdf",
        ),
    ):
        service.extract_text_from_pdf("file.pdf", b"%PDF")


def test_decode_rows_raises_for_non_utf8_bytes(service: QCFReportsService) -> None:
    with pytest.raises(service.QCFReportsServiceError, match="Could not decode file bad.cf as UTF-8"):
        service.decode_rows("bad.cf", b"\xff")


def test_extract_data_rows_raises_when_rows_are_missing(service: QCFReportsService) -> None:
    with pytest.raises(service.QCFReportsServiceError, match="Invoice file file.cf has no rows"):
        service.extract_data_rows([], "file.cf")


def test_extract_data_rows_raises_when_no_detail_rows_exist(service: QCFReportsService) -> None:
    rows = [["header"], ['"9"', "1", "2", "3", "4"]]

    with pytest.raises(service.QCFReportsServiceError, match="Invoice file file.cf has no data rows"):
        service.extract_data_rows(rows, "file.cf")


def test_extract_data_rows_raises_when_detail_row_is_too_short(service: QCFReportsService) -> None:
    rows = [["header"], ['"1"', "short"]]

    with pytest.raises(service.QCFReportsServiceError, match="Invalid invoice data row length in file file.cf"):
        service.extract_data_rows(rows, "file.cf")


def test_extract_footer_row_raises_when_footer_is_missing(service: QCFReportsService) -> None:
    rows = [
        ["header"],
        ['"1"', "detail", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x"],
    ]

    with pytest.raises(service.QCFReportsServiceError, match="Invoice file file.cf has no footer row"):
        service.extract_footer_row(rows, "file.cf")


def test_extract_footer_row_raises_when_multiple_footers_exist(service: QCFReportsService) -> None:
    rows = [["header"], ['"9"', "1", "2", "3", "4"], ['"9"', "1", "2", "3", "4"]]

    with pytest.raises(service.QCFReportsServiceError, match="Invoice file file.cf has more than one footer row"):
        service.extract_footer_row(rows, "file.cf")


def test_extract_footer_row_raises_when_footer_is_too_short(service: QCFReportsService) -> None:
    rows = [["header"], ['"9"', "1", "2"]]

    with pytest.raises(service.QCFReportsServiceError, match="Invalid invoice footer row length in file file.cf"):
        service.extract_footer_row(rows, "file.cf")


def test_normalize_payment_unicef_id_handles_pt_prefix(service: QCFReportsService) -> None:
    assert service.normalize_payment_unicef_id("PT-123") == "RCPT-123"


def test_normalize_payment_unicef_id_raises_for_unsupported_reference(service: QCFReportsService) -> None:
    with pytest.raises(service.QCFReportsServiceError, match="Unsupported payment reference XX-123"):
        service.normalize_payment_unicef_id("XX-123")


def test_to_decimal_raises_for_invalid_value(service: QCFReportsService) -> None:
    with pytest.raises(service.QCFReportsServiceError, match="Could not parse decimal value abc"):
        service.to_decimal("abc")


def test_parse_principal_amount_from_pdf_text_raises_when_pattern_is_missing(service: QCFReportsService) -> None:
    with pytest.raises(
        service.QCFReportsServiceError,
        match="Could not parse principal amount from AD PDF in ad.zip",
    ):
        service.parse_principal_amount_from_pdf_text("no principal here", "ad.zip")


def test_parse_data_file_raises_when_advice_name_is_missing(service: QCFReportsService) -> None:
    with (
        mock.patch.object(service, "extract_pdf_from_archive", return_value=("", b"%PDF")),
        mock.patch.object(service, "extract_text_from_pdf", return_value="Principal 1,190.32"),
        pytest.raises(
            service.QCFReportsServiceError,
            match="No advice filename found in data file AD-missing-name.zip",
        ),
    ):
        service.parse_data_file("AD-missing-name.zip", io.BytesIO(b"zip"))


def test_generate_report_raises_when_row_is_missing_required_fields(service: QCFReportsService, qcf_context) -> None:
    with pytest.raises(
        service.QCFReportsServiceError,
        match=f"Invoice row for payment {qcf_context['payment_1'].unicef_id} is missing required report fields",
    ):
        service.generate_report(
            qcf_context["payment_plan"], [(qcf_context["payment_1"], ['"1"', "short"])], ADVICE_NAME
        )


def test_normalize_payment_unicef_id_returns_rc_values_unchanged(service: QCFReportsService) -> None:
    assert service.normalize_payment_unicef_id("RCPT-123") == "RCPT-123"


def test_western_union_models_str_return_name() -> None:
    invoice = WesternUnionInvoice.objects.create(name="QCF-str.zip")
    data_file = WesternUnionData.objects.create(name="AD-str.zip")

    assert str(invoice) == "QCF-str.zip"
    assert str(data_file) == "AD-str.zip"
