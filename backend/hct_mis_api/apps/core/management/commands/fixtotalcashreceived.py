from time import time

from django.core.management import BaseCommand
from hct_mis_api.apps.payment.services.handle_total_cash_in_households import handle_total_cash_in_households


class Command(BaseCommand):
    help = "Fix total cash received in household"

    def handle(self, *args, **options):
        start_time = time()
        handle_total_cash_in_households()
        print(f"time: {time()-start_time}")
