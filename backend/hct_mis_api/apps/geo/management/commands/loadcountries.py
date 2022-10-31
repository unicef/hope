import logging

from django.core.management import BaseCommand

from django_countries import countries

from hct_mis_api.apps.geo.missing_countries import missing_countries
from hct_mis_api.apps.geo.models import Country

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **options) -> None:
        initialize_countries()


def initialize_countries() -> None:
    results = {"errors": []}
    try:
        default_data = {
            "lft": 0,
            "rght": 0,
            "tree_id": 0,
            "level": 0,
        }
        for c in countries:
            data = {
                "name": c.name,
                "short_name": c.name,
                "iso_code3": countries.alpha3(c.code),
                "iso_num": str(countries.numeric(c.code)).rjust(4, "0"),
                **default_data,
            }
            Country.objects.get_or_create(iso_code2=c.code, defaults=data)

        for c in missing_countries:
            data = {
                "name": c.get("name"),
                "short_name": c.get("name"),
                "iso_code3": c.get("iso_code3"),
                "iso_num": c.get("iso_num").rjust(4, "0"),
                **default_data,
            }
            country = Country.objects.filter(iso_code2=c.get("iso_code2")).first()
            if country:
                country.short_name = c.get("name")
            else:
                country = Country(iso_code2=c.get("iso_code2"), **data)
            country.save()
    except Exception as e:
        logger.exception(e)
        results["errors"].append(e)
    return results
