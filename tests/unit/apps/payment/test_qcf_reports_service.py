from datetime import date, datetime, timedelta
from decimal import Decimal
import io
from pathlib import Path
import re
from typing import Callable
from unittest.mock import Mock, patch
import zipfile

from django.utils import timezone
import pytest

from extras.test_utils.factories import (
    PaymentFactory,
    PaymentPlanFactory,
    UserFactory,
    WesternUnionPaymentPlanReportFactory,
)
from hope.apps.payment.services.qcf_reports_service import (
    DataParseResult,
    InvoiceParseResult,
    MatchedDataPaymentRow,
    QCFReportPaymentPlanData,
    QCFReportPaymentRowData,
    QCFReportsService,
)
from hope.models import WesternUnionData, WesternUnionInvoice, WesternUnionInvoicePayment

pytestmark = pytest.mark.django_db
SAMPLE_DIR = Path(__file__).parent / "test_file"


@pytest.fixture
def service() -> QCFReportsService:
    return QCFReportsService()


@pytest.fixture
def one_day() -> timedelta:
    return timedelta(days=1)


@pytest.fixture
def sample_file() -> Callable[[str], io.BytesIO]:
    def _sample_file(filename: str) -> io.BytesIO:
        return io.BytesIO((SAMPLE_DIR / filename).read_bytes())

    return _sample_file


@pytest.fixture
def build_zip_file() -> Callable[[str, str | bytes], io.BytesIO]:
    def _build_zip_file(member_name: str, member_content: str | bytes) -> io.BytesIO:
        file_like = io.BytesIO()
        with zipfile.ZipFile(file_like, "w") as archive:
            archive.writestr(member_name, member_content)
        file_like.seek(0)
        return file_like

    return _build_zip_file


@pytest.fixture
def build_payment_row() -> Callable[[], MatchedDataPaymentRow]:
    def _build_payment_row() -> MatchedDataPaymentRow:
        payment = PaymentFactory(
            unicef_id="RCPT-3900-26-0.004.911",
            fsp_auth_code="0188322767",
        )
        return MatchedDataPaymentRow(
            payment=payment,
            mtcn="0188322767",
            transaction_status="2",
            principal_amount=Decimal("100.00"),
            charges_amount=Decimal("0.00"),
            fee_amount=Decimal("0.00"),
        )

    return _build_payment_row


def test_reconcile_invoice_marks_error_when_no_matching_data_file_found_after_grace_period(
    service: QCFReportsService,
    one_day: timedelta,
    sample_file: Callable[[str], io.BytesIO],
    build_zip_file: Callable[[str, str | bytes], io.BytesIO],
    build_payment_row: Callable[[], MatchedDataPaymentRow],
) -> None:
    invoice = WesternUnionInvoice.objects.create(
        name="AD-AUS001029-SL-20251115.ZIP",
        advice_name="Advice-20251115",
        date=timezone.now().date() - service.UNMATCHED_INVOICE_ERROR_GRACE_PERIOD - one_day,
        net_amount=Decimal("100.00"),
    )

    service.reconcile_invoice(invoice)

    invoice.refresh_from_db()

    assert invoice.status == WesternUnionInvoice.STATUS_ERROR
    assert invoice.error_msg == "No matching data file found"


def test_reconcile_invoice_keeps_recent_unmatched_invoice_pending(
    service: QCFReportsService,
    one_day: timedelta,
    sample_file: Callable[[str], io.BytesIO],
    build_zip_file: Callable[[str, str | bytes], io.BytesIO],
    build_payment_row: Callable[[], MatchedDataPaymentRow],
) -> None:
    invoice = WesternUnionInvoice.objects.create(
        name="AD-AUS001029-SL-20251115.ZIP",
        advice_name="Advice-20251115",
        date=timezone.now().date(),
        net_amount=Decimal("100.00"),
    )

    service.reconcile_invoice(invoice)

    invoice.refresh_from_db()

    assert invoice.status == WesternUnionInvoice.STATUS_PENDING
    assert invoice.error_msg is None


def test_reconcile_invoice_completes_with_matching_data_file(
    service: QCFReportsService,
    one_day: timedelta,
    sample_file: Callable[[str], io.BytesIO],
    build_zip_file: Callable[[str, str | bytes], io.BytesIO],
    build_payment_row: Callable[[], MatchedDataPaymentRow],
) -> None:
    invoice = WesternUnionInvoice.objects.create(
        name="AD-AUS001029-SL-20251115.ZIP",
        advice_name="Advice-20251115",
        date=date(2025, 11, 15),
        net_amount=Decimal("100.00"),
    )
    matched_data = WesternUnionData.objects.create(
        name="QCF-AUS001029-SL-20251115.ZIP",
        date=date(2025, 11, 14),
        amount=Decimal("100.00"),
        status=WesternUnionData.STATUS_PENDING,
    )
    payment_map = {"payment-plan-id": [build_payment_row()]}

    with (
        patch.object(
            service,
            "extract_data_payment_rows",
            return_value=payment_map,
        ) as extract_data_payment_rows_mock,
        patch.object(
            service,
            "link_payments_from_data_rows",
        ) as link_payments_from_data_rows_mock,
        patch.object(
            service,
            "generate_reports_for_invoice",
        ) as generate_reports_for_invoice_mock,
    ):
        service.reconcile_invoice(invoice)

    invoice.refresh_from_db()
    matched_data.refresh_from_db()

    assert invoice.status == WesternUnionInvoice.STATUS_COMPLETED
    assert invoice.error_msg == ""
    assert invoice.matched_data == matched_data
    assert matched_data.status == WesternUnionData.STATUS_COMPLETED
    assert matched_data.error_msg == ""
    extract_data_payment_rows_mock.assert_called_once_with(matched_data)
    link_payments_from_data_rows_mock.assert_called_once_with(invoice, payment_map)
    generate_reports_for_invoice_mock.assert_called_once_with(invoice, payment_map, send_notifications=True)


def test_reconcile_invoice_passes_send_notifications_flag_to_report_generation(
    service: QCFReportsService,
    one_day: timedelta,
    sample_file: Callable[[str], io.BytesIO],
    build_zip_file: Callable[[str, str | bytes], io.BytesIO],
    build_payment_row: Callable[[], MatchedDataPaymentRow],
) -> None:
    invoice = WesternUnionInvoice.objects.create(
        name="AD-AUS001029-SL-20251116.ZIP",
        advice_name="Advice-20251116",
        date=date(2025, 11, 16),
        net_amount=Decimal("150.00"),
    )
    matched_data = WesternUnionData.objects.create(
        name="QCF-AUS001029-SL-20251116.ZIP",
        date=date(2025, 11, 16),
        amount=Decimal("150.00"),
        status=WesternUnionData.STATUS_PENDING,
    )
    payment_map = {"payment-plan-id": [build_payment_row()]}

    with (
        patch.object(service, "extract_data_payment_rows", return_value=payment_map),
        patch.object(service, "link_payments_from_data_rows"),
        patch.object(service, "generate_reports_for_invoice") as generate_reports_for_invoice_mock,
    ):
        service.reconcile_invoice(invoice, send_notifications=False)

    matched_data.refresh_from_db()

    assert matched_data.status == WesternUnionData.STATUS_COMPLETED
    generate_reports_for_invoice_mock.assert_called_once_with(invoice, payment_map, send_notifications=False)


def test_reconcile_invoice_marks_error_when_no_valid_payments_found_in_matching_data_file(
    service: QCFReportsService,
    one_day: timedelta,
    sample_file: Callable[[str], io.BytesIO],
    build_zip_file: Callable[[str, str | bytes], io.BytesIO],
    build_payment_row: Callable[[], MatchedDataPaymentRow],
) -> None:
    invoice = WesternUnionInvoice.objects.create(
        name="AD-AUS001029-SL-20251115.ZIP",
        advice_name="Advice-20251115",
        date=date(2025, 11, 15),
        net_amount=Decimal("100.00"),
    )
    matched_data = WesternUnionData.objects.create(
        name="QCF-AUS001029-SL-20251115.ZIP",
        date=date(2025, 11, 15),
        amount=Decimal("100.00"),
        status=WesternUnionData.STATUS_PENDING,
    )

    with patch.object(
        service,
        "extract_data_payment_rows",
        return_value={},
    ) as extract_data_payment_rows_mock:
        service.reconcile_invoice(invoice)

    invoice.refresh_from_db()
    matched_data.refresh_from_db()

    assert invoice.status == WesternUnionInvoice.STATUS_ERROR
    assert invoice.error_msg == "No valid payments found in matching data file"
    assert matched_data.status == WesternUnionData.STATUS_ERROR
    assert matched_data.error_msg == "No valid payments found in matching data file"
    extract_data_payment_rows_mock.assert_called_once_with(matched_data)


