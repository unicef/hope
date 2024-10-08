from typing import Any

from django.core.management import BaseCommand

from hct_mis_api.apps.payment.models import PaymentRecord


class Command(BaseCommand):
    help = "Fix payment records delivered amount"

    def handle(self, *args: Any, **options: Any) -> None:
        self.stdout.write("Updating payment records")
        updated = PaymentRecord.objects.filter(status=PaymentRecord.STATUS_FORCE_FAILED).update(
            delivered_quantity=0,
            delivered_quantity_usd=0,
            delivery_date=None,
        )
        self.stdout.write(f"Updated {updated} payment records")
