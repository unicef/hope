from django.core.management import BaseCommand
from django.db.models import Q

from hct_mis_api.apps.household.models import Individual
from hct_mis_api.apps.registration_datahub.models import ImportedIndividual


def update_mis_unicef_id_individual_and_household() -> None:
    for imported_individual in ImportedIndividual.objects.filter(Q(mis_unicef_id__isnull=True) | Q(mis_unicef_id="")):
        individual = Individual.objects.filter(imported_individual_id=imported_individual.id).first()
        if individual:
            imported_individual.mis_unicef_id = individual.unicef_id
            imported_individual.save()

            if individual.household and imported_individual.household:
                imported_individual.household.mis_unicef_id = individual.household.unicef_id
                imported_individual.household.save()


class Command(BaseCommand):
    help = "Fix unicef id for imported Households and Individuals"

    def handle(self, *args, **options) -> None:
        update_mis_unicef_id_individual_and_household()
        self.stdout.write("Unicef id fixed for imported Households and Individuals")