def test_get_matching_data_file_picks_closest_date(
    service: QCFReportsService,
    one_day: timedelta,
    sample_file: Callable[[str], io.BytesIO],
    build_zip_file: Callable[[str, str | bytes], io.BytesIO],
    build_payment_row: Callable[[], MatchedDataPaymentRow],
) -> None:
    invoice = WesternUnionInvoice.objects.create(
        name="AD-AUS001029-SL-20251115.ZIP",
        advice_name="Advice-20251115",
        date=date(2025, 11, 15),
        net_amount=Decimal("100.00"),
    )
    farther_data = WesternUnionData.objects.create(
        name="QCF-AUS001029-SL-20251110.ZIP",
        date=date(2025, 11, 10),
        amount=Decimal("100.00"),
        status=WesternUnionData.STATUS_PENDING,
    )
    closer_data = WesternUnionData.objects.create(
        name="QCF-AUS001029-SL-20251114.ZIP",
        date=date(2025, 11, 14),
        amount=Decimal("100.00"),
        status=WesternUnionData.STATUS_PENDING,
    )

    matched_data = service.get_matching_data_file(invoice)

    assert matched_data == closer_data
    assert matched_data != farther_data


def test_reconcile_pending_records_logs_and_continues_after_invoice_failure(
    service: QCFReportsService,
    one_day: timedelta,
    sample_file: Callable[[str], io.BytesIO],
    build_zip_file: Callable[[str, str | bytes], io.BytesIO],
    build_payment_row: Callable[[], MatchedDataPaymentRow],
) -> None:
    first_invoice = WesternUnionInvoice.objects.create(
        name="AD-AUS001029-SL-20251119.ZIP",
        advice_name="Advice-20251119",
        date=date(2025, 11, 19),
        net_amount=Decimal("100.00"),
        status=WesternUnionInvoice.STATUS_PENDING,
        is_legacy=False,
    )
    second_invoice = WesternUnionInvoice.objects.create(
        name="AD-AUS001029-SL-20251120.ZIP",
        advice_name="Advice-20251120",
        date=date(2025, 11, 20),
        net_amount=Decimal("120.00"),
        status=WesternUnionInvoice.STATUS_PENDING,
        is_legacy=False,
    )

    with (
        patch.object(
            service,
            "reconcile_invoice",
            side_effect=[service.QCFReportsServiceError("boom"), None],
        ) as reconcile_invoice_mock,
        patch("hope.apps.payment.services.qcf_reports_service.logger.exception") as exception_mock,
    ):
        service.reconcile_pending_records()

    assert reconcile_invoice_mock.call_count == 2
    called_invoice_ids = [call.args[0].id for call in reconcile_invoice_mock.call_args_list]
    assert called_invoice_ids == [first_invoice.id, second_invoice.id]
    exception_mock.assert_called_once()


def test_reconcile_pending_records_ignores_legacy_invoices(
    service: QCFReportsService,
    one_day: timedelta,
    sample_file: Callable[[str], io.BytesIO],
    build_zip_file: Callable[[str, str | bytes], io.BytesIO],
    build_payment_row: Callable[[], MatchedDataPaymentRow],
) -> None:
    legacy_invoice = WesternUnionInvoice.objects.create(
        name="AD-AUS001029-SL-20251117.ZIP",
        advice_name="Legacy-advice",
        date=date(2025, 11, 17),
        net_amount=Decimal("100.00"),
        status=WesternUnionInvoice.STATUS_PENDING,
        is_legacy=True,
    )
    current_invoice = WesternUnionInvoice.objects.create(
        name="AD-AUS001029-SL-20251118.ZIP",
        advice_name="Current-advice",
        date=date(2025, 11, 18),
        net_amount=Decimal("120.00"),
        status=WesternUnionInvoice.STATUS_PENDING,
        is_legacy=False,
    )

    with patch.object(service, "reconcile_invoice") as reconcile_invoice_mock:
        service.reconcile_pending_records()

    reconcile_invoice_mock.assert_called_once()
    called_invoice = reconcile_invoice_mock.call_args.args[0]
    assert called_invoice.id == current_invoice.id
    assert called_invoice.id != legacy_invoice.id


def test_reconcile_invoice_marks_only_invoice_error_when_report_generation_fails(
    service: QCFReportsService,
    one_day: timedelta,
    sample_file: Callable[[str], io.BytesIO],
    build_zip_file: Callable[[str, str | bytes], io.BytesIO],
    build_payment_row: Callable[[], MatchedDataPaymentRow],
) -> None:
    invoice = WesternUnionInvoice.objects.create(
        name="AD-AUS001029-SL-20251121.ZIP",
        advice_name="Advice-20251121",
        date=date(2025, 11, 21),
        net_amount=Decimal("100.00"),
    )
    matched_data = WesternUnionData.objects.create(
        name="QCF-AUS001029-SL-20251121.ZIP",
        date=date(2025, 11, 21),
        amount=Decimal("100.00"),
        status=WesternUnionData.STATUS_PENDING,
    )
    payment_map = {"payment-plan-id": [build_payment_row()]}

    with (
        patch.object(service, "extract_data_payment_rows", return_value=payment_map),
        patch.object(service, "link_payments_from_data_rows"),
        patch.object(
            service,
            "generate_reports_for_invoice",
            side_effect=service.QCFReportsServiceError("report failed"),
        ),
    ):
        service.reconcile_invoice(invoice)

    invoice.refresh_from_db()
    matched_data.refresh_from_db()

    assert invoice.status == WesternUnionInvoice.STATUS_ERROR
    assert invoice.error_msg == "report failed"
    assert matched_data.status == WesternUnionData.STATUS_PENDING
    assert matched_data.error_msg is None


def test_should_mark_unmatched_invoice_as_error_returns_false_without_date(
    service: QCFReportsService,
    one_day: timedelta,
    sample_file: Callable[[str], io.BytesIO],
    build_zip_file: Callable[[str, str | bytes], io.BytesIO],
    build_payment_row: Callable[[], MatchedDataPaymentRow],
) -> None:
    invoice = WesternUnionInvoice.objects.create(name="AD-AUS001029-SL-20251122.ZIP")

    assert service.should_mark_unmatched_invoice_as_error(invoice) is False


def test_process_files_since_runs_imports_and_reconciliation(
    service: QCFReportsService,
    one_day: timedelta,
    sample_file: Callable[[str], io.BytesIO],
    build_zip_file: Callable[[str, str | bytes], io.BytesIO],
    build_payment_row: Callable[[], MatchedDataPaymentRow],
) -> None:
    date_from = datetime(2026, 1, 1)

    with (
        patch.object(service, "import_invoice_files_since") as import_invoice_files_since_mock,
        patch.object(service, "import_data_files_since") as import_data_files_since_mock,
        patch.object(service, "reconcile_pending_records") as reconcile_pending_records_mock,
    ):
        service.process_files_since(date_from)

    import_invoice_files_since_mock.assert_called_once_with(date_from)
    import_data_files_since_mock.assert_called_once_with(date_from)
    reconcile_pending_records_mock.assert_called_once_with()


def test_import_invoice_file_sets_pending_fields_on_success(
    service: QCFReportsService,
    one_day: timedelta,
    sample_file: Callable[[str], io.BytesIO],
    build_zip_file: Callable[[str, str | bytes], io.BytesIO],
    build_payment_row: Callable[[], MatchedDataPaymentRow],
) -> None:
    parse_result = InvoiceParseResult(
        date=date(2026, 1, 1),
        advice_name="Advice-1",
        net_amount=Decimal("100.00"),
        charges=Decimal("3.00"),
    )

    with (
        patch.object(service, "attach_file"),
        patch.object(service, "parse_invoice_file", return_value=parse_result),
    ):
        service.import_invoice_file("AD-AUS001029-SL-20260101.ZIP", io.BytesIO(b"content"))

    invoice = WesternUnionInvoice.objects.get(name="AD-AUS001029-SL-20260101.ZIP")
    assert invoice.date == parse_result.date
    assert invoice.advice_name == parse_result.advice_name
    assert invoice.net_amount == parse_result.net_amount
    assert invoice.charges == parse_result.charges
    assert invoice.status == WesternUnionInvoice.STATUS_PENDING
    assert invoice.error_msg == ""


