"""Tests for program cycle model and validation."""

from decimal import Decimal
from typing import Any

from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils import timezone
from django.utils.dateparse import parse_date
import pytest
from rest_framework.exceptions import ValidationError

from extras.test_utils.factories import (
    BusinessAreaFactory,
    PaymentPlanFactory,
    ProgramCycleFactory,
    ProgramFactory,
    UserFactory,
)
from hope.models import BusinessArea, Program, ProgramCycle, User

pytestmark = pytest.mark.django_db


@pytest.fixture
def afghanistan(db: Any) -> BusinessArea:
    return BusinessAreaFactory(name="Afghanistan", slug="afghanistan")


@pytest.fixture
def user(db: Any) -> User:
    return UserFactory.create()


@pytest.fixture
def program(afghanistan: BusinessArea) -> Program:
    program = ProgramFactory(
        status=Program.DRAFT,
        business_area=afghanistan,
        start_date="2020-01-01",
        end_date="2099-12-31",
    )
    # Create default cycle for the program
    ProgramCycleFactory(
        program=program,
        title="Default Cycle 001",
        start_date="2020-01-01",
        end_date="2020-01-02",
    )
    return program


@pytest.fixture
def cycle(program: Program) -> ProgramCycle:
    return ProgramCycleFactory(
        program=program,
        start_date="2021-01-01",
        end_date="2022-01-01",
        title="Cycle 002",
    )


def activate_program(cycle: ProgramCycle) -> None:
    cycle.program.status = Program.ACTIVE
    cycle.program.save()
    cycle.program.refresh_from_db()
    assert cycle.program.status == Program.ACTIVE


def test_set_active(cycle: ProgramCycle) -> None:
    with pytest.raises(ValidationError, match="Program should be within Active status."):
        cycle.set_active()
    activate_program(cycle)

    cycle.status = ProgramCycle.DRAFT
    cycle.save()
    assert cycle.status == ProgramCycle.DRAFT
    cycle.set_active()
    cycle.refresh_from_db()
    assert cycle.status == ProgramCycle.ACTIVE

    cycle.status = ProgramCycle.FINISHED
    cycle.save()
    assert cycle.status == ProgramCycle.FINISHED
    cycle.set_active()
    cycle.refresh_from_db()
    assert cycle.status == ProgramCycle.ACTIVE
    assert not cycle.can_remove_cycle


def test_set_draft(cycle: ProgramCycle) -> None:
    with pytest.raises(ValidationError, match="Program should be within Active status."):
        cycle.set_active()
    activate_program(cycle)

    cycle.status = ProgramCycle.FINISHED
    cycle.save()
    assert cycle.status == ProgramCycle.FINISHED
    cycle.set_draft()
    cycle.refresh_from_db()
    assert cycle.status == ProgramCycle.FINISHED

    cycle.status = ProgramCycle.ACTIVE
    cycle.save()
    assert cycle.status == ProgramCycle.ACTIVE
    cycle.set_draft()
    cycle.refresh_from_db()
    assert cycle.status == ProgramCycle.DRAFT
    assert cycle.can_remove_cycle


def test_set_finish(cycle: ProgramCycle) -> None:
    with pytest.raises(ValidationError, match="Program should be within Active status."):
        cycle.set_finish()
    activate_program(cycle)

    cycle.status = ProgramCycle.DRAFT
    cycle.save()
    cycle.set_finish()
    cycle.refresh_from_db()
    assert cycle.status == ProgramCycle.DRAFT

    cycle.status = ProgramCycle.ACTIVE
    cycle.save()
    cycle.set_finish()
    cycle.refresh_from_db()
    assert cycle.status == ProgramCycle.FINISHED
    assert not cycle.can_remove_cycle


def test_total_entitled_quantity_usd(cycle: ProgramCycle) -> None:
    assert cycle.total_entitled_quantity_usd == Decimal("0.0")
    PaymentPlanFactory(program_cycle=cycle, total_entitled_quantity_usd=Decimal(123.99))
    assert cycle.total_entitled_quantity_usd == Decimal("123.99")


def test_total_undelivered_quantity_usd(cycle: ProgramCycle) -> None:
    assert cycle.total_undelivered_quantity_usd == Decimal("0.0")
    PaymentPlanFactory(program_cycle=cycle, total_undelivered_quantity_usd=Decimal(222.33))
    assert cycle.total_undelivered_quantity_usd == Decimal("222.33")


def test_total_delivered_quantity_usd(cycle: ProgramCycle) -> None:
    assert cycle.total_delivered_quantity_usd == Decimal("0.0")
    PaymentPlanFactory(program_cycle=cycle, total_delivered_quantity_usd=Decimal(333.11))
    assert cycle.total_delivered_quantity_usd == Decimal("333.11")


def test_cycle_validation_start_date(program: Program, cycle: ProgramCycle) -> None:
    with pytest.raises(DjangoValidationError, match="Start date must be after the latest cycle."):
        ProgramCycleFactory(program=program, start_date=parse_date("2021-01-01"))

    with pytest.raises(DjangoValidationError, match="End date cannot be before start date."):
        ProgramCycleFactory(
            program=program,
            start_date=parse_date("2021-01-05"),
            end_date=parse_date("2021-01-01"),
        )

    cycle2 = ProgramCycleFactory(program=program)
    assert cycle2.start_date > parse_date(cycle.start_date)

    cycle_new = ProgramCycleFactory(program=program, start_date=parse_date("2099-01-01"))
    assert cycle_new.start_date > timezone.now().date()
