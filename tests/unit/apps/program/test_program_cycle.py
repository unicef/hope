from decimal import Decimal

from django.core.exceptions import ValidationError as DjangoValidationError
from django.test import TestCase
from django.utils import timezone
from django.utils.dateparse import parse_date
from extras.test_utils.factories.account import UserFactory
from extras.test_utils.factories.core import create_afghanistan
from extras.test_utils.factories.payment import PaymentPlanFactory
from extras.test_utils.factories.program import ProgramCycleFactory, ProgramFactory
from rest_framework.exceptions import ValidationError

from hope.models.business_area import BusinessArea
from hope.models.program import Program
from hope.models.program_cycle import ProgramCycle


class TestProgramCycleMethods(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        create_afghanistan()
        cls.user = UserFactory.create()
        cls.business_area = BusinessArea.objects.get(slug="afghanistan")
        cls.program = ProgramFactory(
            status=Program.DRAFT,
            business_area=cls.business_area,
            start_date="2020-01-01",
            end_date="2099-12-31",
            cycle__title="Default Cycle 001",
            cycle__start_date="2020-01-01",
            cycle__end_date="2020-01-02",
        )
        cls.cycle = ProgramCycleFactory(
            program=cls.program,
            start_date="2021-01-01",
            end_date="2022-01-01",
            title="Cycle 002",
        )

    def activate_program(self) -> None:
        self.cycle.program.status = Program.ACTIVE
        self.cycle.program.save()
        self.cycle.program.refresh_from_db()
        assert self.cycle.program.status == Program.ACTIVE

    def test_set_active(self) -> None:
        with self.assertRaisesMessage(ValidationError, "Program should be within Active status."):
            self.cycle.set_active()
        self.activate_program()

        self.cycle.status = ProgramCycle.DRAFT
        self.cycle.save()
        assert self.cycle.status == ProgramCycle.DRAFT
        self.cycle.set_active()
        self.cycle.refresh_from_db()
        assert self.cycle.status == ProgramCycle.ACTIVE

        self.cycle.status = ProgramCycle.FINISHED
        self.cycle.save()
        assert self.cycle.status == ProgramCycle.FINISHED
        self.cycle.set_active()
        self.cycle.refresh_from_db()
        assert self.cycle.status == ProgramCycle.ACTIVE
        assert not self.cycle.can_remove_cycle

    def test_set_draft(self) -> None:
        with self.assertRaisesMessage(ValidationError, "Program should be within Active status."):
            self.cycle.set_active()
        self.activate_program()

        self.cycle.status = ProgramCycle.FINISHED
        self.cycle.save()
        assert self.cycle.status == ProgramCycle.FINISHED
        self.cycle.set_active()
        self.cycle.refresh_from_db()
        assert self.cycle.status == ProgramCycle.ACTIVE

        self.cycle.status = ProgramCycle.ACTIVE
        self.cycle.save()
        assert self.cycle.status == ProgramCycle.ACTIVE
        self.cycle.set_active()
        self.cycle.refresh_from_db()
        assert self.cycle.status == ProgramCycle.ACTIVE
        assert not self.cycle.can_remove_cycle

    def test_set_finish(self) -> None:
        with self.assertRaisesMessage(ValidationError, "Program should be within Active status."):
            self.cycle.set_finish()
        self.activate_program()

        self.cycle.status = ProgramCycle.DRAFT
        self.cycle.save()
        self.cycle.set_finish()
        self.cycle.refresh_from_db()
        assert self.cycle.status == ProgramCycle.DRAFT

        self.cycle.status = ProgramCycle.ACTIVE
        self.cycle.save()
        self.cycle.set_finish()
        self.cycle.refresh_from_db()
        assert self.cycle.status == ProgramCycle.FINISHED
        assert not self.cycle.can_remove_cycle

    def test_total_entitled_quantity_usd(self) -> None:
        assert self.cycle.total_entitled_quantity_usd == Decimal("0.0")
        PaymentPlanFactory(program_cycle=self.cycle, total_entitled_quantity_usd=Decimal(123.99))
        assert self.cycle.total_entitled_quantity_usd == Decimal("123.99")

    def test_total_undelivered_quantity_usd(self) -> None:
        assert self.cycle.total_undelivered_quantity_usd == Decimal("0.0")
        PaymentPlanFactory(program_cycle=self.cycle, total_undelivered_quantity_usd=Decimal(222.33))
        assert self.cycle.total_undelivered_quantity_usd == Decimal("222.33")

    def test_total_delivered_quantity_usd(self) -> None:
        assert self.cycle.total_delivered_quantity_usd == Decimal("0.0")
        PaymentPlanFactory(program_cycle=self.cycle, total_delivered_quantity_usd=Decimal(333.11))
        assert self.cycle.total_delivered_quantity_usd == Decimal("333.11")

    def test_cycle_validation_start_date(self) -> None:
        with self.assertRaisesMessage(DjangoValidationError, "Start date must be after the latest cycle."):
            ProgramCycleFactory(program=self.program, start_date=parse_date("2021-01-01"))

        with self.assertRaisesMessage(DjangoValidationError, "End date cannot be before start date."):
            ProgramCycleFactory(
                program=self.program,
                start_date=parse_date("2021-01-05"),
                end_date=parse_date("2021-01-01"),
            )

        cycle2 = ProgramCycleFactory(program=self.program)
        assert cycle2.start_date > parse_date(self.cycle.start_date)

        cycle_new = ProgramCycleFactory(program=self.program, start_date=parse_date("2099-01-01"))
        assert cycle_new.start_date > timezone.now().date()