def test_import_invoice_file_marks_error_on_failure(
    service: QCFReportsService,
    one_day: timedelta,
    sample_file: Callable[[str], io.BytesIO],
    build_zip_file: Callable[[str, str | bytes], io.BytesIO],
    build_payment_row: Callable[[], MatchedDataPaymentRow],
) -> None:
    with (
        patch.object(service, "attach_file"),
        patch.object(
            service,
            "parse_invoice_file",
            side_effect=service.QCFReportsServiceError("broken invoice"),
        ),
    ):
        service.import_invoice_file("AD-AUS001029-SL-20260102.ZIP", io.BytesIO(b"content"))

    invoice = WesternUnionInvoice.objects.get(name="AD-AUS001029-SL-20260102.ZIP")
    assert invoice.status == WesternUnionInvoice.STATUS_ERROR
    assert invoice.error_msg == "broken invoice"


def test_import_data_file_sets_pending_fields_on_success(
    service: QCFReportsService,
    one_day: timedelta,
    sample_file: Callable[[str], io.BytesIO],
    build_zip_file: Callable[[str, str | bytes], io.BytesIO],
    build_payment_row: Callable[[], MatchedDataPaymentRow],
) -> None:
    parse_result = DataParseResult(date=date(2026, 1, 1), amount=Decimal("200.00"))

    with (
        patch.object(service, "attach_file"),
        patch.object(service, "parse_data_file", return_value=parse_result),
    ):
        service.import_data_file("QCF-AUS001029-SL-20260101.ZIP", io.BytesIO(b"content"))

    data_file = WesternUnionData.objects.get(name="QCF-AUS001029-SL-20260101.ZIP")
    assert data_file.date == parse_result.date
    assert data_file.amount == parse_result.amount
    assert data_file.status == WesternUnionData.STATUS_PENDING
    assert data_file.error_msg == ""


def test_import_data_file_marks_error_on_failure(
    service: QCFReportsService,
    one_day: timedelta,
    sample_file: Callable[[str], io.BytesIO],
    build_zip_file: Callable[[str, str | bytes], io.BytesIO],
    build_payment_row: Callable[[], MatchedDataPaymentRow],
) -> None:
    with (
        patch.object(service, "attach_file"),
        patch.object(
            service,
            "parse_data_file",
            side_effect=service.QCFReportsServiceError("broken data"),
        ),
    ):
        service.import_data_file("QCF-AUS001029-SL-20260102.ZIP", io.BytesIO(b"content"))

    data_file = WesternUnionData.objects.get(name="QCF-AUS001029-SL-20260102.ZIP")
    assert data_file.status == WesternUnionData.STATUS_ERROR
    assert data_file.error_msg == "broken data"


def test_import_invoice_files_since_logs_and_continues_on_failure(
    service: QCFReportsService,
    one_day: timedelta,
    sample_file: Callable[[str], io.BytesIO],
    build_zip_file: Callable[[str, str | bytes], io.BytesIO],
    build_payment_row: Callable[[], MatchedDataPaymentRow],
) -> None:
    service._ftp_client = Mock()

    with (
        patch.object(
            service._ftp_client,
            "get_invoice_files_since",
            return_value=[
                ("AD-AUS001029-SL-20260101.ZIP", io.BytesIO(b"content")),
                ("AD-AUS001029-SL-20260102.ZIP", io.BytesIO(b"content")),
            ],
        ),
        patch.object(
            service,
            "import_invoice_file",
            side_effect=[service.QCFReportsServiceError("boom"), None],
        ) as import_invoice_file_mock,
        patch("hope.apps.payment.services.qcf_reports_service.logger.exception") as exception_mock,
    ):
        service.import_invoice_files_since(datetime(2026, 1, 1))

    assert import_invoice_file_mock.call_count == 2
    exception_mock.assert_called_once()


def test_import_invoice_files_since_imports_new_file(
    service: QCFReportsService,
    one_day: timedelta,
    sample_file: Callable[[str], io.BytesIO],
    build_zip_file: Callable[[str, str | bytes], io.BytesIO],
    build_payment_row: Callable[[], MatchedDataPaymentRow],
) -> None:
    file_like = io.BytesIO(b"content")

    service._ftp_client = Mock()

    with (
        patch.object(
            service._ftp_client,
            "get_invoice_files_since",
            return_value=[("AD-AUS001029-SL-20260103.ZIP", file_like)],
        ),
        patch.object(service, "import_invoice_file") as import_invoice_file_mock,
    ):
        service.import_invoice_files_since(datetime(2026, 1, 1))

    import_invoice_file_mock.assert_called_once_with("AD-AUS001029-SL-20260103.ZIP", file_like)


def test_import_invoice_files_since_skips_existing_file(
    service: QCFReportsService,
    one_day: timedelta,
    sample_file: Callable[[str], io.BytesIO],
    build_zip_file: Callable[[str, str | bytes], io.BytesIO],
    build_payment_row: Callable[[], MatchedDataPaymentRow],
) -> None:
    existing = WesternUnionInvoice.objects.create(name="AD-AUS001029-SL-20260101.ZIP")
    del existing

    service._ftp_client = Mock()

    with (
        patch.object(
            service._ftp_client,
            "get_invoice_files_since",
            return_value=[("AD-AUS001029-SL-20260101.ZIP", io.BytesIO(b"content"))],
        ),
        patch.object(service, "import_invoice_file") as import_invoice_file_mock,
    ):
        service.import_invoice_files_since(datetime(2026, 1, 1))

    import_invoice_file_mock.assert_not_called()


def test_import_data_files_since_skips_existing_file(
    service: QCFReportsService,
    one_day: timedelta,
    sample_file: Callable[[str], io.BytesIO],
    build_zip_file: Callable[[str, str | bytes], io.BytesIO],
    build_payment_row: Callable[[], MatchedDataPaymentRow],
) -> None:
    WesternUnionData.objects.create(name="QCF-AUS001029-SL-20260101.ZIP")

    service._ftp_client = Mock()

    with (
        patch.object(
            service._ftp_client,
            "get_data_files_since",
            return_value=[("QCF-AUS001029-SL-20260101.ZIP", io.BytesIO(b"content"))],
        ),
        patch.object(service, "import_data_file") as import_data_file_mock,
    ):
        service.import_data_files_since(datetime(2026, 1, 1))

    import_data_file_mock.assert_not_called()


def test_import_data_files_since_logs_and_continues_on_failure(
    service: QCFReportsService,
    one_day: timedelta,
    sample_file: Callable[[str], io.BytesIO],
    build_zip_file: Callable[[str, str | bytes], io.BytesIO],
    build_payment_row: Callable[[], MatchedDataPaymentRow],
) -> None:
    service._ftp_client = Mock()

    with (
        patch.object(
            service._ftp_client,
            "get_data_files_since",
            return_value=[("QCF-AUS001029-SL-20260101.ZIP", io.BytesIO(b"content"))],
        ),
        patch.object(
            service,
            "import_data_file",
            side_effect=service.QCFReportsServiceError("boom"),
        ),
        patch("hope.apps.payment.services.qcf_reports_service.logger.exception") as exception_mock,
    ):
        service.import_data_files_since(datetime(2026, 1, 1))

    exception_mock.assert_called_once()


def test_import_data_files_since_imports_new_file(
    service: QCFReportsService,
    one_day: timedelta,
    sample_file: Callable[[str], io.BytesIO],
    build_zip_file: Callable[[str, str | bytes], io.BytesIO],
    build_payment_row: Callable[[], MatchedDataPaymentRow],
) -> None:
    file_like = io.BytesIO(b"content")

    service._ftp_client = Mock()

    with (
        patch.object(
            service._ftp_client,
            "get_data_files_since",
            return_value=[("QCF-AUS001029-SL-20260103.ZIP", file_like)],
        ),
        patch.object(service, "import_data_file") as import_data_file_mock,
    ):
        service.import_data_files_since(datetime(2026, 1, 1))

    import_data_file_mock.assert_called_once_with("QCF-AUS001029-SL-20260103.ZIP", file_like)


