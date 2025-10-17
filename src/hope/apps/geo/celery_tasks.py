import csv
import logging

from celery import shared_task
from django.db import transaction

from hope.apps.geo.models import Area, AreaType, Country
from hope.apps.utils.sentry import sentry_tags

logger = logging.getLogger(__name__)


@shared_task
@sentry_tags
def import_areas_from_csv_task(csv_data: str) -> None:
    """Import areas from a CSV file in a background task."""
    reader = csv.DictReader(csv_data.splitlines())
    rows = list(reader)

    with transaction.atomic():
        country = Country.objects.get(short_name=rows[0]["Country"])

        keys = list(rows[0].keys())
        num_cols = len(keys)

        d = num_cols // 2
        name_headers = keys[:d]
        p_code_headers = keys[d:]

        area_types_cache = {(at.name, at.area_level): at for at in AreaType.objects.filter(country=country)}
        for level, name_header in enumerate(name_headers):
            if (name_header, level) not in area_types_cache:
                parent_type = None
                if level > 0:
                    parent_level = level - 1
                    parent_name = name_headers[parent_level]
                    parent_type = area_types_cache.get((parent_name, parent_level))

                area_type, created = AreaType.objects.get_or_create(
                    name=name_header,
                    country=country,
                    area_level=level,
                    defaults={"parent": parent_type},
                )
                if not created and area_type.parent != parent_type:
                    area_type.parent = parent_type
                    area_type.save()
                area_types_cache[(name_header, level)] = area_type

        all_p_codes = {row[h] for row in rows for h in p_code_headers if row.get(h)}
        areas_cache = {a.p_code: a for a in Area.objects.filter(p_code__in=all_p_codes)}

        for row in rows:
            parent_area = None
            for level, name_header in enumerate(name_headers):
                p_code_header = p_code_headers[level]
                area_name = row.get(name_header)
                p_code = row.get(p_code_header)

                if not area_name or not p_code:
                    continue

                area_type = area_types_cache.get((name_header, level))
                if not area_type:
                    continue

                area = areas_cache.get(p_code)
                defaults = {
                    "name": area_name,
                    "area_type": area_type,
                    "parent": parent_area,
                }

                if area:
                    changed = False
                    for key, value in defaults.items():
                        if getattr(area, key) != value:
                            setattr(area, key, value)
                            changed = True
                    if changed:
                        area.save()
                else:
                    area = Area.objects.create(p_code=p_code, **defaults)
                    areas_cache[p_code] = area
                parent_area = area
