from django.core.management import BaseCommand

from hct_mis_api.apps.household.models import Individual
from hct_mis_api.apps.registration_datahub.models import ImportedIndividual, ImportedHousehold


def update_mis_unicef_id_individual_and_household():

    for imported_individual in ImportedIndividual.objects.exclude(mis_unicef_id__null=False):
        individual = Individual.objects.filter(imported_individual_id=imported_individual.id).first()
        if individual:
            imported_individual.mis_unicef_id = individual.pk
            imported_individual.save()

            if individual.household and imported_individual.household:
                imported_household = ImportedHousehold.objects.get(id=imported_individual.household.id)
                imported_household.mis_unicef_id = individual.household.unicef_id
                imported_household.save()


class Command(BaseCommand):
    help = "Fix unicef id for imported Households and Individuals"

    def handle(self, *args, **options):
        update_mis_unicef_id_individual_and_household()
        self.stdout.write("Unicef id fixed for imported Households and Individuals")
