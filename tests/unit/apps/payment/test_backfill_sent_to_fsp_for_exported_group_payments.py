from django.utils import timezone
import pytest

from extras.test_utils.factories import (
    FileTempFactory,
    FinancialServiceProviderFactory,
    PaymentFactory,
    PaymentPlanFactory,
    PaymentPlanGroupFactory,
)
from hope.models import FinancialServiceProvider, Payment, PaymentPlan
from hope.one_time_scripts.backfill_sent_to_fsp_for_exported_group_payments import (
    INTERNAL_DATA_KEY,
    _set_backfill_values,
    backfill,
)

pytestmark = pytest.mark.django_db


@pytest.fixture
def historical_group_export():
    group = PaymentPlanGroupFactory()
    export_file = FileTempFactory()
    xlsx_fsp = FinancialServiceProviderFactory()
    payment_plan = PaymentPlanFactory(
        program_cycle=group.cycle,
        payment_plan_group=group,
        financial_service_provider=xlsx_fsp,
        status=PaymentPlan.Status.ACCEPTED,
        use_payment_gateway=False,
        export_tag=1,
        export_file_delivery=export_file,
    )
    original_status_date = timezone.now()
    payment = PaymentFactory(
        parent=payment_plan,
        status=Payment.STATUS_PENDING,
        status_date=original_status_date,
        delivered_quantity=None,
        internal_data={"existing": "value"},
    )

    api_fsp = FinancialServiceProviderFactory(communication_channel=FinancialServiceProvider.COMMUNICATION_CHANNEL_API)
    api_payment_plan = PaymentPlanFactory(
        program_cycle=group.cycle,
        payment_plan_group=group,
        financial_service_provider=api_fsp,
        status=PaymentPlan.Status.ACCEPTED,
        use_payment_gateway=False,
        export_tag=2,
        export_file_delivery=FileTempFactory(),
    )
    api_payment = PaymentFactory(
        parent=api_payment_plan,
        status=Payment.STATUS_PENDING,
        delivered_quantity=None,
    )
    return payment, api_payment, export_file, original_status_date


def test_backfill_dry_run_does_not_change_payments(
    historical_group_export,
    django_assert_num_queries,
) -> None:
    payment, _api_payment, _export_file, original_status_date = historical_group_export

    summary = backfill()

    with django_assert_num_queries(1):
        payment.refresh_from_db()
    assert summary == {"dry_run": True, "eligible_payments": 1, "updated_payments": 0}
    assert payment.status == Payment.STATUS_PENDING
    assert payment.status_date == original_status_date
    assert payment.internal_data == {"existing": "value"}


def test_backfill_updates_only_historical_manual_group_payments(
    historical_group_export,
    django_assert_num_queries,
) -> None:
    payment, api_payment, export_file, original_status_date = historical_group_export
    old_signature = payment.signature_hash

    summary = backfill(dry_run=False, batch_size=1)

    with django_assert_num_queries(2):
        payment.refresh_from_db()
        api_payment.refresh_from_db()
    stored_signature = payment.signature_hash
    payment.update_signature_hash()
    assert summary == {"dry_run": False, "eligible_payments": 1, "updated_payments": 1}
    assert payment.status == Payment.STATUS_SENT_TO_FSP
    assert payment.status_date == export_file.created
    assert payment.internal_data["existing"] == "value"
    backfill_entry = payment.internal_data[INTERNAL_DATA_KEY][-1]
    assert backfill_entry["export_file_id"] == str(export_file.pk)
    assert backfill_entry["previous_status"] == Payment.STATUS_PENDING
    assert backfill_entry["previous_status_date"] == original_status_date.isoformat()
    assert stored_signature != old_signature
    assert payment.signature_hash == stored_signature
    assert api_payment.status == Payment.STATUS_PENDING


def test_backfill_is_safe_to_run_again(historical_group_export, django_assert_num_queries) -> None:
    payment, _api_payment, _export_file, _original_status_date = historical_group_export
    first_summary = backfill(dry_run=False)

    second_summary = backfill(dry_run=False)

    with django_assert_num_queries(1):
        payment.refresh_from_db()
    assert first_summary["updated_payments"] == 1
    assert second_summary == {"dry_run": False, "eligible_payments": 0, "updated_payments": 0}
    assert payment.status == Payment.STATUS_SENT_TO_FSP


def test_set_backfill_values_rejects_invalid_history(historical_group_export, django_assert_num_queries) -> None:
    payment, _api_payment, _export_file, _original_status_date = historical_group_export
    payment.internal_data = {INTERNAL_DATA_KEY: {}}

    with django_assert_num_queries(0), pytest.raises(ValueError, match="to be a list"):
        _set_backfill_values(payment, timezone.now())


def test_set_backfill_values_requires_export_file(historical_group_export, django_assert_num_queries) -> None:
    payment, _api_payment, _export_file, _original_status_date = historical_group_export
    payment.parent.export_file_delivery = None

    with django_assert_num_queries(0), pytest.raises(ValueError, match="has no delivery export file"):
        _set_backfill_values(payment, timezone.now())
