import logging
from typing import Any

from django.core.management import BaseCommand
from django.db import Error
from django_countries import countries

from hope.apps.geo.missing_countries import missing_countries
from hope.models.country import Country

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args: Any, **options: Any) -> None:
        initialize_countries()


def initialize_countries() -> dict:
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
    except Error as e:
        logger.warning(e)
        results["errors"].append(e)
    return results
