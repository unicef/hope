from datetime import timezone as dt_timezone
from typing import Optional
from unittest.mock import patch

from django.utils import timezone
import pytest

from extras.test_utils.factories import (
    BusinessAreaFactory,
    PaymentFactory,
    PaymentPlanFactory,
    ProgramFactory,
)
from hope.apps.dashboard.services import DashboardCacheBase
from hope.models import BusinessArea, Payment, PaymentPlan, Program


@pytest.fixture
def use_default_db_for_dashboard():
    with (
        patch("hope.apps.dashboard.services.settings.DASHBOARD_DB", "default"),
        patch("hope.apps.dashboard.celery_tasks.settings.DASHBOARD_DB", "default"),
    ):
        yield


pytestmark = pytest.mark.usefixtures("use_default_db_for_dashboard")

CURRENT_YEAR = timezone.now().year
TEST_DATE = timezone.datetime(CURRENT_YEAR, 7, 15, tzinfo=dt_timezone.utc)


# ============================================================================
# Local Fixtures
# ============================================================================


@pytest.fixture
def create_payment_for_queryset(db):
    def _create(
        program_obj: Program,
        business_area_obj: BusinessArea,
        *,
        pp_status: str = PaymentPlan.Status.ACCEPTED,
        pp_is_removed: bool = False,
        prog_is_visible: bool = True,
        payment_is_removed: bool = False,
        payment_conflicted: bool = False,
        payment_excluded: bool = False,
        payment_status: str = "Transaction Successful",
        delivery_date: Optional[timezone.datetime] = None,
    ) -> tuple[Payment, PaymentPlan]:
        program_obj.is_visible = prog_is_visible
        program_obj.save()

        pp = PaymentPlanFactory(
            program_cycle__program=program_obj,
            status=pp_status,
            is_removed=pp_is_removed,
        )
        payment = PaymentFactory(
            parent=pp,
            program=program_obj,
            business_area=business_area_obj,
            is_removed=payment_is_removed,
            conflicted=payment_conflicted,
            excluded=payment_excluded,
            status=payment_status,
            delivery_date=delivery_date or timezone.now(),
        )
        return payment, pp

    return _create


@pytest.fixture
def ba_for_base_queryset_tests(db):
    return BusinessAreaFactory()


@pytest.fixture
def prog_for_base_queryset_tests(ba_for_base_queryset_tests):
    return ProgramFactory(business_area=ba_for_base_queryset_tests)


@pytest.fixture
def prog_invisible_for_base_queryset_tests(ba_for_base_queryset_tests):
    return ProgramFactory(business_area=ba_for_base_queryset_tests, is_visible=False)


# ============================================================================
# Base Queryset Filter Tests
# ============================================================================


@pytest.mark.parametrize(
    "pp_status",
    [
        PaymentPlan.Status.IN_APPROVAL,
        PaymentPlan.Status.IN_AUTHORIZATION,
        PaymentPlan.Status.IN_REVIEW,
        PaymentPlan.Status.ACCEPTED,
        PaymentPlan.Status.FINISHED,
    ],
    ids=[
        "IN_APPROVAL",
        "IN_AUTHORIZATION",
        "IN_REVIEW",
        "ACCEPTED",
        "FINISHED",
    ],
)
@pytest.mark.django_db
def test_base_queryset_includes_payment_with_valid_plan_status(
    pp_status,
    create_payment_for_queryset,
    ba_for_base_queryset_tests,
    prog_for_base_queryset_tests,
) -> None:
    payment, _ = create_payment_for_queryset(
        prog_for_base_queryset_tests, ba_for_base_queryset_tests, pp_status=pp_status
    )
    qs = DashboardCacheBase._get_base_payment_queryset(business_area=ba_for_base_queryset_tests)
    assert qs.filter(pk=payment.pk).exists(), f"Payment should be included for PP status {pp_status}"


@pytest.mark.django_db
def test_base_queryset_excludes_payment_with_draft_status(
    create_payment_for_queryset,
    ba_for_base_queryset_tests,
    prog_for_base_queryset_tests,
) -> None:
    invalid_status = PaymentPlan.Status.DRAFT
    payment_invalid, _ = create_payment_for_queryset(
        prog_for_base_queryset_tests, ba_for_base_queryset_tests, pp_status=invalid_status
    )
    qs_invalid = DashboardCacheBase._get_base_payment_queryset(business_area=ba_for_base_queryset_tests)
    assert not qs_invalid.filter(pk=payment_invalid.pk).exists(), (
        f"Payment should be excluded for PP status {invalid_status}"
    )