def test_get_matching_data_candidates_returns_only_pending_non_error_rows(
    service: QCFReportsService,
    one_day: timedelta,
    sample_file: Callable[[str], io.BytesIO],
    build_zip_file: Callable[[str, str | bytes], io.BytesIO],
    build_payment_row: Callable[[], MatchedDataPaymentRow],
) -> None:
    invoice = WesternUnionInvoice.objects.create(
        name="AD-AUS001029-SL-20260101.ZIP",
        net_amount=Decimal("100.00"),
    )
    pending_match = WesternUnionData.objects.create(
        name="QCF-pending.zip",
        amount=Decimal("100.00"),
        status=WesternUnionData.STATUS_PENDING,
    )
    WesternUnionData.objects.create(
        name="QCF-completed.zip",
        amount=Decimal("100.00"),
        status=WesternUnionData.STATUS_COMPLETED,
    )
    WesternUnionData.objects.create(
        name="QCF-error.zip",
        amount=Decimal("100.00"),
        status=WesternUnionData.STATUS_ERROR,
    )
    WesternUnionData.objects.create(
        name="QCF-null.zip",
        amount=None,
        status=WesternUnionData.STATUS_PENDING,
    )

    candidates = service.get_matching_data_candidates(invoice)

    assert candidates == [pending_match]


def test_link_payments_from_data_rows_replaces_existing_links(
    service: QCFReportsService,
    one_day: timedelta,
    sample_file: Callable[[str], io.BytesIO],
    build_zip_file: Callable[[str, str | bytes], io.BytesIO],
    build_payment_row: Callable[[], MatchedDataPaymentRow],
) -> None:
    invoice = WesternUnionInvoice.objects.create(name="AD-AUS001029-SL-20260103.ZIP")
    old_payment = PaymentFactory()
    new_payment = PaymentFactory(unicef_id="RCPT-3900-26-0.004.911", fsp_auth_code="0188322767")
    WesternUnionInvoicePayment.objects.create(
        western_union_invoice=invoice,
        payment=old_payment,
        transaction_status="2",
    )
    payment_map = {
        str(new_payment.parent_id): [
            MatchedDataPaymentRow(
                payment=new_payment,
                mtcn="0188322767",
                transaction_status="7",
                principal_amount=Decimal("100.00"),
                charges_amount=Decimal("0.00"),
                fee_amount=Decimal("0.00"),
            )
        ]
    }

    service.link_payments_from_data_rows(invoice, payment_map)

    links = list(WesternUnionInvoicePayment.objects.filter(western_union_invoice=invoice))
    assert len(links) == 1
    assert links[0].payment_id == new_payment.id
    assert links[0].transaction_status == "7"


def test_link_payments_from_data_rows_raises_when_empty(
    service: QCFReportsService,
    one_day: timedelta,
    sample_file: Callable[[str], io.BytesIO],
    build_zip_file: Callable[[str, str | bytes], io.BytesIO],
    build_payment_row: Callable[[], MatchedDataPaymentRow],
) -> None:
    invoice = WesternUnionInvoice.objects.create(name="AD-AUS001029-SL-20260104.ZIP")

    with pytest.raises(
        service.QCFReportsServiceError, match=re.escape("No valid payments found in matching data file")
    ):
        service.link_payments_from_data_rows(invoice, {})


def test_extract_data_payment_rows_raises_when_matching_data_file_has_no_file(
    service: QCFReportsService,
    one_day: timedelta,
    sample_file: Callable[[str], io.BytesIO],
    build_zip_file: Callable[[str, str | bytes], io.BytesIO],
    build_payment_row: Callable[[], MatchedDataPaymentRow],
) -> None:
    data_file = WesternUnionData.objects.create(name="QCF-no-file.zip")

    with pytest.raises(service.QCFReportsServiceError, match=re.escape("Matching data file has no file")):
        service.extract_data_payment_rows(data_file)


def test_extract_data_payment_rows_skips_missing_payments(
    service: QCFReportsService,
    one_day: timedelta,
    sample_file: Callable[[str], io.BytesIO],
    build_zip_file: Callable[[str, str | bytes], io.BytesIO],
    build_payment_row: Callable[[], MatchedDataPaymentRow],
) -> None:
    existing_payment = PaymentFactory(
        unicef_id="RCPT-0520-25-0.000.145",
        fsp_auth_code="0486455966",
    )
    data_file = WesternUnionData.objects.create(name="QCF-skip-missing.zip")
    existing_row = MatchedDataPaymentRow(
        payment=existing_payment,
        mtcn="0486455966",
        transaction_status="2",
        principal_amount=Decimal("262.55"),
        charges_amount=Decimal("7.88"),
        fee_amount=Decimal("0.00"),
    )

    with (
        patch.object(service, "read_rows_from_file_like", return_value=[["header"], ["detail"]]),
        patch.object(
            service,
            "extract_data_rows",
            return_value=[
                [
                    '"1"',
                    '"0486455966"',
                    "1250812",
                    '"00"',
                    '"P"',
                    '"08:02:50"',
                    "0",
                    '"BW"',
                    '"XXX\\YYY"',
                    '"PT-0520-25-0.000.145"',
                    "262.55",
                    "7.88",
                    "0.00",
                    '""',
                    '""',
                    "0",
                    '""',
                    '""',
                    '"2"',
                    '""',
                ],
                [
                    '"1"',
                    '"9999999999"',
                    "1250812",
                    '"00"',
                    '"P"',
                    '"08:02:51"',
                    "0",
                    '"BW"',
                    '"MISS\\ING"',
                    '"PT-0520-25-0.000.999"',
                    "100.00",
                    "1.00",
                    "0.00",
                    '""',
                    '""',
                    "0",
                    '""',
                    '""',
                    '"2"',
                    '""',
                ],
            ],
        ),
        patch.object(service, "aggregate_data_payment_row", return_value=existing_row),
    ):
        service.attach_file(data_file, "QCF-skip-missing.zip", io.BytesIO(b"content"))
        payment_map = service.extract_data_payment_rows(data_file)

    assert payment_map == {str(existing_payment.parent_id): [existing_row]}


def test_extract_data_payment_rows_groups_aggregated_rows_by_payment_plan(
    service: QCFReportsService,
    one_day: timedelta,
    sample_file: Callable[[str], io.BytesIO],
    build_zip_file: Callable[[str, str | bytes], io.BytesIO],
    build_payment_row: Callable[[], MatchedDataPaymentRow],
) -> None:
    payment = PaymentFactory(
        unicef_id="RCPT-3900-26-0.004.911",
        fsp_auth_code="0188322767",
    )
    data_file = WesternUnionData.objects.create(name="QCF-grouped.zip")
    aggregated_row = MatchedDataPaymentRow(
        payment=payment,
        mtcn="0188322767",
        transaction_status="7",
        principal_amount=Decimal("10.00"),
        charges_amount=Decimal("1.00"),
        fee_amount=Decimal("0.00"),
    )

    with (
        patch.object(service, "read_rows_from_file_like", return_value=[["header"], ["detail"]]),
        patch.object(
            service,
            "extract_data_rows",
            return_value=[
                [
                    '"1"',
                    '"0188322767"',
                    "1260319",
                    '"01"',
                    '"P"',
                    '"12:17:32"',
                    "0",
                    '"US"',
                    '"ALUSINE\\\\KARGBO"',
                    '"PT-3900-26-0.004.911"',
                    "10.00",
                    "1.00",
                    "0.00",
                    '""',
                    '""',
                    "0",
                    '""',
                    '""',
                    '"7"',
                    '""',
                ]
            ],
        ),
        patch("hope.apps.payment.services.qcf_reports_service.Payment.objects.get", return_value=payment),
        patch.object(service, "aggregate_data_payment_row", return_value=aggregated_row) as aggregate_mock,
    ):
        service.attach_file(data_file, "QCF-grouped.zip", io.BytesIO(b"content"))
        payment_map = service.extract_data_payment_rows(data_file)

    aggregate_mock.assert_called_once()
    assert payment_map == {str(payment.parent_id): [aggregated_row]}


