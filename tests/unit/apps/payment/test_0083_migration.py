from decimal import Decimal
import importlib
from typing import Any, Callable

import pytest

migration_module = importlib.import_module("hope.apps.payment.migrations.0083_migration")


PlanRow = Callable[..., dict[str, Any]]


@pytest.fixture
def plan_row() -> PlanRow:
    """Build a payment plan as the dict the migration reads with .values(), not as a model object.

    The plan's FSP, currency and use_payment_gateway columns no longer exist on today's PaymentPlan (0084 and 0093
    move them to the group), so factories cannot create these plans and the test database has no such columns.
    """

    def build(**values: Any) -> dict[str, Any]:
        return {
            "id": values["id"],
            "payment_plan_group_id": "group",
            "plan_type": values.get("plan_type", "REGULAR"),
            "follow_up_instruction_id": values.get("follow_up_instruction_id"),
            "source_payment_plan_id": values.get("source_payment_plan_id"),
            "status": values.get("status", "ACCEPTED"),
            "financial_service_provider_id": values.get("financial_service_provider_id", "fsp-1"),
            "currency_id": values.get("currency_id", "usd"),
            "use_payment_gateway": values.get("use_payment_gateway", False),
            "exchange_rate": values.get("exchange_rate", Decimal("1.5")),
        }

    return build


@pytest.fixture
def accepted_plans(plan_row: PlanRow) -> list[dict[str, Any]]:
    return [plan_row(id="pp-1"), plan_row(id="pp-2")]


@pytest.fixture
def finished_and_draft_plans(plan_row: PlanRow) -> list[dict[str, Any]]:
    return [plan_row(id="pp-draft", status="DRAFT"), plan_row(id="pp-finished", status="FINISHED")]


@pytest.fixture
def plans_with_different_fsps(plan_row: PlanRow) -> list[dict[str, Any]]:
    return [plan_row(id="pp-1"), plan_row(id="pp-2", financial_service_provider_id="fsp-2")]


@pytest.fixture
def plans_with_different_currencies(plan_row: PlanRow) -> list[dict[str, Any]]:
    return [plan_row(id="pp-1"), plan_row(id="pp-2", currency_id="eur")]


@pytest.fixture
def plans_with_different_gateway_flags(plan_row: PlanRow) -> list[dict[str, Any]]:
    return [plan_row(id="pp-1"), plan_row(id="pp-2", use_payment_gateway=True)]


@pytest.fixture
def accepted_plans_with_different_rates(plan_row: PlanRow) -> list[dict[str, Any]]:
    return [plan_row(id="pp-1"), plan_row(id="pp-2", exchange_rate=Decimal("1.6"))]


@pytest.fixture
def draft_plans_with_different_rates(plan_row: PlanRow) -> list[dict[str, Any]]:
    return [
        plan_row(id="pp-1", status="DRAFT"),
        plan_row(id="pp-2", status="TP_LOCKED", exchange_rate=Decimal("1.6")),
    ]


@pytest.fixture
def plans_before_and_at_fsp_lock(plan_row: PlanRow) -> list[dict[str, Any]]:
    return [
        plan_row(id="pp-open", status="OPEN"),
        plan_row(id="pp-locked", status="LOCKED"),
        plan_row(id="pp-locked-fsp", status="LOCKED_FSP"),
    ]


@pytest.fixture
def plans_one_without_fsp(plan_row: PlanRow) -> list[dict[str, Any]]:
    return [
        plan_row(id="pp-without-fsp", status="OPEN", financial_service_provider_id=None),
        plan_row(id="pp-with-fsp", status="OPEN"),
    ]


@pytest.fixture
def follow_up_of_the_draft_plan(plan_row: PlanRow) -> list[dict[str, Any]]:
    return [
        plan_row(id="pp-finished", status="FINISHED"),
        plan_row(id="pp-draft", status="DRAFT"),
        plan_row(id="pp-follow-up", plan_type="FOLLOW_UP", status="ACCEPTED", source_payment_plan_id="pp-draft"),
    ]


@pytest.fixture
def follow_up_of_a_plan_in_another_group(plan_row: PlanRow) -> list[dict[str, Any]]:
    return [
        plan_row(id="pp-draft", status="DRAFT"),
        plan_row(id="pp-finished", status="FINISHED"),
        plan_row(id="pp-follow-up", plan_type="FOLLOW_UP", source_payment_plan_id="pp-elsewhere"),
    ]


