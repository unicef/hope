"""
Backfill Western Union AD invoices for 2026 reprocessing.

Run from Django shell:
    from hope.one_time_scripts.backfill_wu_ad_invoices import backfill_wu_ad_invoices
    backfill_wu_ad_invoices(dry_run=True)
    backfill_wu_ad_invoices(dry_run=False)
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Iterable

from django.db import transaction

from hope.apps.payment.services.qcf_reports_service import InvoiceParseResult, QCFReportsService
from hope.models import WesternUnionData, WesternUnionInvoice


REPROCESS_FROM_DATE = date(2026, 1, 1)


@dataclass
class ParsedInvoiceCandidate:
    filename: str
    parse_result: InvoiceParseResult
    file_like: object


def backfill_wu_ad_invoices(
    dry_run: bool = True,
    invoice_name: str | None = None,
    limit: int | None = None,
) -> None:
    service = QCFReportsService()
    target_data_files = list(get_target_data_files(limit=limit))
    if not target_data_files:
        print("No 2026 Western Union data files require AD invoice backfill.")
        return

    print(f"Target data files: {len(target_data_files)}")
    print(f"Reprocessing from date: {REPROCESS_FROM_DATE}")

    parsed_invoice_candidates = list(load_invoice_candidates(service, invoice_name=invoice_name, limit=limit))
    print(f"Candidate AD invoice files found on FTP: {len(parsed_invoice_candidates)}")

    if dry_run:
        preview_matches(service, parsed_invoice_candidates)
        return

    imported_count = import_invoice_candidates(service, parsed_invoice_candidates)
    print(f"Imported AD invoice files: {imported_count}")

    pending_invoices = (
        WesternUnionInvoice.objects.filter(
            is_legacy=False,
            status=WesternUnionInvoice.STATUS_PENDING,
            date__gte=REPROCESS_FROM_DATE,
        )
        .exclude(advice_name__isnull=True)
        .order_by("date", "id")
    )
    if invoice_name:
        pending_invoices = pending_invoices.filter(name=invoice_name)
    if limit is not None:
        pending_invoices = pending_invoices[:limit]

    for invoice in pending_invoices:
        matched_data = service.get_matching_data_file(invoice, include_completed=True)
        if matched_data is None:
            print(f"[WAITING] {invoice.name}: no matching data file found yet")
            service.reconcile_invoice(invoice, send_notifications=False)
            continue

        print(f"[PROCESS] {invoice.name}: matching {matched_data.name}")
        reconcile_backfill_invoice(service, invoice, matched_data)

    print("Backfill finished.")


def get_target_data_files(limit: int | None = None) -> Iterable[WesternUnionData]:
    queryset = (
        WesternUnionData.objects.exclude(status=WesternUnionData.STATUS_ERROR)
        .exclude(amount__isnull=True)
        .filter(date__gte=REPROCESS_FROM_DATE)
        .order_by("date", "id")
    )

    if limit is not None:
        queryset = queryset[:limit]
    return queryset


def load_invoice_candidates(
    service: QCFReportsService,
    invoice_name: str | None = None,
    limit: int | None = None,
) -> Iterable[ParsedInvoiceCandidate]:
    yielded_count = 0
    for file_attr in service.ftp_client.list_files_w_attrs():
        filename = file_attr.filename
        if not service.ftp_client.INVOICE_PREFIX_PATTERN.match(filename):
            continue
        if invoice_name and filename != invoice_name:
            continue
        if WesternUnionInvoice.objects.filter(name=filename).exists():
            continue

        try:
            file_date = service.parse_date_from_filename(filename)
            if file_date < REPROCESS_FROM_DATE:
                continue

            file_like = service.ftp_client.download(filename)
            parse_result = service.parse_invoice_file(filename, file_like)
            file_like.seek(0)
        except Exception as exc:
            print(f"[ERROR] Failed to parse FTP invoice candidate {filename}: {exc}")
            continue

        yield ParsedInvoiceCandidate(filename=filename, parse_result=parse_result, file_like=file_like)
        yielded_count += 1
        if limit is not None and yielded_count >= limit:
            return


def preview_matches(
    service: QCFReportsService,
    parsed_invoice_candidates: list[ParsedInvoiceCandidate],
) -> None:
    print("Dry run enabled. No files or database rows will be modified.")
    for candidate in parsed_invoice_candidates:
        matched_data = preview_matching_data_file(service, candidate.parse_result.net_amount, candidate.parse_result.date)
        if matched_data is None:
            print(f"[DRY-RUN][WAITING] {candidate.filename}: no matching data file found yet")
            continue

        print(f"[DRY-RUN] {candidate.filename}: would match data {matched_data.name} (status={matched_data.status})")


def preview_matching_data_file(service: QCFReportsService, amount, invoice_date: date) -> WesternUnionData | None:
    invoice_stub = WesternUnionInvoice(
        name="preview",
        advice_name="preview",
        net_amount=amount,
        date=invoice_date,
        is_legacy=False,
    )
    return service.get_matching_data_file(invoice_stub, include_completed=True)


def import_invoice_candidates(service: QCFReportsService, parsed_invoice_candidates: list[ParsedInvoiceCandidate]) -> int:
    imported_count = 0
    for candidate in parsed_invoice_candidates:
        print(f"[IMPORT] {candidate.filename}")
        service.import_invoice_file(candidate.filename, candidate.file_like)
        imported_count += 1
    return imported_count


def reconcile_backfill_invoice(
    service: QCFReportsService,
    invoice: WesternUnionInvoice,
    matched_data: WesternUnionData,
) -> None:
    mark_matched_data_error = False
    try:
        with transaction.atomic():
            try:
                payment_plan_id_payments_map = service.extract_data_payment_rows(matched_data)
                service.link_payments_from_data_rows(invoice, payment_plan_id_payments_map)
            except Exception as exc:
                mark_matched_data_error = True
                raise exc

            service.generate_reports_for_invoice(
                invoice,
                payment_plan_id_payments_map,
                send_notifications=False,
            )
            invoice.matched_data = matched_data
            invoice.status = WesternUnionInvoice.STATUS_COMPLETED
            invoice.error_msg = ""
            invoice.save(update_fields=["matched_data", "status", "error_msg"])
            matched_data.status = WesternUnionData.STATUS_COMPLETED
            matched_data.error_msg = ""
            matched_data.save(update_fields=["status", "error_msg"])
    except Exception as exc:
        if mark_matched_data_error:
            service.mark_record_error(matched_data, exc)
        service.mark_record_error(invoice, exc)
