from datetime import timedelta

from django.utils import timezone
import pytest

from extras.test_utils.factories import BusinessAreaFactory, PaymentFactory, PaymentPlanFactory, ProgramFactory
from hope.models import Payment
from hope.one_time_scripts.mark_active_ineligible_payments import mark_active_ineligible_payments

pytestmark = pytest.mark.django_db


@pytest.fixture
def historical_payment_statuses() -> dict[str, Payment]:
    first_business_area = BusinessAreaFactory(name="Ineligible Backfill First", slug="ineligible-backfill-first")
    first_program = ProgramFactory(name="Ineligible Backfill First", business_area=first_business_area)
    first_payment_plan = PaymentPlanFactory(business_area=first_business_area, program_cycle__program=first_program)
    second_business_area = BusinessAreaFactory(name="Ineligible Backfill Second", slug="ineligible-backfill-second")
    second_program = ProgramFactory(name="Ineligible Backfill Second", business_area=second_business_area)
    second_payment_plan = PaymentPlanFactory(business_area=second_business_area, program_cycle__program=second_program)
    eligible_pending = PaymentFactory(
        parent=first_payment_plan,
        program=first_program,
        status=Payment.STATUS_PENDING,
    )
    conflicted_pending = PaymentFactory(
        parent=first_payment_plan,
        program=first_program,
        status=Payment.STATUS_PENDING,
        conflicted=True,
        status_date=timezone.now() - timedelta(days=1),
    )
    excluded_pending = PaymentFactory(
        parent=first_payment_plan,
        program=first_program,
        status=Payment.STATUS_PENDING,
        excluded=True,
    )
    no_program_pending = PaymentFactory(
        parent=first_payment_plan,
        program=None,
        status=Payment.STATUS_PENDING,
        excluded=True,
    )
    invalid_wallet_pending = PaymentFactory(
        parent=second_payment_plan,
        program=second_program,
        status=Payment.STATUS_PENDING,
        has_valid_wallet=False,
    )
    invalid_wallet_delivered = PaymentFactory(
        parent=second_payment_plan,
        program=second_program,
        status=Payment.STATUS_SUCCESS,
        has_valid_wallet=False,
    )
    conflicted_error = PaymentFactory(
        parent=second_payment_plan,
        program=second_program,
        status=Payment.STATUS_ERROR,
        conflicted=True,
    )
    removed_pending = PaymentFactory(
        parent=second_payment_plan,
        program=second_program,
        status=Payment.STATUS_PENDING,
        excluded=True,
        is_removed=True,
    )
    overlapping_pending = PaymentFactory(
        parent=second_payment_plan,
        program=second_program,
        status=Payment.STATUS_PENDING,
        conflicted=True,
        excluded=True,
        has_valid_wallet=False,
    )
    return {
        "eligible_pending": eligible_pending,
        "conflicted_pending": conflicted_pending,
        "excluded_pending": excluded_pending,
        "no_program_pending": no_program_pending,
        "invalid_wallet_pending": invalid_wallet_pending,
        "invalid_wallet_delivered": invalid_wallet_delivered,
        "conflicted_error": conflicted_error,
        "removed_pending": removed_pending,
        "overlapping_pending": overlapping_pending,
    }


