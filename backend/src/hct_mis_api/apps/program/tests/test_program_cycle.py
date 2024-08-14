from decimal import Decimal

from django.test import TestCase

from rest_framework.exceptions import ValidationError

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.payment.fixtures import PaymentPlanFactory
from hct_mis_api.apps.program.fixtures import ProgramCycleFactory, ProgramFactory
from hct_mis_api.apps.program.models import Program, ProgramCycle


class TestProgramCycleMethods(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
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
        self.assertEqual(self.cycle.program.status, Program.ACTIVE)

    def test_set_active(self) -> None:
        with self.assertRaisesMessage(ValidationError, "Program should be within Active status."):
            self.cycle.set_active()
        self.activate_program()

        self.cycle.status = ProgramCycle.DRAFT
        self.cycle.save()
        self.assertEqual(self.cycle.status, ProgramCycle.DRAFT)
        self.cycle.set_active()
        self.cycle.refresh_from_db()
        self.assertEqual(self.cycle.status, ProgramCycle.ACTIVE)

        self.cycle.status = ProgramCycle.FINISHED
        self.cycle.save()
        self.assertEqual(self.cycle.status, ProgramCycle.FINISHED)
        self.cycle.set_active()
        self.cycle.refresh_from_db()
        self.assertEqual(self.cycle.status, ProgramCycle.ACTIVE)

        self.cycle.status = ProgramCycle.ACTIVE
        self.cycle.save()
        self.assertEqual(self.cycle.status, ProgramCycle.ACTIVE)
        self.cycle.set_active()
        self.cycle.refresh_from_db()
        self.assertEqual(self.cycle.status, ProgramCycle.ACTIVE)

    def test_set_draft(self) -> None:
        with self.assertRaisesMessage(ValidationError, "Program should be within Active status."):
            self.cycle.set_active()
        self.activate_program()

        self.cycle.status = ProgramCycle.FINISHED
        self.cycle.save()
        self.assertEqual(self.cycle.status, ProgramCycle.FINISHED)
        self.cycle.set_draft()
        self.cycle.refresh_from_db()
        self.assertEqual(self.cycle.status, ProgramCycle.FINISHED)

        self.cycle.status = ProgramCycle.ACTIVE
        self.cycle.save()
        self.assertEqual(self.cycle.status, ProgramCycle.ACTIVE)
        self.cycle.set_draft()
        self.cycle.refresh_from_db()
        self.assertEqual(self.cycle.status, ProgramCycle.DRAFT)

    def test_set_finish(self) -> None:
        with self.assertRaisesMessage(ValidationError, "Program should be within Active status."):
            self.cycle.set_finish()
        self.activate_program()

        self.cycle.status = ProgramCycle.DRAFT
        self.cycle.save()
        self.cycle.set_finish()
        self.cycle.refresh_from_db()
        self.assertEqual(self.cycle.status, ProgramCycle.DRAFT)

        self.cycle.status = ProgramCycle.ACTIVE
        self.cycle.save()
        self.cycle.set_finish()
        self.cycle.refresh_from_db()
        self.assertEqual(self.cycle.status, ProgramCycle.FINISHED)

    def test_total_entitled_quantity_usd(self) -> None:
        self.assertEqual(self.cycle.total_entitled_quantity_usd, Decimal("0.0"))
        PaymentPlanFactory(program=self.program, program_cycle=self.cycle, total_entitled_quantity_usd=Decimal(123.99))
        self.assertEqual(self.cycle.total_entitled_quantity_usd, Decimal("123.99"))

    def test_total_undelivered_quantity_usd(self) -> None:
        self.assertEqual(self.cycle.total_undelivered_quantity_usd, Decimal("0.0"))
        PaymentPlanFactory(
            program=self.program, program_cycle=self.cycle, total_undelivered_quantity_usd=Decimal(222.33)
        )
        self.assertEqual(self.cycle.total_undelivered_quantity_usd, Decimal("222.33"))

    def test_total_delivered_quantity_usd(self) -> None:
        self.assertEqual(self.cycle.total_delivered_quantity_usd, Decimal("0.0"))
        PaymentPlanFactory(program=self.program, program_cycle=self.cycle, total_delivered_quantity_usd=Decimal(333.11))
        self.assertEqual(self.cycle.total_delivered_quantity_usd, Decimal("333.11"))
