from time import time

from django.core.management import BaseCommand
from django.db import transaction

from hct_mis_api.apps.payment.services.handle_total_cash_in_households import handle_total_cash_in_households
from hct_mis_api.apps.targeting.models import TargetPopulation


class Command(BaseCommand):
    help = "Fix background TP"

    @transaction.atomic
    def handle(self, *args, **options):
        print("Fixing locked, sent TPs")
        locked_and_finished_tps = TargetPopulation.objects.filter(
            status__in=[
                TargetPopulation.STATUS_LOCKED,
                TargetPopulation.STATUS_PROCESSING,
                TargetPopulation.STATUS_READY_FOR_CASH_ASSIST,
                TargetPopulation.STATUS_STEFICON_COMPLETED,
                TargetPopulation.STATUS_STEFICON_ERROR,
                TargetPopulation.STATUS_STEFICON_WAIT,
            ],
        )
        locked_and_finished_tps.update(build_status=TargetPopulation.BUILD_STATUS_OK)
        for tp in locked_and_finished_tps:
            tp.refresh_stats()
            tp.save()
        print("Rebuilding OPEN TPs")
        open_tps = TargetPopulation.objects.filter(status=TargetPopulation.STATUS_OPEN, created_at__year__gt="2021")
        for tp in open_tps:
            print(tp)
            tp.full_rebuild()
            tp.save()
