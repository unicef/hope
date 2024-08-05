from django.test import TestCase

from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.program.fixtures import ProgramCycleFactory, ProgramFactory
from hct_mis_api.apps.program.models import ProgramCycle
from hct_mis_api.apps.targeting.fixtures import TargetPopulationFactory
from hct_mis_api.one_time_scripts.assign_program_cycle_to_target_population import (
    assign_program_cycle_to_target_population,
)


class TestAssignProgramToGrievanceTickets(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        business_area = create_afghanistan()
        cls.program = ProgramFactory(
            business_area=business_area,
            cycle__title="Default Cycle",
            cycle__start_date="2020-01-01",
            cycle__end_date="2020-01-25",
        )
        cls.tp = TargetPopulationFactory(program=cls.program, program_cycle=None)
        # other cycle
        ProgramCycleFactory(
            program=cls.program,
            title="Last Cycle",
            status=ProgramCycle.DRAFT,
            start_date="2022-01-01",
            end_date="2022-01-22",
        )

    def test_update_tp_cycles(self) -> None:
        self.assertIsNone(self.tp.program_cycle)
        program_cycle = self.program.cycles.first()
        self.assertEqual(program_cycle.title, "Default Cycle")
        cycle_2 = self.program.cycles.last()
        self.assertEqual(cycle_2.title, "Last Cycle")
        self.assertEqual(ProgramCycle.objects.count(), 2)
        self.assertEqual(self.program.cycles.all().count(), 2)

        assign_program_cycle_to_target_population()

        self.tp.refresh_from_db()
        self.assertIsNotNone(self.tp.program_cycle)
        self.assertEqual(self.tp.program_cycle.title, "Default Cycle")
