from datetime import date
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import Mock, patch

import pytest

from hope.models import WesternUnionData, WesternUnionInvoice
from hope.one_time_scripts.backfill_wu_ad_invoices import (
    REPROCESS_FROM_DATE,
    ParsedInvoiceCandidate,
    backfill_wu_ad_invoices,
    get_target_data_files,
    load_invoice_candidates,
    preview_matching_data_file,
    reconcile_backfill_invoice,
)

pytestmark = pytest.mark.django_db


def test_get_target_data_files_returns_only_2026_non_error_rows_with_amount() -> None:
    excluded_old = WesternUnionData.objects.create(
        name="QCF-AUS001029-SL-20251231.ZIP",
        date=date(2025, 12, 31),
        amount=Decimal("100.00"),
        status=WesternUnionData.STATUS_PENDING,
    )
    included_completed = WesternUnionData.objects.create(
        name="QCF-AUS001029-SL-20260101.ZIP",
        date=REPROCESS_FROM_DATE,
        amount=Decimal("200.00"),
        status=WesternUnionData.STATUS_COMPLETED,
    )
    excluded_error = WesternUnionData.objects.create(
        name="QCF-AUS001029-SL-20260102.ZIP",
        date=date(2026, 1, 2),
        amount=Decimal("300.00"),
        status=WesternUnionData.STATUS_ERROR,
    )
    excluded_missing_amount = WesternUnionData.objects.create(
        name="QCF-AUS001029-SL-20260103.ZIP",
        date=date(2026, 1, 3),
        amount=None,
        status=WesternUnionData.STATUS_PENDING,
    )

    target_rows = list(get_target_data_files())

    assert target_rows == [included_completed]
    assert excluded_old not in target_rows
    assert excluded_error not in target_rows
    assert excluded_missing_amount not in target_rows


def test_load_invoice_candidates_only_returns_2026_ad_files_not_already_imported() -> None:
    existing_invoice = WesternUnionInvoice.objects.create(name="AD-AUS001029-SL-20260116.ZIP")
    service = Mock()
    service.ftp_client.list_files_w_attrs.return_value = [
        SimpleNamespace(filename="QCF-AUS001029-SL-20260115.ZIP"),
        SimpleNamespace(filename="AD-AUS001029-SL-20251231.ZIP"),
        SimpleNamespace(filename=existing_invoice.name),
        SimpleNamespace(filename="AD-AUS001029-SL-20260115.ZIP"),
    ]
    service.ftp_client.INVOICE_PREFIX_PATTERN.match.side_effect = lambda value: value.startswith("AD-")
    service.parse_date_from_filename.side_effect = lambda value: date(
        int(value[-12:-8]),
        int(value[-8:-6]),
        int(value[-6:-4]),
    )
    service.download.return_value = Mock()
    service.parse_invoice_file.return_value = Mock()

    candidates = list(load_invoice_candidates(service))

    assert [candidate.filename for candidate in candidates] == ["AD-AUS001029-SL-20260115.ZIP"]


def test_load_invoice_candidates_respects_invoice_name() -> None:
    service = Mock()
    service.ftp_client.list_files_w_attrs.return_value = [
        SimpleNamespace(filename="AD-AUS001029-SL-20260115.ZIP"),
        SimpleNamespace(filename="AD-AUS001029-SL-20260116.ZIP"),
    ]
    service.ftp_client.INVOICE_PREFIX_PATTERN.match.side_effect = lambda value: value.startswith("AD-")
    service.parse_date_from_filename.side_effect = lambda _value: date(2026, 1, 15)
    service.download.return_value = Mock()
    service.parse_invoice_file.return_value = Mock()

    named_candidates = list(
        load_invoice_candidates(
            service,
            invoice_name="AD-AUS001029-SL-20260116.ZIP",
        )
    )

    assert [candidate.filename for candidate in named_candidates] == ["AD-AUS001029-SL-20260116.ZIP"]


def test_backfill_dry_run_only_previews_matches() -> None:
    WesternUnionData.objects.create(
        name="QCF-AUS001029-SL-20260115.ZIP",
        date=date(2026, 1, 15),
        amount=Decimal("100.00"),
        status=WesternUnionData.STATUS_PENDING,
    )
    service = Mock()
    candidates = [
        ParsedInvoiceCandidate(
            filename="AD-AUS001029-SL-20260115.ZIP",
            parse_result=Mock(net_amount=Decimal("100.00"), date=date(2026, 1, 15)),
            file_like=Mock(),
        )
    ]

    with (
        patch("hope.one_time_scripts.backfill_wu_ad_invoices.QCFReportsService", return_value=service),
        patch("hope.one_time_scripts.backfill_wu_ad_invoices.load_invoice_candidates", return_value=candidates),
        patch("hope.one_time_scripts.backfill_wu_ad_invoices.preview_matches") as preview_matches_mock,
        patch(
            "hope.one_time_scripts.backfill_wu_ad_invoices.import_invoice_candidates"
        ) as import_invoice_candidates_mock,
    ):
        backfill_wu_ad_invoices(dry_run=True)

    preview_matches_mock.assert_called_once_with(service, candidates)
    import_invoice_candidates_mock.assert_not_called()
    service.reconcile_invoice.assert_not_called()