def test_aggregate_data_payment_row_raises_for_inconsistent_mtcns(
    service: QCFReportsService,
    one_day: timedelta,
    sample_file: Callable[[str], io.BytesIO],
    build_zip_file: Callable[[str, str | bytes], io.BytesIO],
    build_payment_row: Callable[[], MatchedDataPaymentRow],
) -> None:
    payment = PaymentFactory(unicef_id="RCPT-3900-26-0.004.911")
    payment_rows = [
        [
            '"1"',
            '"111"',
            "1",
            '"01"',
            '"P"',
            '"1"',
            "0",
            '"US"',
            '"A"',
            '"PT-3900-26-0.004.911"',
            "1",
            "0",
            "0",
            '""',
            '""',
            "0",
            '""',
            '""',
            '"2"',
            '""',
        ],
        [
            '"1"',
            '"222"',
            "1",
            '"01"',
            '"P"',
            '"1"',
            "0",
            '"US"',
            '"A"',
            '"PT-3900-26-0.004.911"',
            "1",
            "0",
            "0",
            '""',
            '""',
            "0",
            '""',
            '""',
            '"2"',
            '""',
        ],
    ]

    with pytest.raises(
        service.QCFReportsServiceError,
        match=re.escape("Inconsistent MTCN values found for payment RCPT-3900-26-0.004.911"),
    ):
        service.aggregate_data_payment_row("RCPT-3900-26-0.004.911", payment, payment_rows)


def test_aggregate_data_payment_row_prefers_record_type_three_and_sums_amounts(
    service: QCFReportsService,
    one_day: timedelta,
    sample_file: Callable[[str], io.BytesIO],
    build_zip_file: Callable[[str, str | bytes], io.BytesIO],
    build_payment_row: Callable[[], MatchedDataPaymentRow],
) -> None:
    payment = PaymentFactory(
        unicef_id="RCPT-3900-26-0.004.911",
        fsp_auth_code="0188322767",
    )
    payment_rows = [
        [
            '"2"',
            '"0188322767"',
            "1260319",
            '"01"',
            '"O"',
            '"12:17:32"',
            "0",
            '"US"',
            '"ALUSINE\\KARGBO"',
            '"PT-3900-26-0.004.911"',
            "-32.70",
            "-1.00",
            "0.00",
            '""',
            '""',
            "0",
            '""',
            '""',
            '"2"',
            '"REP"',
        ],
        [
            '"3"',
            '"0188322767"',
            "1260319",
            '"01"',
            '"P"',
            '"12:17:32"',
            "1260419",
            '"US"',
            '"ALUSINE\\KARGBO"',
            '"PT-3900-26-0.004.911"',
            "0.00",
            "1.00",
            "0.00",
            '""',
            '""',
            "0",
            '""',
            '""',
            '"7"',
            '"REP"',
        ],
    ]

    aggregated_row = service.aggregate_data_payment_row(
        "RCPT-3900-26-0.004.911",
        payment,
        payment_rows,
    )

    assert aggregated_row.mtcn == "0188322767"
    assert aggregated_row.transaction_status == "7"
    assert aggregated_row.principal_amount == Decimal("-32.70")
    assert aggregated_row.charges_amount == Decimal("0.00")
    assert aggregated_row.fee_amount == Decimal("0.00")


def test_record_type_rank_uses_expected_order(
    service: QCFReportsService,
    one_day: timedelta,
    sample_file: Callable[[str], io.BytesIO],
    build_zip_file: Callable[[str, str | bytes], io.BytesIO],
    build_payment_row: Callable[[], MatchedDataPaymentRow],
) -> None:
    assert service.record_type_rank("3") > service.record_type_rank("1")
    assert service.record_type_rank("1") > service.record_type_rank("2")
    with pytest.raises(service.QCFReportsServiceError, match=re.escape("Unexpected record type 4")):
        service.record_type_rank("4")
    with pytest.raises(service.QCFReportsServiceError, match=re.escape("Unexpected record type x")):
        service.record_type_rank("x")


def test_pick_best_data_match_returns_single_candidate(
    service: QCFReportsService,
    one_day: timedelta,
    sample_file: Callable[[str], io.BytesIO],
    build_zip_file: Callable[[str, str | bytes], io.BytesIO],
    build_payment_row: Callable[[], MatchedDataPaymentRow],
) -> None:
    invoice = WesternUnionInvoice.objects.create(name="AD-AUS001029-SL-20260105.ZIP", net_amount=Decimal("10.00"))
    candidate = WesternUnionData.objects.create(
        name="QCF-AUS001029-SL-20260105.ZIP",
        amount=Decimal("10.00"),
        status=WesternUnionData.STATUS_PENDING,
    )

    assert service.pick_best_data_match(invoice, [candidate]) == candidate


def test_attach_file_sets_file_on_record(
    service: QCFReportsService,
    one_day: timedelta,
    sample_file: Callable[[str], io.BytesIO],
    build_zip_file: Callable[[str, str | bytes], io.BytesIO],
    build_payment_row: Callable[[], MatchedDataPaymentRow],
) -> None:
    invoice = WesternUnionInvoice.objects.create(name="AD-attach.zip")

    service.attach_file(invoice, "AD-attach.zip", io.BytesIO(b"hello"))

    invoice.refresh_from_db()
    assert invoice.file is not None
    assert invoice.file.file.name.endswith("AD-attach.zip")


def test_mark_record_error_sets_status_and_error_msg(
    service: QCFReportsService,
    one_day: timedelta,
    sample_file: Callable[[str], io.BytesIO],
    build_zip_file: Callable[[str, str | bytes], io.BytesIO],
    build_payment_row: Callable[[], MatchedDataPaymentRow],
) -> None:
    invoice = WesternUnionInvoice.objects.create(name="AD-error.zip")

    with patch("hope.apps.payment.services.qcf_reports_service.logger.exception") as exception_mock:
        service.mark_record_error(invoice, ValueError("boom"))

    invoice.refresh_from_db()
    assert invoice.status == WesternUnionInvoice.STATUS_ERROR
    assert invoice.error_msg == "boom"
    exception_mock.assert_called_once()


def test_parse_invoice_file_returns_expected_result(
    service: QCFReportsService,
    one_day: timedelta,
    sample_file: Callable[[str], io.BytesIO],
    build_zip_file: Callable[[str, str | bytes], io.BytesIO],
    build_payment_row: Callable[[], MatchedDataPaymentRow],
) -> None:
    with (
        patch.object(service, "parse_date_from_filename", return_value=date(2025, 1, 1)),
        patch.object(service, "extract_pdf_from_archive", return_value=("AdviceName", b"%PDF")),
        patch.object(service, "extract_text_from_pdf", return_value="pdf text"),
        patch.object(service, "parse_principal_amount_from_pdf_text", return_value=Decimal("1190.32")),
        patch.object(service, "parse_charges_amount_from_pdf_text", return_value=Decimal("35.72")),
    ):
        result = service.parse_invoice_file("AD-123-XYZ-20250101.zip", io.BytesIO(b"zip"))

    assert result == InvoiceParseResult(
        date=date(2025, 1, 1),
        advice_name="AdviceName",
        net_amount=Decimal("1190.32"),
        charges=Decimal("35.72"),
    )


def test_parse_invoice_file_raises_when_advice_name_is_missing(
    service: QCFReportsService,
    one_day: timedelta,
    sample_file: Callable[[str], io.BytesIO],
    build_zip_file: Callable[[str, str | bytes], io.BytesIO],
    build_payment_row: Callable[[], MatchedDataPaymentRow],
) -> None:
    with (
        patch.object(service, "parse_date_from_filename", return_value=date(2025, 1, 1)),
        patch.object(service, "extract_pdf_from_archive", return_value=("", b"%PDF")),
        patch.object(service, "extract_text_from_pdf", return_value="pdf text"),
        patch.object(service, "parse_principal_amount_from_pdf_text", return_value=Decimal("1190.32")),
        patch.object(service, "parse_charges_amount_from_pdf_text", return_value=Decimal("35.72")),
    ):
        with pytest.raises(
            service.QCFReportsServiceError,
            match=re.escape("No advice filename found in invoice file AD-123-XYZ-20250101.zip"),
        ):
            service.parse_invoice_file("AD-123-XYZ-20250101.zip", io.BytesIO(b"zip"))


