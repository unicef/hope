import logging
from datetime import date, timedelta
from random import randint
from typing import List

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.payment.models import Payment, PaymentPlan
from hct_mis_api.apps.program.models import Program, ProgramCycle
from hct_mis_api.apps.targeting.models import TargetPopulation

logger = logging.getLogger(__name__)


def adjust_cycles_start_and_end_dates_for_active_program(program: Program) -> None:
    logger.info("** ** ** Adjusting cycles start and end dates...")
    cycles_qs = ProgramCycle.objects.filter(program=program).only("start_date", "end_date").order_by("start_date")
    if not cycles_qs:
        return

    previous_cycle = None
    with transaction.atomic():
        for cycle in cycles_qs:
            # probably it's not possible but to be sure that no any cycles without end_date
            if cycle.end_date is None:
                cycle.end_date = cycle.start_date

            if previous_cycle:
                if cycle.start_date <= previous_cycle.end_date:
                    cycle.start_date = previous_cycle.end_date + timedelta(days=1)
            if cycle.end_date < cycle.start_date:
                cycle.end_date = cycle.start_date
            try:
                cycle.save()
            except ValidationError:
                # if validation error just save one day cycle
                cycle.end_date = cycle.start_date
                cycle.save()

            previous_cycle = cycle


def generate_unique_cycle_title(start_date: str) -> str:
    # add to the cycle title just random 4 digits
    while True:
        cycle_name = f"Cycle {start_date} ({str(randint(1111, 9999))})"
        if not ProgramCycle.objects.filter(title=cycle_name).exists():
            return cycle_name


def create_new_program_cycle(program_id: str, status: str, start_date: date, end_date: date) -> ProgramCycle:
    return ProgramCycle.objects.create(
        title=generate_unique_cycle_title(str(start_date)),
        program_id=program_id,
        status=status,
        start_date=start_date,
        end_date=end_date,
        created_by=None,
    )


def processing_with_finished_program(program: Program) -> None:
    start_date = program.start_date
    end_date = program.end_date
    program_id_str = str(program.id)
    # update if exists or create new cycle
    if cycle := ProgramCycle.objects.filter(program_id=program.id).first():
        if cycle.start_date != start_date:
            cycle.start_date = start_date
        if cycle.end_date != end_date:
            cycle.end_date = end_date
        if cycle.status != ProgramCycle.FINISHED:
            cycle.status = ProgramCycle.FINISHED
        cycle.save(update_fields=["start_date", "end_date", "status"])
    else:
        cycle = create_new_program_cycle(str(program.id), ProgramCycle.FINISHED, start_date, end_date)

    # update TP
    TargetPopulation.objects.filter(program_id=program_id_str).update(program_cycle=cycle)
    # update Payment Plan
    PaymentPlan.objects.filter(program_id=program_id_str).update(program_cycle=cycle)


def processing_with_active_program(payment_plans_list: list, default_cycle_id: List[str]) -> None:
    hhs_in_cycles_dict = dict()
    for comparing_with_pp in payment_plans_list:
        new_hh_ids = set(
            [str(hh_id) for hh_id in comparing_with_pp.eligible_payments.values_list("household_id", flat=True)]
        )
        cycles = (
            ProgramCycle.objects.filter(program_id=comparing_with_pp.program_id)
            .exclude(id__in=default_cycle_id)
            .only("id")
        )
        for cycle in cycles:
            cycle_id_str = str(cycle.id)
            if cycle_id_str not in hhs_in_cycles_dict:
                hhs_in_cycles_dict[cycle_id_str] = set(
                    [
                        str(hh_id)
                        for hh_id in Payment.objects.filter(parent__program_cycle=cycle).values_list(
                            "household_id", flat=True
                        )
                    ]
                )
            hh_ids_in_cycles = hhs_in_cycles_dict[cycle_id_str]

            # check any conflicts
            if new_hh_ids.intersection(hh_ids_in_cycles):
                continue

            TargetPopulation.objects.filter(id=comparing_with_pp.target_population_id).update(program_cycle=cycle)
            comparing_with_pp.program_cycle = cycle
            hhs_in_cycles_dict[cycle_id_str].update(new_hh_ids)
            break

        if not comparing_with_pp.program_cycle:
            cycle = create_new_program_cycle(
                str(comparing_with_pp.program_id),
                ProgramCycle.ACTIVE,
                comparing_with_pp.start_date.date(),
                comparing_with_pp.end_date.date(),
            )
            TargetPopulation.objects.filter(id=comparing_with_pp.target_population_id).update(program_cycle=cycle)
            comparing_with_pp.program_cycle = cycle
            hhs_in_cycles_dict[str(cycle.id)] = new_hh_ids

        comparing_with_pp.save(update_fields=["program_cycle"])


def program_cycle_data_migration() -> None:
    start_time = timezone.now()
    logger.info("Hi There! Started Program Cycle Data Migration.")
    logger.info(f"Cycles before running creation: {ProgramCycle.objects.all().count()}")
    for ba in BusinessArea.objects.all().only("id", "name"):
        logger.info(f"Started processing {ba.name}...")

        # FINISHED programs
        for finished_program in (
            Program.objects.filter(business_area_id=ba.id)
            .exclude(status__in=[Program.DRAFT, Program.ACTIVE])
            .only("id", "name", "start_date", "end_date", "status")
        ):
            processing_with_finished_program(finished_program)

        # ACTIVE and DRAFT programs
        for program in (
            Program.objects.filter(business_area_id=ba.id)
            .exclude(status=Program.FINISHED)
            .only("id", "name", "start_date", "end_date", "status")
        ):
            with transaction.atomic():
                logger.info(f"** Creating Program Cycles for program {program.name}")

                default_cycle = ProgramCycle.objects.filter(program_id=program.id).first()
                default_cycle_id: List = []
                if default_cycle:
                    default_cycle_id.append(str(default_cycle.id))
                else:
                    logger.info(f"###### Default Program Cycles for program {program.name} does not exist")

                payment_plan_qs = (
                    PaymentPlan.objects.filter(program_id=program.id)
                    .order_by("start_date", "created_at")
                    .only("id", "program_id", "target_population_id")
                )
                PaymentPlan.objects.filter(program_id=program.id).update(program_cycle=None)
                processing_with_active_program(list(payment_plan_qs), default_cycle_id)

                if default_cycle:
                    default_cycle.delete(soft=False)

                # after create all Cycles let's adjust dates to find any overlapping
                adjust_cycles_start_and_end_dates_for_active_program(program)

    logger.info(f"Cycles after creation: {ProgramCycle.objects.all().count()}")
    print(f"Congratulations! Done in {timezone.now() - start_time}")
