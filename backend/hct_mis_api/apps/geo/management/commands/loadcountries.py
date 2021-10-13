from django.core.management import BaseCommand

from django_countries import countries

from hct_mis_api.apps.geo.models import Country


class Command(BaseCommand):
    def handle(self, *args, **options):
        for c in countries:
            defaults = {
                "name": c.name,
                "short_name": c.name,
                "iso_code3": countries.alpha3(c.code),
                "iso_num": str(countries.numeric(c.code)).rjust(4, "0"),
                "lft": 0,
                "rght": 0,
                "tree_id": 0,
                "level": 0,
            }
            Country.objects.get_or_create(iso_code2=c.code, defaults=defaults)