def test_parse_data_file_extracts_footer_total(
    service: QCFReportsService,
    one_day: timedelta,
    sample_file: Callable[[str], io.BytesIO],
    build_zip_file: Callable[[str, str | bytes], io.BytesIO],
    build_payment_row: Callable[[], MatchedDataPaymentRow],
) -> None:
    result = service.parse_data_file(
        "QCF-123-XYZ-20250101.zip",
        sample_file("QCF-123-XYZ-20250101.zip"),
    )

    assert result == DataParseResult(date=date(2025, 1, 1), amount=Decimal("1190.32"))


def test_parse_date_from_filename_raises_for_invalid_name(
    service: QCFReportsService,
    one_day: timedelta,
    sample_file: Callable[[str], io.BytesIO],
    build_zip_file: Callable[[str, str | bytes], io.BytesIO],
    build_payment_row: Callable[[], MatchedDataPaymentRow],
) -> None:
    with pytest.raises(
        service.QCFReportsServiceError, match=re.escape("Could not parse date from filename invalid.zip")
    ):
        service.parse_date_from_filename("invalid.zip")


def test_read_rows_from_file_like_raises_for_empty_file(
    service: QCFReportsService,
    one_day: timedelta,
    sample_file: Callable[[str], io.BytesIO],
    build_zip_file: Callable[[str, str | bytes], io.BytesIO],
    build_payment_row: Callable[[], MatchedDataPaymentRow],
) -> None:
    with pytest.raises(service.QCFReportsServiceError, match=re.escape("File empty.cf is empty")):
        service.read_rows_from_file_like("empty.cf", io.BytesIO())


def test_read_rows_from_file_like_reads_plain_utf8_csv(
    service: QCFReportsService,
    one_day: timedelta,
    sample_file: Callable[[str], io.BytesIO],
    build_zip_file: Callable[[str, str | bytes], io.BytesIO],
    build_payment_row: Callable[[], MatchedDataPaymentRow],
) -> None:
    rows = service.read_rows_from_file_like("plain.cf", io.BytesIO(b"a,b\n1,2\n"))

    assert rows == [["a", "b"], ["1", "2"]]


def test_read_rows_from_zip_raises_when_archive_has_no_cf_files(
    service: QCFReportsService,
    one_day: timedelta,
    sample_file: Callable[[str], io.BytesIO],
    build_zip_file: Callable[[str, str | bytes], io.BytesIO],
    build_payment_row: Callable[[], MatchedDataPaymentRow],
) -> None:
    archive = build_zip_file("note.txt", "hello")

    with pytest.raises(
        service.QCFReportsServiceError, match=re.escape("No supported text files found in archive bad.zip")
    ):
        service.read_rows_from_zip("bad.zip", archive.getvalue())


def test_read_rows_from_zip_skips_invalid_cf_and_uses_next_candidate(
    service: QCFReportsService,
    one_day: timedelta,
    sample_file: Callable[[str], io.BytesIO],
    build_zip_file: Callable[[str, str | bytes], io.BytesIO],
    build_payment_row: Callable[[], MatchedDataPaymentRow],
) -> None:
    archive = io.BytesIO()
    with zipfile.ZipFile(archive, "w") as zipped:
        zipped.writestr("bad.cf", b"\xff")
        zipped.writestr("good.cf", "a,b\n1,2\n")
    archive.seek(0)

    rows = service.read_rows_from_zip("mixed.zip", archive.getvalue())

    assert rows == [["a", "b"], ["1", "2"]]


def test_read_rows_from_zip_raises_when_all_candidates_are_invalid(
    service: QCFReportsService,
    one_day: timedelta,
    sample_file: Callable[[str], io.BytesIO],
    build_zip_file: Callable[[str, str | bytes], io.BytesIO],
    build_payment_row: Callable[[], MatchedDataPaymentRow],
) -> None:
    archive = io.BytesIO()
    with zipfile.ZipFile(archive, "w") as zipped:
        zipped.writestr("bad-1.cf", b"\xff")
        zipped.writestr("bad-2.cf", b"\xfe")
    archive.seek(0)

    with pytest.raises(
        service.QCFReportsServiceError, match=re.escape("Could not parse any supported archive member in bad.zip")
    ):
        service.read_rows_from_zip("bad.zip", archive.getvalue())


def test_extract_pdf_from_archive_returns_pdf_name_and_bytes(
    service: QCFReportsService,
    one_day: timedelta,
    sample_file: Callable[[str], io.BytesIO],
    build_zip_file: Callable[[str, str | bytes], io.BytesIO],
    build_payment_row: Callable[[], MatchedDataPaymentRow],
) -> None:
    archive = io.BytesIO()
    with zipfile.ZipFile(archive, "w") as zipped:
        zipped.writestr("nested/AdviceName.pdf", b"%PDF-1.4")
    archive.seek(0)

    advice_name, pdf_bytes = service.extract_pdf_from_archive("invoice.zip", archive.getvalue())

    assert advice_name == "AdviceName"
    assert pdf_bytes == b"%PDF-1.4"


def test_extract_pdf_from_archive_raises_when_archive_has_no_pdf(
    service: QCFReportsService,
    one_day: timedelta,
    sample_file: Callable[[str], io.BytesIO],
    build_zip_file: Callable[[str, str | bytes], io.BytesIO],
    build_payment_row: Callable[[], MatchedDataPaymentRow],
) -> None:
    archive = build_zip_file("note.txt", "hello")

    with pytest.raises(service.QCFReportsServiceError, match=re.escape("No PDF advice file found in archive bad.zip")):
        service.extract_pdf_from_archive("bad.zip", archive.getvalue())


def test_extract_pdf_from_archive_raises_when_multiple_pdfs_exist(
    service: QCFReportsService,
    one_day: timedelta,
    sample_file: Callable[[str], io.BytesIO],
    build_zip_file: Callable[[str, str | bytes], io.BytesIO],
    build_payment_row: Callable[[], MatchedDataPaymentRow],
) -> None:
    archive = io.BytesIO()
    with zipfile.ZipFile(archive, "w") as zipped:
        zipped.writestr("one.pdf", b"1")
        zipped.writestr("two.pdf", b"2")
    archive.seek(0)

    with pytest.raises(
        service.QCFReportsServiceError, match=re.escape("More than one PDF advice file found in archive multi.zip")
    ):
        service.extract_pdf_from_archive("multi.zip", archive.getvalue())


def test_extract_text_from_pdf_raises_when_reader_fails(
    service: QCFReportsService,
    one_day: timedelta,
    sample_file: Callable[[str], io.BytesIO],
    build_zip_file: Callable[[str, str | bytes], io.BytesIO],
    build_payment_row: Callable[[], MatchedDataPaymentRow],
) -> None:
    with (
        patch("hope.apps.payment.services.qcf_reports_service.PdfReader", side_effect=ValueError("bad pdf")),
        pytest.raises(
            service.QCFReportsServiceError,
            match=re.escape("Could not extract text from Western Union AD PDF in file.pdf: bad pdf"),
        ),
    ):
        service.extract_text_from_pdf("file.pdf", b"%PDF")


def test_extract_text_from_pdf_raises_when_no_text_is_extracted(
    service: QCFReportsService,
    one_day: timedelta,
    sample_file: Callable[[str], io.BytesIO],
    build_zip_file: Callable[[str, str | bytes], io.BytesIO],
    build_payment_row: Callable[[], MatchedDataPaymentRow],
) -> None:
    page = Mock()
    page.extract_text.return_value = ""
    pdf_reader = Mock()
    pdf_reader.pages = [page]

    with (
        patch("hope.apps.payment.services.qcf_reports_service.PdfReader", return_value=pdf_reader),
        pytest.raises(
            service.QCFReportsServiceError, match=re.escape("No text extracted from Western Union AD PDF in file.pdf")
        ),
    ):
        service.extract_text_from_pdf("file.pdf", b"%PDF")


def test_extract_text_from_pdf_returns_joined_text(
    service: QCFReportsService,
    one_day: timedelta,
    sample_file: Callable[[str], io.BytesIO],
    build_zip_file: Callable[[str, str | bytes], io.BytesIO],
    build_payment_row: Callable[[], MatchedDataPaymentRow],
) -> None:
    first_page = Mock()
    first_page.extract_text.return_value = "first"
    second_page = Mock()
    second_page.extract_text.return_value = "second"
    pdf_reader = Mock()
    pdf_reader.pages = [first_page, second_page]

    with patch("hope.apps.payment.services.qcf_reports_service.PdfReader", return_value=pdf_reader):
        extracted_text = service.extract_text_from_pdf("file.pdf", b"%PDF")

    assert extracted_text == "first\nsecond"