@pytest.mark.django_db
def test_base_queryset_filter_visible_program(
    create_payment_for_queryset,
    ba_for_base_queryset_tests,
    prog_for_base_queryset_tests,
) -> None:
    payment_visible_prog, _ = create_payment_for_queryset(
        prog_for_base_queryset_tests, ba_for_base_queryset_tests, prog_is_visible=True
    )
    qs_visible = DashboardCacheBase._get_base_payment_queryset(business_area=ba_for_base_queryset_tests)
    assert qs_visible.filter(pk=payment_visible_prog.pk).exists()


@pytest.mark.django_db
def test_base_queryset_filter_invisible_program(
    ba_for_base_queryset_tests,
    prog_invisible_for_base_queryset_tests,
    create_payment_for_queryset,
) -> None:
    payment_invisible_prog, _ = create_payment_for_queryset(
        prog_invisible_for_base_queryset_tests, ba_for_base_queryset_tests, prog_is_visible=False
    )
    qs_invisible = DashboardCacheBase._get_base_payment_queryset(business_area=ba_for_base_queryset_tests)
    assert not qs_invisible.filter(pk=payment_invisible_prog.pk).exists()


@pytest.mark.django_db
def test_base_queryset_filter_pp_not_removed(
    create_payment_for_queryset,
    ba_for_base_queryset_tests,
    prog_for_base_queryset_tests,
) -> None:
    payment_pp_not_removed, _ = create_payment_for_queryset(
        prog_for_base_queryset_tests, ba_for_base_queryset_tests, pp_is_removed=False
    )
    qs_pp_not_removed = DashboardCacheBase._get_base_payment_queryset(business_area=ba_for_base_queryset_tests)
    assert qs_pp_not_removed.filter(pk=payment_pp_not_removed.pk).exists()


@pytest.mark.django_db
def test_base_queryset_filter_pp_removed(
    create_payment_for_queryset,
    ba_for_base_queryset_tests,
    prog_for_base_queryset_tests,
) -> None:
    payment_pp_removed, _ = create_payment_for_queryset(
        prog_for_base_queryset_tests, ba_for_base_queryset_tests, pp_is_removed=True
    )
    qs_pp_removed = DashboardCacheBase._get_base_payment_queryset(business_area=ba_for_base_queryset_tests)
    assert not qs_pp_removed.filter(pk=payment_pp_removed.pk).exists()


@pytest.mark.django_db
def test_base_queryset_filter_payment_not_removed(
    create_payment_for_queryset,
    ba_for_base_queryset_tests,
    prog_for_base_queryset_tests,
) -> None:
    payment_not_removed, _ = create_payment_for_queryset(
        prog_for_base_queryset_tests, ba_for_base_queryset_tests, payment_is_removed=False
    )
    qs_not_removed = DashboardCacheBase._get_base_payment_queryset(business_area=ba_for_base_queryset_tests)
    assert qs_not_removed.filter(pk=payment_not_removed.pk).exists()


@pytest.mark.django_db
def test_base_queryset_filter_payment_removed(
    create_payment_for_queryset,
    ba_for_base_queryset_tests,
    prog_for_base_queryset_tests,
) -> None:
    payment_removed, _ = create_payment_for_queryset(
        prog_for_base_queryset_tests, ba_for_base_queryset_tests, payment_is_removed=True
    )
    qs_removed = DashboardCacheBase._get_base_payment_queryset(business_area=ba_for_base_queryset_tests)
    assert not qs_removed.filter(pk=payment_removed.pk).exists()


@pytest.mark.django_db
def test_base_queryset_filter_payment_not_conflicted(
    create_payment_for_queryset,
    ba_for_base_queryset_tests,
    prog_for_base_queryset_tests,
) -> None:
    payment_not_conflicted, _ = create_payment_for_queryset(
        prog_for_base_queryset_tests, ba_for_base_queryset_tests, payment_conflicted=False
    )
    qs_not_conflicted = DashboardCacheBase._get_base_payment_queryset(business_area=ba_for_base_queryset_tests)
    assert qs_not_conflicted.filter(pk=payment_not_conflicted.pk).exists()


