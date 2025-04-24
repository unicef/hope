from django.core.exceptions import ValidationError
from django.test import TestCase

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.payment.fixtures import PaymentPlanFactory
from hct_mis_api.apps.payment.models import PaymentPlan
from hct_mis_api.apps.program.fixtures import ProgramCycleFactory, ProgramFactory
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.program.validators import ProgramValidator


class TestProgramValidators(TestCase):
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
        PaymentPlanFactory(program_cycle=self.program_cycle, status=PaymentPlan.Status.IN_REVIEW, created_by=self.user)

        with self.assertRaisesMessage(
            ValidationError, "All Payment Plans and Follow-Up Payment Plans have to be Reconciled."
        ):
            ProgramValidator.validate_status_change(**data)
        # add TP and no errors because we ignore TP statuses
        PaymentPlanFactory(program_cycle=self.program_cycle, status=PaymentPlan.Status.TP_OPEN, created_by=self.user)
        ProgramValidator.validate_status_change(**data)