def test_decode_rows_raises_for_non_utf8_bytes(
    service: QCFReportsService,
    one_day: timedelta,
    sample_file: Callable[[str], io.BytesIO],
    build_zip_file: Callable[[str, str | bytes], io.BytesIO],
    build_payment_row: Callable[[], MatchedDataPaymentRow],
) -> None:
    with pytest.raises(service.QCFReportsServiceError, match=re.escape("Could not decode file bad.cf as UTF-8")):
        service.decode_rows("bad.cf", b"\xff")


def test_extract_data_rows_raises_when_rows_are_missing(
    service: QCFReportsService,
    one_day: timedelta,
    sample_file: Callable[[str], io.BytesIO],
    build_zip_file: Callable[[str, str | bytes], io.BytesIO],
    build_payment_row: Callable[[], MatchedDataPaymentRow],
) -> None:
    with pytest.raises(service.QCFReportsServiceError, match=re.escape("Data file file.cf has no rows")):
        service.extract_data_rows([], "file.cf")


def test_extract_data_rows_raises_when_no_detail_rows_exist(
    service: QCFReportsService,
    one_day: timedelta,
    sample_file: Callable[[str], io.BytesIO],
    build_zip_file: Callable[[str, str | bytes], io.BytesIO],
    build_payment_row: Callable[[], MatchedDataPaymentRow],
) -> None:
    with pytest.raises(service.QCFReportsServiceError, match=re.escape("Data file file.cf has no data rows")):
        service.extract_data_rows([["header"], ['"9"', "1", "2", "3", "4"]], "file.cf")


def test_extract_data_rows_raises_when_detail_row_is_too_short(
    service: QCFReportsService,
    one_day: timedelta,
    sample_file: Callable[[str], io.BytesIO],
    build_zip_file: Callable[[str, str | bytes], io.BytesIO],
    build_payment_row: Callable[[], MatchedDataPaymentRow],
) -> None:
    with pytest.raises(service.QCFReportsServiceError, match=re.escape("Invalid data row length in file file.cf")):
        service.extract_data_rows([["header"], ['"1"', "short"]], "file.cf")


def test_extract_footer_row_raises_when_footer_is_missing(
    service: QCFReportsService,
    one_day: timedelta,
    sample_file: Callable[[str], io.BytesIO],
    build_zip_file: Callable[[str, str | bytes], io.BytesIO],
    build_payment_row: Callable[[], MatchedDataPaymentRow],
) -> None:
    with pytest.raises(service.QCFReportsServiceError, match=re.escape("Data file file.cf has no footer row")):
        service.extract_footer_row([["header"], ['"1"', "detail"]], "file.cf")


def test_extract_footer_row_raises_when_multiple_footers_exist(
    service: QCFReportsService,
    one_day: timedelta,
    sample_file: Callable[[str], io.BytesIO],
    build_zip_file: Callable[[str, str | bytes], io.BytesIO],
    build_payment_row: Callable[[], MatchedDataPaymentRow],
) -> None:
    with pytest.raises(
        service.QCFReportsServiceError, match=re.escape("Data file file.cf has more than one footer row")
    ):
        service.extract_footer_row([["header"], ['"9"', "1", "2", "3", "4"], ['"9"', "1", "2", "3", "4"]], "file.cf")


def test_extract_footer_row_raises_when_footer_is_too_short(
    service: QCFReportsService,
    one_day: timedelta,
    sample_file: Callable[[str], io.BytesIO],
    build_zip_file: Callable[[str, str | bytes], io.BytesIO],
    build_payment_row: Callable[[], MatchedDataPaymentRow],
) -> None:
    with pytest.raises(
        service.QCFReportsServiceError, match=re.escape("Invalid data footer row length in file file.cf")
    ):
        service.extract_footer_row([["header"], ['"9"', "1", "2"]], "file.cf")


def test_clean_field(
    service: QCFReportsService,
    one_day: timedelta,
    sample_file: Callable[[str], io.BytesIO],
    build_zip_file: Callable[[str, str | bytes], io.BytesIO],
    build_payment_row: Callable[[], MatchedDataPaymentRow],
) -> None:
    assert service.clean_field(' "abc" ') == "abc"


def test_normalize_payment_unicef_id(
    service: QCFReportsService,
    one_day: timedelta,
    sample_file: Callable[[str], io.BytesIO],
    build_zip_file: Callable[[str, str | bytes], io.BytesIO],
    build_payment_row: Callable[[], MatchedDataPaymentRow],
) -> None:
    assert service.normalize_payment_unicef_id("RCPT-123") == "RCPT-123"
    assert service.normalize_payment_unicef_id("PT-123") == "RCPT-123"
    with pytest.raises(service.QCFReportsServiceError, match=re.escape("Unsupported payment reference XX-123")):
        service.normalize_payment_unicef_id("XX-123")


def test_to_decimal_raises_for_invalid_value(
    service: QCFReportsService,
    one_day: timedelta,
    sample_file: Callable[[str], io.BytesIO],
    build_zip_file: Callable[[str, str | bytes], io.BytesIO],
    build_payment_row: Callable[[], MatchedDataPaymentRow],
) -> None:
    with pytest.raises(service.QCFReportsServiceError, match=re.escape("Could not parse decimal value abc")):
        service.to_decimal("abc")


def test_parse_principal_amount_from_pdf_text(
    service: QCFReportsService,
    one_day: timedelta,
    sample_file: Callable[[str], io.BytesIO],
    build_zip_file: Callable[[str, str | bytes], io.BytesIO],
    build_payment_row: Callable[[], MatchedDataPaymentRow],
) -> None:
    assert service.parse_principal_amount_from_pdf_text("Principal 1,190.32", "ad.zip") == Decimal("1190.32")
    with pytest.raises(
        service.QCFReportsServiceError, match=re.escape("Could not parse principal amount from AD PDF in ad.zip")
    ):
        service.parse_principal_amount_from_pdf_text("missing", "ad.zip")


def test_parse_charges_amount_from_pdf_text(
    service: QCFReportsService,
    one_day: timedelta,
    sample_file: Callable[[str], io.BytesIO],
    build_zip_file: Callable[[str, str | bytes], io.BytesIO],
    build_payment_row: Callable[[], MatchedDataPaymentRow],
) -> None:
    assert service.parse_charges_amount_from_pdf_text("Charges 35.72") == Decimal("35.72")
    assert service.parse_charges_amount_from_pdf_text("missing") == Decimal("0.00")


def test_payment_plan_data_post_init_tracks_principal_charges_refunds_and_fees(
    service: QCFReportsService,
    one_day: timedelta,
    sample_file: Callable[[str], io.BytesIO],
    build_zip_file: Callable[[str, str | bytes], io.BytesIO],
    build_payment_row: Callable[[], MatchedDataPaymentRow],
) -> None:
    report_data = QCFReportPaymentPlanData(
        payment_plan_unicef_id="PP-1",
        payments_data=[
            QCFReportPaymentRowData(
                payment_unicef_id="RCPT-1",
                mtcn="MTCN-1",
                mtcns_match=True,
                hope_mtcn="MTCN-1",
                payment_plan_unicef_id="PP-1",
                programme="Programme",
                fc="FC-1",
                principal_amount=100.0,
                charges_amount=3.0,
                fee_amount=1.5,
                ad_name_value="Advice-1",
            ),
            QCFReportPaymentRowData(
                payment_unicef_id="RCPT-2",
                mtcn="MTCN-2",
                mtcns_match=False,
                hope_mtcn="MTCN-X",
                payment_plan_unicef_id="PP-1",
                programme="Programme",
                fc="FC-1",
                principal_amount=-50.0,
                charges_amount=2.0,
                fee_amount=0.5,
                ad_name_value="Advice-1",
            ),
        ],
    )

    assert report_data.principal_total == 100.0
    assert report_data.charges_total == 5.0
    assert report_data.refunds_total == -50.0
    assert report_data.fees_total == 2.0


