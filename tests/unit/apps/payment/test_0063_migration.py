from datetime import date
import importlib
import io
import os
from types import SimpleNamespace
import zipfile

from django.core.files.base import ContentFile
import pytest

from extras.test_utils.factories import FileTempFactory, WesternUnionInvoiceFactory
from hope.models import WesternUnionData, WesternUnionInvoice

pytestmark = pytest.mark.django_db

migration_module = importlib.import_module("hope.apps.payment.migrations.0063_migration")


def test_migration_creates_pending_data_row_for_2026_legacy_qcf_invoice_and_marks_legacy_completed() -> None:
    legacy_invoice = WesternUnionInvoiceFactory(
        name="QCF-AUS001029-SL-20260115.ZIP",
        file=build_file_temp("sample.zip", build_qcf_archive('"9",10,-228.90,0.00,0.00\n')),
    )

    migration_module.migrate_existing_qcf_invoices_to_wu_data(build_apps(), schema_editor=None)

    legacy_invoice.refresh_from_db()
    migrated_data = WesternUnionData.objects.get(name=legacy_invoice.name)

    assert migrated_data.file_id == legacy_invoice.file_id
    assert migrated_data.date == date(2026, 1, 15)
    assert migrated_data.status == WesternUnionData.STATUS_PENDING
    assert str(migrated_data.amount) == "-228.90"
    assert legacy_invoice.is_legacy is True
    assert legacy_invoice.status == WesternUnionInvoice.STATUS_COMPLETED
    assert legacy_invoice.error_msg == ""


def test_migration_skips_creating_data_row_for_pre_2026_legacy_qcf_invoice() -> None:
    legacy_invoice = WesternUnionInvoiceFactory(
        name="QCF-AUS001029-SL-20251231.ZIP",
        file=build_file_temp("sample.zip", build_qcf_archive('"9",10,-125.00,0.00,0.00\n')),
    )

    migration_module.migrate_existing_qcf_invoices_to_wu_data(build_apps(), schema_editor=None)

    legacy_invoice.refresh_from_db()

    assert WesternUnionData.objects.filter(name=legacy_invoice.name).exists() is False
    assert legacy_invoice.is_legacy is True
    assert legacy_invoice.status == WesternUnionInvoice.STATUS_COMPLETED
    assert legacy_invoice.error_msg == ""


def test_migration_creates_error_data_row_for_invalid_2026_legacy_qcf_invoice() -> None:
    legacy_invoice = WesternUnionInvoiceFactory(
        name="QCF-AUS001029-SL-20260115.ZIP",
        file=build_file_temp("sample.zip", build_qcf_archive('"0","header only"\n')),
    )

    migration_module.migrate_existing_qcf_invoices_to_wu_data(build_apps(), schema_editor=None)

    legacy_invoice.refresh_from_db()
    migrated_data = WesternUnionData.objects.get(name=legacy_invoice.name)

    assert migrated_data.status == WesternUnionData.STATUS_ERROR
    assert migrated_data.date == date(2026, 1, 15)
    assert migrated_data.amount is None
    assert "no footer row" in (migrated_data.error_msg or "").lower()
    assert legacy_invoice.is_legacy is True
    assert legacy_invoice.status == WesternUnionInvoice.STATUS_COMPLETED
    assert legacy_invoice.error_msg == ""


def test_migration_creates_error_data_row_for_unreadable_2026_legacy_qcf_file() -> None:
    file_temp = build_file_temp("sample.zip", build_qcf_archive('"9",10,-228.90,0.00,0.00\n'))
    assert file_temp.file.name
    os.remove(file_temp.file.path)
    legacy_invoice = WesternUnionInvoiceFactory(
        name="QCF-AUS001029-SL-20260115.ZIP",
        file=file_temp,
    )

    migration_module.migrate_existing_qcf_invoices_to_wu_data(build_apps(), schema_editor=None)

    legacy_invoice.refresh_from_db()
    migrated_data = WesternUnionData.objects.get(name=legacy_invoice.name)

    assert migrated_data.status == WesternUnionData.STATUS_ERROR
    assert migrated_data.date == date(2026, 1, 15)
    assert migrated_data.amount is None
    assert "no such file" in (migrated_data.error_msg or "").lower() or "blob missing" in (
        migrated_data.error_msg or ""
    )
    assert legacy_invoice.is_legacy is True
    assert legacy_invoice.status == WesternUnionInvoice.STATUS_COMPLETED
    assert legacy_invoice.error_msg == ""


def build_apps() -> SimpleNamespace:
    return SimpleNamespace(
        get_model=lambda app_label, model_name: {
            ("payment", "WesternUnionInvoice"): WesternUnionInvoice,
            ("payment", "WesternUnionData"): WesternUnionData,
        }[(app_label, model_name)]
    )


def build_file_temp(filename: str, file_bytes: bytes):
    file_temp = FileTempFactory()
    file_temp.file.save(filename, ContentFile(file_bytes), save=True)
    return file_temp


def build_qcf_archive(footer_row: str) -> bytes:
    content = '"0","header"\n' + footer_row
    file_obj = io.BytesIO()
    with zipfile.ZipFile(file_obj, "w") as archive:
        archive.writestr("sample.cf", content)
    return file_obj.getvalue()
