import logging
from typing import Optional

from django.db import transaction
from django.utils import timezone

from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.payment.models import PaymentPlan
from hct_mis_api.apps.program.models import Program, ProgramCycle
from hct_mis_api.apps.targeting.models import TargetPopulation

logger = logging.getLogger(__name__)


def adjust_cycles_start_and_end_dates_for_active_program(program: Program) -> None:
    logger.info("** ** ** Adjusting cycles start and end dates...")
    # TODO: add here some code XD
    # start_data = program.start_date
    # end_data = program.end_date
    #
    # cycles_qs = ProgramCycle.objects.filter(program=program)


def create_new_program_cycle(
    program_id: str, status: str, start_date: str, end_date: Optional[str] = None
) -> ProgramCycle:
    return ProgramCycle.objects.create(
        program_id=program_id,
        status=status,
        start_date=start_date,
        end_date=end_date,
        created_by=None,
    )


def processing_with_finished_program(payment_plan: PaymentPlan, start_date: str, end_date: str) -> None:
    # update if exists or create new cycle
    if ProgramCycle.objects.filter(program_id=payment_plan.program_id).exists():
        cycle = ProgramCycle.objects.filter(program_id=payment_plan.program_id).first()
        if cycle.start_date != start_date:
            cycle.start_date = start_date
        if cycle.end_date != end_date:
            cycle.end_date = end_date
        if cycle.status != ProgramCycle.FINISHED:
            cycle.status = ProgramCycle.FINISHED
        cycle.save(update_fields=["start_date", "end_date", "status"])
    else:
        cycle = create_new_program_cycle(str(payment_plan.program_id), ProgramCycle.FINISHED, start_date, end_date)

    # update TP
    TargetPopulation.objects.filter(id=payment_plan.target_population_id).update(program_cycle=cycle)
    # update Payment Plan
    PaymentPlan.objects.filter(id=payment_plan.id).update(program_cycle=cycle)


def processing_with_active_program(payment_plan: PaymentPlan) -> None:
    logger.info(f"** ** Processing Payment Plan {payment_plan.unicef_id}")
    payment_plan_start_date = str(payment_plan.start_date)
    payment_plan_end_date = str(payment_plan.end_date)

    if ProgramCycle.objects.filter(program_id=payment_plan.program_id).exists():
        cycle = ProgramCycle.objects.filter(program_id=payment_plan.program_id).first()
    else:
        cycle = create_new_program_cycle(
            str(payment_plan.program_id), ProgramCycle.ACTIVE, payment_plan_start_date, payment_plan_end_date
        )

    # check if any conflicts in the cycle
    new_hh_ids = list(payment_plan.eligible_payments.values_list("household_id", flat=True))

    for comparing_with_payment_plan in PaymentPlan.objects.filter(program_cycle=cycle):
        hh_ids_in_cycles = list(comparing_with_payment_plan.eligible_payments.values_list("household_id", flat=True))
        # create new cycle if any conflicts
        if any(hh_id in new_hh_ids for hh_id in hh_ids_in_cycles):
            cycle = create_new_program_cycle(
                str(payment_plan.program_id), ProgramCycle.ACTIVE, payment_plan_start_date, payment_plan_end_date
            )
            # just create new cycle and stop searching conflicts
            continue

    # update TP
    TargetPopulation.objects.filter(id=payment_plan.target_population_id).update(program_cycle=cycle)
    # update Payment Plan
    PaymentPlan.objects.filter(id=payment_plan.id).update(program_cycle=cycle)

    # adjust cycle start and end dates based on PaymentPlan
    # if cycle start date if later than payment plan
    if cycle.start_date > payment_plan.start_date:
        cycle.start_date = payment_plan.start_date
    # if end date is earlier should set payment plan end date
    if cycle.end_date < payment_plan.end_date:
        cycle.end_date = payment_plan.end_date
    if cycle.status != ProgramCycle.ACTIVE:
        cycle.status = ProgramCycle.FINISHED
    cycle.save(update_fields=["start_date", "end_date", "status"])


def program_cycle_data_migration(batch_size: int = 1000) -> None:
    start_time = timezone.now()
    logger.info("Hi There! Started Program Cycle Data Migration.")
    for ba in BusinessArea.objects.all().only("id", "name"):
        logger.info(f"Started processing {ba.name}...")

        for program in Program.objects.filter(business_area_id=ba.id).only(
            "id", "name", "start_date", "end_date", "status"
        ):
            logger.info(f"** Creating Program Cycles for program {program.name}")

            payment_plan_qs = PaymentPlan.objects.filter(program_id=program.id).only("id")
            pp_count = payment_plan_qs.count()
            pp_ids = list(payment_plan_qs.values_list("id", flat=True))

            for batch_start in range(0, pp_count, batch_size):
                batch_end = batch_start + batch_size
                logger.info(f"Handling {batch_start} - {batch_end}/{pp_count} PaymentPlans")

                processing_ids = pp_ids[batch_start:batch_end]
                for pp_id in processing_ids:
                    with transaction.atomic():
                        payment_plan = PaymentPlan.objects.select_related("target_population").get(id=pp_id)

                        if program.status == Program.FINISHED:
                            start_data = program.start_date
                            end_data = program.end_date

                            processing_with_finished_program(payment_plan, start_data, end_data)

                        if program.status == Program.ACTIVE:
                            processing_with_active_program(payment_plan)

            # after create all Cycles let's adjust dates to find any overlapping
            adjust_cycles_start_and_end_dates_for_active_program(program)

    print(f"Congratulations! Done in {timezone.now() - start_time}")