@pytest.fixture
def instruction_child_and_its_source(plan_row: PlanRow) -> list[dict[str, Any]]:
    return [
        plan_row(id="pp-finished", status="FINISHED"),
        plan_row(id="pp-accepted"),
        plan_row(
            id="pp-child",
            plan_type="FOLLOW_UP",
            status="DRAFT",
            follow_up_instruction_id="instruction",
            source_payment_plan_id="pp-accepted",
        ),
    ]


def test_plans_that_agree_stay_in_one_part(accepted_plans: list[dict[str, Any]]) -> None:
    parts = migration_module.split_plans_into_parts(accepted_plans)

    assert parts == [[accepted_plans[0], accepted_plans[1]]]


def test_finished_and_draft_plans_split_and_finished_keeps_the_group(
    finished_and_draft_plans: list[dict[str, Any]],
) -> None:
    parts = migration_module.split_plans_into_parts(finished_and_draft_plans)

    assert parts == [[finished_and_draft_plans[1]], [finished_and_draft_plans[0]]]


def test_plans_with_different_fsps_split(plans_with_different_fsps: list[dict[str, Any]]) -> None:
    parts = migration_module.split_plans_into_parts(plans_with_different_fsps)

    assert parts == [[plans_with_different_fsps[0]], [plans_with_different_fsps[1]]]


def test_plans_with_different_currencies_split(plans_with_different_currencies: list[dict[str, Any]]) -> None:
    parts = migration_module.split_plans_into_parts(plans_with_different_currencies)

    assert parts == [[plans_with_different_currencies[0]], [plans_with_different_currencies[1]]]


def test_plans_with_different_payment_gateway_flags_split(
    plans_with_different_gateway_flags: list[dict[str, Any]],
) -> None:
    parts = migration_module.split_plans_into_parts(plans_with_different_gateway_flags)

    assert parts == [[plans_with_different_gateway_flags[0]], [plans_with_different_gateway_flags[1]]]


def test_opened_plans_with_different_exchange_rates_split(
    accepted_plans_with_different_rates: list[dict[str, Any]],
) -> None:
    parts = migration_module.split_plans_into_parts(accepted_plans_with_different_rates)

    assert parts == [[accepted_plans_with_different_rates[0]], [accepted_plans_with_different_rates[1]]]


def test_draft_plans_with_different_exchange_rates_stay_together(
    draft_plans_with_different_rates: list[dict[str, Any]],
) -> None:
    parts = migration_module.split_plans_into_parts(draft_plans_with_different_rates)

    assert parts == [[draft_plans_with_different_rates[0], draft_plans_with_different_rates[1]]]


def test_plans_before_fsp_lock_stay_together_and_fsp_locked_plan_splits(
    plans_before_and_at_fsp_lock: list[dict[str, Any]],
) -> None:
    parts = migration_module.split_plans_into_parts(plans_before_and_at_fsp_lock)

    assert parts == [
        [plans_before_and_at_fsp_lock[2]],
        [plans_before_and_at_fsp_lock[0], plans_before_and_at_fsp_lock[1]],
    ]


def test_plan_without_fsp_joins_the_plan_with_one(plans_one_without_fsp: list[dict[str, Any]]) -> None:
    parts = migration_module.split_plans_into_parts(plans_one_without_fsp)

    assert parts == [[plans_one_without_fsp[1], plans_one_without_fsp[0]]]


def test_follow_up_goes_with_its_source_plan(follow_up_of_the_draft_plan: list[dict[str, Any]]) -> None:
    parts = migration_module.split_plans_into_parts(follow_up_of_the_draft_plan)

    assert parts == [[follow_up_of_the_draft_plan[0]], [follow_up_of_the_draft_plan[1], follow_up_of_the_draft_plan[2]]]


def test_follow_up_of_a_plan_outside_the_group_stays_with_the_group(
    follow_up_of_a_plan_in_another_group: list[dict[str, Any]],
) -> None:
    parts = migration_module.split_plans_into_parts(follow_up_of_a_plan_in_another_group)

    assert parts == [
        [follow_up_of_a_plan_in_another_group[1], follow_up_of_a_plan_in_another_group[2]],
        [follow_up_of_a_plan_in_another_group[0]],
    ]


def test_instruction_child_goes_with_its_source_plan_and_does_not_split_the_group(
    instruction_child_and_its_source: list[dict[str, Any]],
) -> None:
    parts = migration_module.split_plans_into_parts(instruction_child_and_its_source)

    assert parts == [
        [instruction_child_and_its_source[0]],
        [instruction_child_and_its_source[1], instruction_child_and_its_source[2]],
    ]