def test_backfill_reprocesses_only_non_legacy_2026_pending_invoices_without_notifications() -> None:
    WesternUnionData.objects.create(
        name="QCF-AUS001029-SL-20260115.ZIP",
        date=date(2026, 1, 15),
        amount=Decimal("100.00"),
        status=WesternUnionData.STATUS_COMPLETED,
    )
    legacy_invoice = WesternUnionInvoice.objects.create(
        name="QCF-AUS001029-SL-20260115.ZIP",
        is_legacy=True,
        status=WesternUnionInvoice.STATUS_COMPLETED,
    )
    old_invoice = WesternUnionInvoice.objects.create(
        name="AD-AUS001029-SL-20251231.ZIP",
        advice_name="Advice-old",
        date=date(2025, 12, 31),
        net_amount=Decimal("100.00"),
        status=WesternUnionInvoice.STATUS_PENDING,
        is_legacy=False,
    )
    waiting_invoice = WesternUnionInvoice.objects.create(
        name="AD-AUS001029-SL-20260114.ZIP",
        advice_name="Advice-waiting",
        date=date(2026, 1, 14),
        net_amount=Decimal("90.00"),
        status=WesternUnionInvoice.STATUS_PENDING,
        is_legacy=False,
    )
    matched_invoice = WesternUnionInvoice.objects.create(
        name="AD-AUS001029-SL-20260115.ZIP",
        advice_name="Advice-new",
        date=date(2026, 1, 15),
        net_amount=Decimal("100.00"),
        status=WesternUnionInvoice.STATUS_PENDING,
        is_legacy=False,
    )

    data_file = WesternUnionData.objects.get(name="QCF-AUS001029-SL-20260115.ZIP")
    service = Mock()
    service.get_matching_data_file.side_effect = [None, data_file]

    with (
        patch("hope.one_time_scripts.backfill_wu_ad_invoices.QCFReportsService", return_value=service),
        patch("hope.one_time_scripts.backfill_wu_ad_invoices.load_invoice_candidates", return_value=[]),
        patch("hope.one_time_scripts.backfill_wu_ad_invoices.import_invoice_candidates", return_value=0),
        patch(
            "hope.one_time_scripts.backfill_wu_ad_invoices.reconcile_backfill_invoice"
        ) as reconcile_backfill_invoice_mock,
    ):
        backfill_wu_ad_invoices(dry_run=False)

    assert service.reconcile_invoice.call_count == 1
    first_invoice = service.reconcile_invoice.call_args_list[0].args[0]
    assert first_invoice.id == waiting_invoice.id
    assert service.get_matching_data_file.call_args_list[0].kwargs == {"include_completed": True}
    assert service.get_matching_data_file.call_args_list[1].kwargs == {"include_completed": True}
    assert service.reconcile_invoice.call_args_list[0].kwargs == {"send_notifications": False}
    reconcile_backfill_invoice_mock.assert_called_once_with(service, matched_invoice, data_file)
    assert legacy_invoice.status == WesternUnionInvoice.STATUS_COMPLETED
    assert old_invoice.status == WesternUnionInvoice.STATUS_PENDING


def test_reconcile_backfill_invoice_processes_completed_data_without_notifications() -> None:
    invoice = WesternUnionInvoice.objects.create(
        name="AD-AUS001029-SL-20260115.ZIP",
        advice_name="Advice-new",
        date=date(2026, 1, 15),
        net_amount=Decimal("100.00"),
        status=WesternUnionInvoice.STATUS_PENDING,
        is_legacy=False,
    )
    matched_data = WesternUnionData.objects.create(
        name="QCF-AUS001029-SL-20260115.ZIP",
        date=date(2026, 1, 15),
        amount=Decimal("100.00"),
        status=WesternUnionData.STATUS_COMPLETED,
    )
    service = Mock()
    payment_map = {"payment-plan-id": [Mock()]}
    service.extract_data_payment_rows.return_value = payment_map

    reconcile_backfill_invoice(service, invoice, matched_data)

    invoice.refresh_from_db()
    matched_data.refresh_from_db()

    service.extract_data_payment_rows.assert_called_once_with(matched_data)
    service.link_payments_from_data_rows.assert_called_once_with(invoice, payment_map)
    service.generate_reports_for_invoice.assert_called_once_with(
        invoice,
        payment_map,
        send_notifications=False,
    )
    assert invoice.status == WesternUnionInvoice.STATUS_COMPLETED
    assert invoice.matched_data == matched_data
    assert matched_data.status == WesternUnionData.STATUS_COMPLETED


def test_backfill_passes_invoice_name_to_candidate_loading_without_filtering_data_rows_by_ad_name() -> None:
    WesternUnionData.objects.create(
        name="QCF-AUS001029-SL-20260115.ZIP",
        date=date(2026, 1, 15),
        amount=Decimal("100.00"),
        status=WesternUnionData.STATUS_PENDING,
    )
    service = Mock()

    with (
        patch("hope.one_time_scripts.backfill_wu_ad_invoices.QCFReportsService", return_value=service),
        patch(
            "hope.one_time_scripts.backfill_wu_ad_invoices.load_invoice_candidates", return_value=[]
        ) as load_candidates_mock,
        patch("hope.one_time_scripts.backfill_wu_ad_invoices.preview_matches"),
    ):
        backfill_wu_ad_invoices(
            dry_run=True,
            invoice_name="AD-AUS001029-SL-20260115.ZIP",
        )

    load_candidates_mock.assert_called_once_with(
        service,
        invoice_name="AD-AUS001029-SL-20260115.ZIP",
    )


def test_preview_matching_data_file_uses_non_legacy_invoice_stub() -> None:
    service = Mock()
    matched_data = WesternUnionData(name="QCF-AUS001029-SL-20260115.ZIP")
    service.get_matching_data_file.return_value = matched_data

    result = preview_matching_data_file(service, Decimal("100.00"), date(2026, 1, 15))

    assert result == matched_data
    invoice_stub = service.get_matching_data_file.call_args.args[0]
    assert invoice_stub.is_legacy is False
    assert service.get_matching_data_file.call_args.kwargs == {"include_completed": True}
