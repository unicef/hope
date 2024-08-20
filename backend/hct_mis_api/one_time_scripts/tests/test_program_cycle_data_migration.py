from django.test.testcases import TestCase

from freezegun import freeze_time

from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.household.fixtures import create_household_and_individuals
from hct_mis_api.apps.payment.fixtures import PaymentFactory, PaymentPlanFactory
from hct_mis_api.apps.payment.models import PaymentPlan
from hct_mis_api.apps.program.fixtures import ProgramCycleFactory, ProgramFactory
from hct_mis_api.apps.program.models import Program, ProgramCycle
from hct_mis_api.apps.targeting.fixtures import TargetPopulationFactory
from hct_mis_api.apps.targeting.models import TargetPopulation
from hct_mis_api.one_time_scripts.program_cycle_data_migration import (
    program_cycle_data_migration,
)


class TestProgramCycleDataMigration(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        ba = create_afghanistan()
        start_date = "2022-10-10"
        end_date = "2023-10-10"
        with freeze_time("2020-10-10"):
            program_finished = ProgramFactory(
                name="Finished 001",
                business_area=ba,
                start_date="2022-10-10",
                end_date="2022-10-29",
                status=Program.FINISHED,
                cycle__title="Already Created Cycle for program_finished",
                cycle__status=ProgramCycle.DRAFT,
                cycle__start_date="2022-10-11",
                cycle__end_date="2022-10-12",
            )
            program_finished2 = ProgramFactory(
                name="Finished 002",
                business_area=ba,
                start_date="2022-11-10",
                end_date="2022-11-30",
                status=Program.FINISHED,
                cycle__title="Cycle_program_finished2",
                cycle__status=ProgramCycle.DRAFT,
                cycle__start_date="2022-10-11",
                cycle__end_date="2022-10-12",
            )
            # remove default program cycle for program_finished2
            ProgramCycle.objects.filter(title="Cycle_program_finished2").delete()
            tp_1 = TargetPopulationFactory(program=program_finished, program_cycle=None)
            tp_2 = TargetPopulationFactory(program=program_finished2, program_cycle=None)
            PaymentPlanFactory(
                program=program_finished,
                target_population=tp_1,
                program_cycle=None,
                start_date=start_date,
                end_date=end_date,
            )
            PaymentPlanFactory(
                program=program_finished2,
                target_population=tp_2,
                program_cycle=None,
                start_date=start_date,
                end_date=end_date,
            )

            # active programs
            program_active_001 = ProgramFactory(
                name="Active 001",
                business_area=ba,
                start_date="2023-01-01",
                end_date="2022-01-30",
                status=Program.ACTIVE,
                cycle__title="Cycle for program_active_001",
                cycle__status=ProgramCycle.DRAFT,
                cycle__start_date="2023-01-01",
                cycle__end_date="2023-01-30",
            )
            program_active_002 = ProgramFactory(
                name="Active 002",
                business_area=ba,
                start_date="2023-02-01",
                end_date="2023-02-25",
                status=Program.ACTIVE,
                cycle__title="Cycle for program_active_002",
                cycle__status=ProgramCycle.DRAFT,
                cycle__start_date="2023-02-01",
                cycle__end_date="2023-02-25",
            )
            ProgramCycle.objects.filter(title="Cycle for program_active_002").delete()
            cls.tp_3 = TargetPopulationFactory(program=program_active_001, program_cycle=None)
            cls.tp_4 = TargetPopulationFactory(program=program_active_002, program_cycle=None)
            ProgramCycleFactory(
                program=program_active_002,
                title="Cycle 01",
                start_date="2023-02-10",
                end_date=None,
            )
        household_1, inds = create_household_and_individuals(
            household_data={
                "business_area": ba,
                "program": program_finished,
            },
            individuals_data=[
                {
                    "business_area": ba,
                    "program": program_finished,
                },
            ],
        )
        household_2, inds = create_household_and_individuals(
            household_data={
                "business_area": ba,
                "program": program_finished,
            },
            individuals_data=[
                {
                    "business_area": ba,
                    "program": program_finished,
                },
            ],
        )
        household_3, inds = create_household_and_individuals(
            household_data={
                "business_area": ba,
                "program": program_finished,
            },
            individuals_data=[
                {
                    "business_area": ba,
                    "program": program_finished,
                },
            ],
        )
        household_4, inds = create_household_and_individuals(
            household_data={
                "business_area": ba,
                "program": program_finished,
            },
            individuals_data=[
                {
                    "business_area": ba,
                    "program": program_finished,
                },
            ],
        )
        household_5, inds = create_household_and_individuals(
            household_data={
                "business_area": ba,
                "program": program_finished,
            },
            individuals_data=[
                {
                    "business_area": ba,
                    "program": program_finished,
                },
            ],
        )
        household_6, inds = create_household_and_individuals(
            household_data={
                "business_area": ba,
                "program": program_finished,
            },
            individuals_data=[
                {
                    "business_area": ba,
                    "program": program_finished,
                },
            ],
        )

        cls.pp_1 = PaymentPlanFactory(
            name="Payment Plan pp1",
            program=program_active_001,
            target_population=cls.tp_3,
            program_cycle=None,
            start_date=start_date,
            end_date=end_date,
        )
        cls.pp_2 = PaymentPlanFactory(
            name="Payment Plan pp2",
            program=program_active_001,
            target_population=cls.tp_3,
            program_cycle=None,
            start_date=start_date,
            end_date=end_date,
        )
        PaymentFactory(household=household_1, parent=cls.pp_1, status="Distribution Successful")
        PaymentFactory(household=household_2, parent=cls.pp_2, status="Distribution Successful")

        cls.pp_3 = PaymentPlanFactory(
            name="Payment Plan pp3",
            program=program_active_002,
            target_population=cls.tp_4,
            program_cycle=None,
            start_date=start_date,
            end_date=end_date,
        )
        cls.pp_4 = PaymentPlanFactory(
            name="Payment Plan pp4",
            program=program_active_002,
            target_population=cls.tp_4,
            program_cycle=None,
            start_date=start_date,
            end_date=end_date,
        )
        cls.pp_5 = PaymentPlanFactory(
            name="Payment Plan pp5",
            program=program_active_002,
            target_population=cls.tp_4,
            program_cycle=None,
            start_date=start_date,
            end_date=end_date,
        )

        # cycle 1 = Cycle 01
        PaymentFactory(household=household_3, parent=cls.pp_3, status="Distribution Successful")
        PaymentFactory(household=household_4, parent=cls.pp_3, status="Distribution Successful")

        # cycle 2 = new created
        PaymentFactory(household=household_4, parent=cls.pp_4, status="Distribution Successful")
        PaymentFactory(household=household_5, parent=cls.pp_4, status="Distribution Successful")

        # cycle 3 = new created
        PaymentFactory(household=household_5, parent=cls.pp_5, status="Distribution Successful")
        PaymentFactory(household=household_6, parent=cls.pp_5, status="Distribution Successful")
        PaymentFactory(household=household_3, parent=cls.pp_5, status="Distribution Successful")

    def test_program_cycle_data_migration(self) -> None:
        # check cycle for program_active_002
        self.assertEqual(ProgramCycle.objects.filter(program=self.pp_3.program).count(), 1)
        self.assertEqual(ProgramCycle.objects.filter(program=self.pp_3.program).first().title, "Cycle 01")

        # run script
        program_cycle_data_migration()

        program_finished = Program.objects.get(name="Finished 001")
        program_finished2 = Program.objects.get(name="Finished 002")
        cycle_for_program_finished = program_finished.cycles.first()
        self.assertEqual(program_finished.start_date, cycle_for_program_finished.start_date)
        self.assertEqual(program_finished.end_date, cycle_for_program_finished.end_date)
        self.assertEqual(cycle_for_program_finished.status, ProgramCycle.FINISHED)
        self.assertEqual(TargetPopulation.objects.filter(program_cycle=cycle_for_program_finished).count(), 1)
        self.assertEqual(PaymentPlan.objects.filter(program_cycle=cycle_for_program_finished).count(), 1)

        cycle_for_program_finished2 = program_finished2.cycles.first()
        self.assertEqual(program_finished2.start_date, cycle_for_program_finished2.start_date)
        self.assertEqual(program_finished2.end_date, cycle_for_program_finished2.end_date)
        self.assertEqual(cycle_for_program_finished2.status, ProgramCycle.FINISHED)
        self.assertEqual(TargetPopulation.objects.filter(program_cycle=cycle_for_program_finished2).count(), 1)
        self.assertEqual(PaymentPlan.objects.filter(program_cycle=cycle_for_program_finished2).count(), 1)

        # check with active program
        self.pp_1.refresh_from_db()
        self.pp_2.refresh_from_db()
        self.tp_3.refresh_from_db()

        self.assertEqual(self.pp_1.program_cycle.status, ProgramCycle.ACTIVE)
        # new default name starts with "Cycle {PaymentPlan.start_date} ({random 4 digits})"
        self.assertTrue(self.pp_1.program_cycle.title.startswith("Cycle 2022-10-10 ("))
        self.assertTrue(self.tp_3.program_cycle.title.startswith("Cycle 2022-10-10 ("))

        self.pp_3.refresh_from_db()
        self.pp_4.refresh_from_db()
        self.pp_5.refresh_from_db()
        self.tp_4.refresh_from_db()

        self.assertEqual(self.pp_3.program_cycle.status, ProgramCycle.ACTIVE)
        self.assertTrue(self.pp_3.program_cycle.title.startswith("Cycle 2022-10-10 ("))
        self.assertEqual(self.pp_4.program_cycle.status, ProgramCycle.ACTIVE)
        self.assertEqual(self.pp_5.program_cycle.status, ProgramCycle.ACTIVE)
        self.assertEqual(self.tp_4.program_cycle.status, ProgramCycle.ACTIVE)

        program_active_002 = self.pp_3.program
        values_cycles = ProgramCycle.objects.filter(program=program_active_002).values(
            "title", "start_date", "end_date"
        )
        self.assertEqual(values_cycles.count(), 3)
