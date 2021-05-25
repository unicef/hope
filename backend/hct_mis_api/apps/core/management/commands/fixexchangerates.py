from decimal import Decimal

from django.core.management import BaseCommand

from hct_mis_api.apps.core.exchange_rates import ExchangeRates
from hct_mis_api.apps.payment.models import PaymentRecord


class Command(BaseCommand):
    help = "Fix Exchange Rates for Payment Records"

    def add_arguments(self, parser):
        parser.add_argument(
            "--silent",
            dest="silent",
            const=True,
            default=True,
            action="store",
            nargs="?",
            type=bool,
            help="Silence the command output messages",
        )

    def handle(self, *args, **options):
        all_payment_records = PaymentRecord.objects.all()

        exchange_rates_client = ExchangeRates()

        for payment_record in all_payment_records:
            exchange_rate = exchange_rates_client.get_exchange_rate_for_currency_code(
                payment_record.currency, payment_record.cash_plan.dispersion_date
            )

            if exchange_rate is None:
                exchange_rate = Decimal(1)
            else:
                exchange_rate = Decimal(exchange_rate)
            payment_record.delivered_quantity_usd = Decimal(payment_record.delivered_quantity / exchange_rate).quantize(
                Decimal(".01")
            )

        PaymentRecord.objects.bulk_update(all_payment_records, ["delivered_quantity_usd"], 1000)

        if options["silent"] is False:
            self.stdout.write("Exchange rates for Payment Records successfully modified")
