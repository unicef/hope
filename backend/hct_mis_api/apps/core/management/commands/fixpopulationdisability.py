from django.core.management import BaseCommand

from hct_mis_api.apps.household.models import DISABLED, NOT_DISABLED, Individual


class Command(BaseCommand):
    help = "Fix Population disability if disability certificate picture added"

    def update_individual_disability(self):
        qs = (
            Individual.objects.filter(disability=NOT_DISABLED)
            .exclude(disability_certificate_picture__isnull=True)
            .exclude(disability_certificate_picture="")
            .update(disability=DISABLED)
        )

        print(f"Fixed {qs} object(s).")

    def handle(self, *args, **options):
        print("Starting Fix Population Disability")

        self.update_individual_disability()
