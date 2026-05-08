from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import patch

from django.test import TestCase
from django.utils import timezone

from extras.test_utils.factories import PaymentFactory
from hope.apps.payment.services.qcf_reports_service import MatchedDataPaymentRow, QCFReportsService
from hope.models import WesternUnionData, WesternUnionInvoice


class TestQCFReportsService(TestCase):
    def setUp(self) -> None:
        self.service = QCFReportsService()
        self.one_day = timedelta(days=1)

    def test_reconcile_invoice_marks_error_when_no_matching_data_file_found_after_grace_period(self) -> None:
        invoice = WesternUnionInvoice.objects.create(
            name="AD-AUS001029-SL-20251115.ZIP",
            advice_name="Advice-20251115",
            date=timezone.now().date() - self.service.UNMATCHED_INVOICE_ERROR_GRACE_PERIOD - self.one_day,
            net_amount=Decimal("100.00"),
        )

        self.service.reconcile_invoice(invoice)

        invoice.refresh_from_db()

        assert invoice.status == WesternUnionInvoice.STATUS_ERROR
        assert invoice.error_msg == "No matching data file found"

    def test_reconcile_invoice_keeps_recent_unmatched_invoice_pending(self) -> None:
        invoice = WesternUnionInvoice.objects.create(
            name="AD-AUS001029-SL-20251115.ZIP",
            advice_name="Advice-20251115",
            date=timezone.now().date(),
            net_amount=Decimal("100.00"),
        )

        self.service.reconcile_invoice(invoice)

        invoice.refresh_from_db()

        assert invoice.status == WesternUnionInvoice.STATUS_PENDING
        assert invoice.error_msg is None

    def test_reconcile_invoice_completes_with_matching_data_file(self) -> None:
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
        payment_map = {"payment-plan-id": [self._build_payment_row()]}

        with (
            patch.object(
                self.service,
                "extract_data_payment_rows",
                return_value=payment_map,
            ) as extract_data_payment_rows_mock,
            patch.object(
                self.service,
                "link_payments_from_data_rows",
            ) as link_payments_from_data_rows_mock,
            patch.object(
                self.service,
                "generate_reports_for_invoice",
            ) as generate_reports_for_invoice_mock,
        ):
            self.service.reconcile_invoice(invoice)

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

    def test_reconcile_invoice_passes_send_notifications_flag_to_report_generation(self) -> None:
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
        payment_map = {"payment-plan-id": [self._build_payment_row()]}

        with (
            patch.object(self.service, "extract_data_payment_rows", return_value=payment_map),
            patch.object(self.service, "link_payments_from_data_rows"),
            patch.object(self.service, "generate_reports_for_invoice") as generate_reports_for_invoice_mock,
        ):
            self.service.reconcile_invoice(invoice, send_notifications=False)

        matched_data.refresh_from_db()

        assert matched_data.status == WesternUnionData.STATUS_COMPLETED
        generate_reports_for_invoice_mock.assert_called_once_with(invoice, payment_map, send_notifications=False)

    def test_reconcile_invoice_marks_error_when_no_valid_payments_found_in_matching_data_file(self) -> None:
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
            self.service,
            "extract_data_payment_rows",
            return_value={},
        ) as extract_data_payment_rows_mock:
            self.service.reconcile_invoice(invoice)

        invoice.refresh_from_db()
        matched_data.refresh_from_db()

        assert invoice.status == WesternUnionInvoice.STATUS_ERROR
        assert invoice.error_msg == "No valid payments found in matching data file"
        assert matched_data.status == WesternUnionData.STATUS_ERROR
        assert matched_data.error_msg == "No valid payments found in matching data file"
        extract_data_payment_rows_mock.assert_called_once_with(matched_data)

    def test_get_matching_data_file_picks_closest_date(self) -> None:
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

        matched_data = self.service.get_matching_data_file(invoice)

        assert matched_data == closer_data
        assert matched_data != farther_data

    def test_reconcile_pending_records_ignores_legacy_invoices(self) -> None:
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

        with patch.object(self.service, "reconcile_invoice") as reconcile_invoice_mock:
            self.service.reconcile_pending_records()

        reconcile_invoice_mock.assert_called_once()
        called_invoice = reconcile_invoice_mock.call_args.args[0]
        assert called_invoice.id == current_invoice.id
        assert called_invoice.id != legacy_invoice.id

    def test_aggregate_data_payment_row_prefers_record_type_three_and_sums_amounts(self) -> None:
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

        aggregated_row = self.service.aggregate_data_payment_row(
            "RCPT-3900-26-0.004.911",
            payment,
            payment_rows,
        )

        assert aggregated_row.mtcn == "0188322767"
        assert aggregated_row.transaction_status == "7"
        assert aggregated_row.principal_amount == Decimal("-32.70")
        assert aggregated_row.charges_amount == Decimal("0.00")
        assert aggregated_row.fee_amount == Decimal("0.00")

    def _build_payment_row(self) -> MatchedDataPaymentRow:
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
