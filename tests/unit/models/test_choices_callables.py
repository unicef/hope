"""Coverage for the callable ``choices`` getters used on model fields.

These callables are passed to model fields as ``choices=...`` so that adding a
choice value does not generate a (no-op) migration. Django only evaluates them
lazily (during validation/form rendering), so they are exercised explicitly here.
"""

from hope.models.fsp_name_mapping import FspNameMapping
from hope.models.payment_plan_split import PaymentPlanSplit
from hope.models.storage_file import StorageFile, get_storage_status_choices
from hope.models.western_union_invoice_payment import (
    WesternUnionInvoicePayment,
    get_transaction_status_choices,
)


def test_fsp_name_mapping_source_model_get_choices() -> None:
    assert FspNameMapping.SourceModel.get_choices() == FspNameMapping.SourceModel.choices


def test_payment_plan_split_type_get_choices() -> None:
    assert PaymentPlanSplit.SplitType.get_choices() == PaymentPlanSplit.SplitType.choices


def test_western_union_invoice_payment_transaction_status_choices() -> None:
    assert get_transaction_status_choices() == WesternUnionInvoicePayment.TRANSACTION_STATUS_CHOICES


def test_storage_file_status_choices() -> None:
    assert get_storage_status_choices() == StorageFile.STATUS_CHOICE