def test_generate_report_xlsx_contains_headers_and_totals(
    service: QCFReportsService,
    one_day: timedelta,
    sample_file: Callable[[str], io.BytesIO],
    build_zip_file: Callable[[str, str | bytes], io.BytesIO],
    build_payment_row: Callable[[], MatchedDataPaymentRow],
) -> None:
    report_data = QCFReportPaymentPlanData(
        payment_plan_unicef_id="PP-1",
        payments_data=[
            QCFReportPaymentRowData(
                payment_unicef_id="RCPT-1",
                mtcn="MTCN-1",
                mtcns_match=True,
                hope_mtcn="MTCN-1",
                payment_plan_unicef_id="PP-1",
                programme="Programme",
                fc="FC1/001",
                principal_amount=100.0,
                charges_amount=3.0,
                fee_amount=0.0,
                ad_name_value="Advice",
            )
        ],
    )

    workbook = service.generate_report_xlsx(report_data)
    worksheet = workbook.active

    assert worksheet.title == "QCF Report - PP-1"
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
    assert worksheet["K2"].value == "Advice"
    assert worksheet["A4"].value == "Principal Total"
    assert worksheet["E4"].value == 100.0
    assert worksheet["A5"].value == "Charges Total"
    assert worksheet["E5"].value == 3.0
    assert worksheet["A6"].value == "Refunds Total"
    assert worksheet["E6"].value == 0


def test_generate_reports_for_invoice_creates_report_and_registers_notification_callback(
    service: QCFReportsService,
    one_day: timedelta,
    sample_file: Callable[[str], io.BytesIO],
    build_zip_file: Callable[[str, str | bytes], io.BytesIO],
    build_payment_row: Callable[[], MatchedDataPaymentRow],
) -> None:
    payment = PaymentFactory(unicef_id="RCPT-1", fsp_auth_code="MTCN-1")
    invoice = WesternUnionInvoice.objects.create(
        name="AD-AUS001029-SL-20260106.ZIP",
        advice_name="Advice-20260106",
    )
    payment_map = {
        str(payment.parent_id): [
            MatchedDataPaymentRow(
                payment=payment,
                mtcn="MTCN-1",
                transaction_status="2",
                principal_amount=Decimal("100.00"),
                charges_amount=Decimal("3.00"),
                fee_amount=Decimal("0.00"),
            )
        ]
    }

    with (
        patch("hope.apps.payment.services.qcf_reports_service.transaction.on_commit") as on_commit_mock,
        patch(
            "hope.apps.payment.services.qcf_reports_service.send_qcf_report_email_notifications_async_task"
        ) as task_mock,
    ):
        service.generate_reports_for_invoice(invoice, payment_map, send_notifications=True)
        report = invoice.reports.get()
        on_commit_mock.assert_called_once()
        callback = on_commit_mock.call_args.args[0]
        callback()
        task_mock.assert_called_once_with(str(report.id))

    assert report.payment_plan_id == payment.parent_id
    assert report.report_file is not None


def test_generate_reports_for_invoice_skips_notification_callback_when_disabled(
    service: QCFReportsService,
    one_day: timedelta,
    sample_file: Callable[[str], io.BytesIO],
    build_zip_file: Callable[[str, str | bytes], io.BytesIO],
    build_payment_row: Callable[[], MatchedDataPaymentRow],
) -> None:
    payment = PaymentFactory(unicef_id="RCPT-2", fsp_auth_code="MTCN-2")
    invoice = WesternUnionInvoice.objects.create(
        name="AD-AUS001029-SL-20260107.ZIP",
        advice_name="Advice-20260107",
    )
    payment_map = {
        str(payment.parent_id): [
            MatchedDataPaymentRow(
                payment=payment,
                mtcn="MTCN-2",
                transaction_status="2",
                principal_amount=Decimal("50.00"),
                charges_amount=Decimal("1.00"),
                fee_amount=Decimal("0.00"),
            )
        ]
    }

    with patch("hope.apps.payment.services.qcf_reports_service.transaction.on_commit") as on_commit_mock:
        service.generate_reports_for_invoice(invoice, payment_map, send_notifications=False)

    report = invoice.reports.get()
    assert report.report_file is not None
    on_commit_mock.assert_not_called()


def test_generate_report_uses_payment_plan_data(
    service: QCFReportsService,
    one_day: timedelta,
    sample_file: Callable[[str], io.BytesIO],
    build_zip_file: Callable[[str, str | bytes], io.BytesIO],
    build_payment_row: Callable[[], MatchedDataPaymentRow],
) -> None:
    payment = PaymentFactory(unicef_id="RCPT-1", fsp_auth_code="MTCN-1")
    payment_rows = [
        MatchedDataPaymentRow(
            payment=payment,
            mtcn="MTCN-1",
            transaction_status="2",
            principal_amount=Decimal("100.00"),
            charges_amount=Decimal("3.00"),
            fee_amount=Decimal("0.00"),
        )
    ]

    filename, workbook = service.generate_report(payment.parent, payment_rows, "Advice")

    assert filename.startswith(f"QCF_{payment.parent.business_area.slug}_{payment.parent.unicef_id}_")
    assert workbook.active["K2"].value == "Advice"


def test_generate_report_marks_mtcn_mismatch_in_workbook(
    service: QCFReportsService,
    one_day: timedelta,
    sample_file: Callable[[str], io.BytesIO],
    build_zip_file: Callable[[str, str | bytes], io.BytesIO],
    build_payment_row: Callable[[], MatchedDataPaymentRow],
) -> None:
    payment = PaymentFactory(unicef_id="RCPT-3", fsp_auth_code="EXPECTED")
    payment_rows = [
        MatchedDataPaymentRow(
            payment=payment,
            mtcn="ACTUAL",
            transaction_status="2",
            principal_amount=Decimal("25.00"),
            charges_amount=Decimal("1.00"),
            fee_amount=Decimal("0.00"),
        )
    ]

    _, workbook = service.generate_report(payment.parent, payment_rows, "Advice")

    assert workbook.active["C2"].value is False


def test_send_notification_emails_sends_to_users_with_permission(
    service: QCFReportsService,
    one_day: timedelta,
    sample_file: Callable[[str], io.BytesIO],
    build_zip_file: Callable[[str, str | bytes], io.BytesIO],
    build_payment_row: Callable[[], MatchedDataPaymentRow],
) -> None:
    report = WesternUnionPaymentPlanReportFactory(
        payment_plan=PaymentPlanFactory(),
    )
    user = UserFactory()
    report.report_file = FileTempFactory(file=SimpleUploadedFile("qcf.xlsx", b"test"))
    report.save(update_fields=["report_file"])

    with (
        patch("hope.apps.payment.services.qcf_reports_service.User.objects.all", return_value=[user]),
        patch.object(user, "has_perm", return_value=True),
        patch.object(user, "email_user") as email_user_mock,
        patch(
            "hope.apps.payment.services.qcf_reports_service.render_to_string",
            side_effect=["rendered-html", "rendered-text"],
        ) as render_to_string_mock,
        patch("hope.apps.payment.services.qcf_reports_service.reverse", return_value="/download/report"),
        patch(
            "hope.apps.payment.services.qcf_reports_service.get_link",
            side_effect=lambda path: f"https://example.com{path}",
        ),
    ):
        service.send_notification_emails(report)

    email_user_mock.assert_called_once()
    render_to_string_mock.assert_any_call(
        "payment/qcf_report_email.html",
        context={
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "message": f"Payment Plan: https://example.com/{report.payment_plan.business_area.slug}/programs/"
            f"{report.payment_plan.program.code}/payment-module/payment-plans/{report.payment_plan.id}",
            "title": f"Payment Plan {report.report_file.file.name} Western Union QCF Report",
            "link": "Western Union QCF Report file: https://example.com/download/report",
        },
    )


def test_send_notification_emails_skips_when_no_users_have_permission(
    service: QCFReportsService,
    one_day: timedelta,
    sample_file: Callable[[str], io.BytesIO],
    build_zip_file: Callable[[str, str | bytes], io.BytesIO],
    build_payment_row: Callable[[], MatchedDataPaymentRow],
) -> None:
    report = WesternUnionPaymentPlanReportFactory(
        payment_plan=PaymentPlanFactory(),
    )
    user = UserFactory()

    with (
        patch("hope.apps.payment.services.qcf_reports_service.User.objects.all", return_value=[user]),
        patch.object(user, "has_perm", return_value=False),
        patch.object(user, "email_user") as email_user_mock,
        patch("hope.apps.payment.services.qcf_reports_service.render_to_string") as render_to_string_mock,
    ):
        service.send_notification_emails(report)

    email_user_mock.assert_not_called()
    render_to_string_mock.assert_not_called()