def test_script_dry_run_reports_grouped_counts_without_updating(
    historical_payment_statuses: dict[str, Payment],
    django_assert_num_queries,
    capsys,
) -> None:
    conflicted_pending = historical_payment_statuses["conflicted_pending"]
    no_program_pending = historical_payment_statuses["no_program_pending"]
    invalid_wallet_pending = historical_payment_statuses["invalid_wallet_pending"]

    with django_assert_num_queries(3):
        summary = mark_active_ineligible_payments()

    conflicted_pending.refresh_from_db()
    no_program_pending.refresh_from_db()
    invalid_wallet_pending.refresh_from_db()
    assert summary == {
        "dry_run": True,
        "candidate_count": 5,
        "updated_count": 0,
        "groups": [
            {
                "business_area_id": str(conflicted_pending.business_area_id),
                "business_area": "ineligible-backfill-first",
                "program_id": str(conflicted_pending.program_id),
                "program": "Ineligible Backfill First",
                "candidate_count": 2,
                "updated_count": 0,
            },
            {
                "business_area_id": str(no_program_pending.business_area_id),
                "business_area": "ineligible-backfill-first",
                "program_id": None,
                "program": None,
                "candidate_count": 1,
                "updated_count": 0,
            },
            {
                "business_area_id": str(invalid_wallet_pending.business_area_id),
                "business_area": "ineligible-backfill-second",
                "program_id": str(invalid_wallet_pending.program_id),
                "program": "Ineligible Backfill Second",
                "candidate_count": 2,
                "updated_count": 0,
            },
        ],
    }
    assert conflicted_pending.status == Payment.STATUS_PENDING
    assert no_program_pending.status == Payment.STATUS_PENDING
    assert invalid_wallet_pending.status == Payment.STATUS_PENDING
    output = capsys.readouterr().out
    assert "Starting dry run: scanning for active ineligible Pending payments..." in output
    assert "Found 5 candidate payments across 3 business area/program groups." in output
    assert "[1/3] ineligible-backfill-first / Ineligible Backfill First: 2 candidates (dry run)." in output
    assert "[2/3] ineligible-backfill-first / [no program]: 1 candidate (dry run)." in output
    assert "[3/3] ineligible-backfill-second / Ineligible Backfill Second: 2 candidates (dry run)." in output
    assert "Dry run complete: 5 payments would be marked across 3 business area/program groups." in output


def test_script_updates_each_group_atomically_and_preserves_other_records(
    historical_payment_statuses: dict[str, Payment],
    django_assert_num_queries,
    capsys,
) -> None:
    original_status_date = historical_payment_statuses["conflicted_pending"].status_date

    with django_assert_num_queries(12):
        summary = mark_active_ineligible_payments(dry_run=False)

    eligible_pending = historical_payment_statuses["eligible_pending"]
    conflicted_pending = historical_payment_statuses["conflicted_pending"]
    excluded_pending = historical_payment_statuses["excluded_pending"]
    no_program_pending = historical_payment_statuses["no_program_pending"]
    invalid_wallet_pending = historical_payment_statuses["invalid_wallet_pending"]
    invalid_wallet_delivered = historical_payment_statuses["invalid_wallet_delivered"]
    conflicted_error = historical_payment_statuses["conflicted_error"]
    removed_pending = historical_payment_statuses["removed_pending"]
    overlapping_pending = historical_payment_statuses["overlapping_pending"]
    eligible_pending.refresh_from_db()
    conflicted_pending.refresh_from_db()
    excluded_pending.refresh_from_db()
    no_program_pending.refresh_from_db()
    invalid_wallet_pending.refresh_from_db()
    invalid_wallet_delivered.refresh_from_db()
    conflicted_error.refresh_from_db()
    removed_pending.refresh_from_db()
    overlapping_pending.refresh_from_db()
    assert summary["candidate_count"] == 5
    assert summary["updated_count"] == 5
    assert eligible_pending.status == Payment.STATUS_PENDING
    assert conflicted_pending.status == Payment.STATUS_NOT_ELIGIBLE
    assert conflicted_pending.status_date == original_status_date
    assert excluded_pending.status == Payment.STATUS_NOT_ELIGIBLE
    assert no_program_pending.status == Payment.STATUS_NOT_ELIGIBLE
    assert invalid_wallet_pending.status == Payment.STATUS_NOT_ELIGIBLE
    assert invalid_wallet_delivered.status == Payment.STATUS_SUCCESS
    assert conflicted_error.status == Payment.STATUS_ERROR
    assert removed_pending.status == Payment.STATUS_PENDING
    assert overlapping_pending.status == Payment.STATUS_NOT_ELIGIBLE
    output = capsys.readouterr().out
    assert "Starting live run: scanning for active ineligible Pending payments..." in output
    assert "[1/3] ineligible-backfill-first / Ineligible Backfill First: updating 2 candidates..." in output
    assert "[1/3] ineligible-backfill-first / Ineligible Backfill First: committed 2 updates." in output
    assert "Live run complete: committed 5 updates across 3 business area/program groups." in output
