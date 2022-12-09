from datetime import datetime

from django.core.management import BaseCommand
from django.db import transaction

from hct_mis_api.apps.household.models import Individual
from hct_mis_api.apps.registration_datahub.models import ImportedIndividual


def update_birth_date() -> None:
    updated = ImportedIndividual.objects.filter(household__country="UA", birth_date__lt=datetime(1923, 1, 1)).update(
        birth_date=datetime(1923, 1, 1)
    )
    print(f"{updated} updated imported individuals")
    updated = Individual.objects.filter(household__country__name="Ukraine", birth_date__lt=datetime(1923, 1, 1)).update(
        birth_date=datetime(1923, 1, 1)
    )
    print(f"{updated} updated individuals")


class Command(BaseCommand):
    help = "Fix birth date"

    def handle(self, *args, **options):
        print("Fix birth date - start")
        try:
            with transaction.atomic():
                update_birth_date()
        except Exception as e:
            print(e)
        print("Fix birth date - end")
