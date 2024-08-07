import logging
from typing import Optional

from django.db import transaction
from django.utils import timezone

from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.payment.models import PaymentPlan
from hct_mis_api.apps.program.models import Program

logger = logging.getLogger(__name__)


def program_cycle_data_migration(batch_size: Optional[int] = 1000) -> None:
    start_time = timezone.now()
    logger.info("Hi There! Started Program Cycle Data Migration.")
    for ba in BusinessArea.objects.all().only("id", "name"):
        logger.info(f"Started processing {ba.name}...")

        for program in Program.objects.filter(business_area_id=ba.pk).only(
            "id", "name", "start_date", "end_date", "status"
        ):
            logger.info(f"** Creating Program Cycles for program {program.name}")

            for payment_plan in PaymentPlan.objects.filter(program_id=program.pk).only("id", "unicef_id"):
                logger.info(f"** ** Processing Payment Plan {payment_plan.unicef_id}")
                with transaction.atomic():
                    pass
                    # target_population = payment_plan.target_population

    # TODO: assign Cycle to TP as well

    print(f"Congratulations! Done in {timezone.now() - start_time}")
