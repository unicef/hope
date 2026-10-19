from datetime import date, timedelta
from decimal import Decimal

import pytest

from extras.test_utils.factories import BusinessAreaFactory, PaymentPlanPurposeFactory
from extras.test_utils.factories.payment import PaymentPlanFactory
from extras.test_utils.factories.program import ProgramCycleFactory, ProgramFactory
from hope.models import BusinessArea, PaymentPlanPurpose, Program, ProgramCycle

BA_PURPOSE_NAME = "BA Purpose"
SECOND_BA_PURPOSE_NAME = "Second BA Purpose"
OTHER_BA_PURPOSE_NAME = "Other BA Purpose"
TEN_PURPOSE_NAMES = (
    "Purpose 1",
    "Purpose 2",
    "Purpose 3",
    "Purpose 4",
    "Purpose 5",
    "Purpose 6",
    "Purpose 7",
    "Purpose 8",
    "Purpose 9",
    "Purpose 10",
)


@pytest.fixture
def ba_purpose() -> PaymentPlanPurpose:
    return PaymentPlanPurposeFactory(name=BA_PURPOSE_NAME)


@pytest.fixture
def second_ba_purpose() -> PaymentPlanPurpose:
    return PaymentPlanPurposeFactory(name=SECOND_BA_PURPOSE_NAME)


@pytest.fixture
def other_ba_purpose() -> PaymentPlanPurpose:
    # limit_to a different business area so it is scoped out of the current BA
    purpose = PaymentPlanPurposeFactory(name=OTHER_BA_PURPOSE_NAME)
    purpose.limit_to.add(BusinessAreaFactory())
    return purpose


@pytest.fixture
def purpose() -> PaymentPlanPurpose:
    return PaymentPlanPurposeFactory(name=BA_PURPOSE_NAME)


@pytest.fixture
def program_with_purpose(business_area: BusinessArea, ba_purpose: PaymentPlanPurpose) -> Program:
    prog = ProgramFactory(business_area=business_area, status=Program.DRAFT)
    prog.payment_plan_purposes.add(ba_purpose)
    # Create a payment plan that uses this purpose so it shows as locked (used in PP)
    cycle = ProgramCycleFactory(program=prog)
    pp = PaymentPlanFactory(
        program_cycle=cycle,
        business_area=business_area,
        payment_plan_purposes=[ba_purpose],
    )
    pp.payment_plan_purposes.set([ba_purpose])
    return prog


@pytest.fixture
def ten_ba_purposes() -> list[PaymentPlanPurpose]:
    return [PaymentPlanPurposeFactory(name=name) for name in TEN_PURPOSE_NAMES]


@pytest.fixture
def program_with_ten_purposes(business_area: BusinessArea, ten_ba_purposes: list[PaymentPlanPurpose]) -> Program:
    prog = ProgramFactory(business_area=business_area, status=Program.DRAFT)
    prog.payment_plan_purposes.set(ten_ba_purposes)
    return prog


def days_from_today(days: int) -> date:
    return date.today() + timedelta(days=days)


def _programme(business_area: BusinessArea, status: str, *cycles: tuple[str, str, int, int | None]) -> Program:
    program = ProgramFactory(
        business_area=business_area,
        status=status,
        start_date=days_from_today(-30),
        end_date=days_from_today(30),
        cycle=False,
    )
    for title, cycle_status, start, end in cycles:
        ProgramCycleFactory(
            program=program,
            title=title,
            status=cycle_status,
            start_date=days_from_today(start),
            end_date=days_from_today(end) if end is not None else None,
        )
    return program


@pytest.fixture
def draft_programme(business_area: BusinessArea) -> Program:
    return _programme(business_area, Program.DRAFT, ("Default Programme Cycle", ProgramCycle.FINISHED, -25, 10))


@pytest.fixture
def active_programme_with_finished_cycle(business_area: BusinessArea) -> Program:
    return _programme(business_area, Program.ACTIVE, ("Default Programme Cycle", ProgramCycle.FINISHED, -25, 0))


@pytest.fixture
def active_programme_with_active_cycle(business_area: BusinessArea) -> Program:
    return _programme(business_area, Program.ACTIVE, ("Default Programme Cycle", ProgramCycle.ACTIVE, -25, 0))


@pytest.fixture
def programme_with_open_ended_cycle(business_area: BusinessArea) -> Program:
    program = _programme(business_area, Program.ACTIVE, ("Default Programme Cycle", ProgramCycle.DRAFT, -25, None))
    PaymentPlanFactory(
        program_cycle=program.cycles.get(),
        business_area=business_area,
        total_entitled_quantity_usd=Decimal("1234.99"),
        total_delivered_quantity_usd=Decimal("50.01"),
        total_undelivered_quantity_usd=Decimal("1184.98"),
    )
    return program


@pytest.fixture
def programme_with_draft_cycle(business_area: BusinessArea) -> Program:
    return _programme(business_area, Program.ACTIVE, ("Default Programme Cycle", ProgramCycle.DRAFT, 0, 1))


@pytest.fixture
def programme_with_three_draft_cycles(business_area: BusinessArea) -> Program:
    return _programme(
        business_area,
        Program.ACTIVE,
        ("First Cycle", ProgramCycle.DRAFT, -25, 10),
        ("Second Cycle", ProgramCycle.DRAFT, 11, 17),
        ("Third Cycle", ProgramCycle.DRAFT, 18, 20),
    )


@pytest.fixture
def programme_with_mixed_cycles(business_area: BusinessArea) -> Program:
    return _programme(
        business_area,
        Program.ACTIVE,
        ("Draft Cycle", ProgramCycle.DRAFT, -25, 10),
        ("Active Cycle", ProgramCycle.ACTIVE, 11, 17),
        ("Finished Cycle", ProgramCycle.FINISHED, 18, 20),
    )