@pytest.mark.django_db
def test_base_queryset_filter_payment_conflicted(
    create_payment_for_queryset,
    ba_for_base_queryset_tests,
    prog_for_base_queryset_tests,
) -> None:
    payment_conflicted, _ = create_payment_for_queryset(
        prog_for_base_queryset_tests, ba_for_base_queryset_tests, payment_conflicted=True
    )
    qs_conflicted = DashboardCacheBase._get_base_payment_queryset(business_area=ba_for_base_queryset_tests)
    assert not qs_conflicted.filter(pk=payment_conflicted.pk).exists()


@pytest.mark.django_db
def test_base_queryset_filter_payment_not_excluded(
    create_payment_for_queryset,
    ba_for_base_queryset_tests,
    prog_for_base_queryset_tests,
) -> None:
    payment_not_excluded, _ = create_payment_for_queryset(
        prog_for_base_queryset_tests, ba_for_base_queryset_tests, payment_excluded=False
    )
    qs_not_excluded = DashboardCacheBase._get_base_payment_queryset(business_area=ba_for_base_queryset_tests)
    assert qs_not_excluded.filter(pk=payment_not_excluded.pk).exists()


@pytest.mark.django_db
def test_base_queryset_filter_payment_excluded(
    create_payment_for_queryset,
    ba_for_base_queryset_tests,
    prog_for_base_queryset_tests,
) -> None:
    payment_excluded, _ = create_payment_for_queryset(
        prog_for_base_queryset_tests, ba_for_base_queryset_tests, payment_excluded=True
    )
    qs_excluded = DashboardCacheBase._get_base_payment_queryset(business_area=ba_for_base_queryset_tests)
    assert not qs_excluded.filter(pk=payment_excluded.pk).exists()


@pytest.mark.django_db
def test_base_queryset_includes_successful_payment_status(
    create_payment_for_queryset,
    ba_for_base_queryset_tests,
    prog_for_base_queryset_tests,
) -> None:
    included_status = "Transaction Successful"
    payment_included, _ = create_payment_for_queryset(
        prog_for_base_queryset_tests, ba_for_base_queryset_tests, payment_status=included_status
    )
    qs_included = DashboardCacheBase._get_base_payment_queryset(business_area=ba_for_base_queryset_tests)
    assert qs_included.filter(pk=payment_included.pk).exists()


@pytest.mark.parametrize(
    "excluded_status",
    [
        "Transaction Erroneous",
        "Not Distributed",
        "Force failed",
        "Manually Cancelled",
    ],
    ids=[
        "Transaction Erroneous",
        "Not Distributed",
        "Force failed",
        "Manually Cancelled",
    ],
)
@pytest.mark.django_db
def test_base_queryset_excludes_payment_with_excluded_status(
    excluded_status,
    create_payment_for_queryset,
    ba_for_base_queryset_tests,
    prog_for_base_queryset_tests,
) -> None:
    payment_excluded, _ = create_payment_for_queryset(
        prog_for_base_queryset_tests, ba_for_base_queryset_tests, payment_status=excluded_status
    )
    qs_excluded = DashboardCacheBase._get_base_payment_queryset(business_area=ba_for_base_queryset_tests)
    assert not qs_excluded.filter(pk=payment_excluded.pk).exists(), (
        f"Payment should be excluded for status {excluded_status}"
    )


@pytest.fixture
def two_business_areas_with_payments(db, create_payment_for_queryset):
    ba1 = BusinessAreaFactory(name="BA1")
    prog1 = ProgramFactory(business_area=ba1)
    payment1, _ = create_payment_for_queryset(prog1, ba1)

    ba2 = BusinessAreaFactory(name="BA2")
    prog2 = ProgramFactory(business_area=ba2)
    payment2, _ = create_payment_for_queryset(prog2, ba2)

    return {
        "ba1": ba1,
        "ba2": ba2,
        "payment1": payment1,
        "payment2": payment2,
    }


@pytest.mark.django_db
def test_get_base_payment_queryset_filters_by_ba(two_business_areas_with_payments) -> None:
    data = two_business_areas_with_payments

    qs_ba1 = DashboardCacheBase._get_base_payment_queryset(business_area=data["ba1"])
    assert qs_ba1.filter(pk=data["payment1"].pk).exists()
    assert not qs_ba1.filter(pk=data["payment2"].pk).exists()


@pytest.mark.django_db
def test_get_base_payment_queryset_returns_all_without_ba(two_business_areas_with_payments) -> None:
    data = two_business_areas_with_payments

    qs_all = DashboardCacheBase._get_base_payment_queryset()
    assert qs_all.filter(pk=data["payment1"].pk).exists()
    assert qs_all.filter(pk=data["payment2"].pk).exists()
