from django.core.management import BaseCommand
from django.db.models import OuterRef, Subquery

from hct_mis_api.apps.registration_datahub.models import (
    ImportedHousehold,
    ImportedIndividual,
)


def update_kobo_asset_id() -> None:
    ImportedHousehold.objects.exclude(flex_registrations_record__isnull=True).update(
        kobo_asset_id=Subquery(
            ImportedHousehold.objects.filter(pk=OuterRef("pk")).values("flex_registrations_record__source_id")[:1]
        )
    )
    ImportedIndividual.objects.exclude(household__flex_registrations_record__isnull=True).update(
        kobo_asset_id=Subquery(
            ImportedHousehold.objects.filter(pk=OuterRef("household__pk")).values(
                "flex_registrations_record__source_id"
            )[:1]
        )
    )


class Command(BaseCommand):
    help = "Fix unicef id for imported Households and Individuals"

    def handle(self, *args, **options):
        update_kobo_asset_id()
        self.stdout.write("Kobo asset id fixed for imported Households and Individuals")
