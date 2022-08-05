from django.core.management import BaseCommand

from hct_mis_api.apps.core.exchange_rates.utils import fix_exchange_rates


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
        fix_exchange_rates(all=True)
        if options["silent"] is False:
            self.stdout.write("Exchange rates for Payment Records successfully modified")
