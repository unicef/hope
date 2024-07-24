from django.core.exceptions import ValidationError
from django.test import TestCase

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.payment.fixtures import PaymentPlanFactory
from hct_mis_api.apps.payment.models import PaymentPlan
from hct_mis_api.apps.program.fixtures import ProgramCycleFactory, ProgramFactory
from hct_mis_api.apps.program.models import Program, ProgramCycle
from hct_mis_api.apps.program.validators import (
    ProgramCycleDeletionValidator,
    ProgramCycleValidator,
    ProgramValidator,
)


class TestProgramValidators(TestCase):
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
        cls.program_cycle = ProgramCycleFactory(
            program=cls.program,
            start_date="2021-01-01",
            end_date="2022-01-01",
            title="Cycle 002",
        )

    def test_program_validator(self) -> None:
        data = {"program": self.program, "program_data": {"status": Program.FINISHED}}
        self.program.status = Program.ACTIVE
        self.program.save()
        PaymentPlanFactory(program=self.program, program_cycle=self.program_cycle, status=PaymentPlan.Status.IN_REVIEW)

        with self.assertRaisesMessage(
            ValidationError, "All Payment Plans and Follow-Up Payment Plans have to be Reconciled."
        ):
            ProgramValidator.validate_status_change(**data)

    def test_program_cycle_validator(self) -> None:
        data = {"program": self.program}
        with self.assertRaisesMessage(
            ValidationError, "Create/Update Programme Cycle is possible only for Active Programme."
        ):
            ProgramCycleValidator.validate_program(**data)

        # TODO add more
        # ValidationError("Programme Cycle start date cannot be earlier than programme start date")
        # ValidationError("Programme Cycle end date cannot be earlier than programme end date")
        # ValidationError("All Programme Cycles should have end date for creation new one.")
        # ValidationError("Programme Cycles' timeframes must not overlap.")
        # ValidationError("Not possible leave the Programme Cycle start date empty.")
        # ValidationError("Not possible leave the Programme Cycle end date empty if it was empty upon starting the edit.")
        # ValidationError("Not possible leave the Programme Cycle title empty.")

    def test_program_cycle_delete_validator(self) -> None:
        data = {"program_cycle": self.program_cycle}
        with self.assertRaisesMessage(ValidationError, "Only Programme Cycle for Active Programme can be deleted."):
            ProgramCycleDeletionValidator.validate_is_deletable(**data)

        with self.assertRaisesMessage(ValidationError, "Only Draft Programme Cycle can be deleted."):
            self.program.status = Program.ACTIVE
            self.program.save()
            self.program_cycle.refresh_from_db()
            ProgramCycleDeletionValidator.validate_is_deletable(**data)

        with self.assertRaisesMessage(ValidationError, "Don’t allow to delete last Cycle."):
            last_program_cycle = ProgramCycle.objects.get(title="Default Cycle 001")
            last_program_cycle.status = ProgramCycle.DRAFT
            last_program_cycle.save()
            ProgramCycleDeletionValidator.validate_is_deletable(**{"program_cycle": last_program_cycle})
