import logging

from django.utils import timezone

from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.payment.models import (
    Payment,
    PaymentHouseholdSnapshot,
    PaymentPlan,
)
from hct_mis_api.apps.payment.services.payment_household_snapshot_service import (
    bulk_create_payment_snapshot_data,
)
from hct_mis_api.apps.program.models import Program

logger = logging.getLogger(__name__)


def create_payment_snapshot() -> None:
    start_time = timezone.now()
    print("*** Starting Payment Snapshot creations ***\n", "*" * 60)
    print(f"Found Payments without snapshot: {Payment.all_objects.filter(household_snapshot__isnull=True).count()}")

    for ba in BusinessArea.objects.all().only("id", "name"):
        program_qs = Program.all_objects.filter(business_area_id=ba.id).only("id", "name")
        if program_qs:
            print(f"Processing {program_qs.count()} programs for {ba.name}.")
            for program in program_qs:
                for payment_plan in PaymentPlan.all_objects.filter(program=program):
                    payments_ids = list(
                        payment_plan.eligible_payments.filter(household_snapshot__isnull=True)
                        .values_list("id", flat=True)
                        .order_by("id")
                    )
                    bulk_create_payment_snapshot_data(payments_ids)

    print(f"Total PaymentHouseholdSnapshot: {PaymentHouseholdSnapshot.objects.count()}")
    print(f"Completed in {timezone.now() - start_time}\n", "*" * 60)
    print(
        f"== After creation new  PaymentHouseholdSnapshot Payment(s) without snapshot: {Payment.all_objects.filter(household_snapshot__isnull=True).count()} =="
    )
