import logging

from django.db.transaction import atomic

from hct_mis_api.apps.geo.models import Area, AreaType, Country

logger = logging.getLogger(__name__)


@atomic()
def initialise_area_types():
    from hct_mis_api.apps.core.models import AdminAreaLevel

    results = {"errors": []}
    for level in AdminAreaLevel.objects.filter(admin_level__gt=0).order_by("admin_level"):
        try:
            country = Country.objects.get(name=level.country_name)
            AreaType.objects.update_or_create(
                area_level=level.admin_level,
                country=country,
                defaults={
                    "name": level.name,
                    "original_id": level.id,
                    "parent": AreaType.objects.filter(area_level=level.admin_level - 1, country=country).first(),
                },
            )
        except Country.DoesNotExist as e:
            logger.exception(e)
        except Exception as e:
            logger.exception(e)
            results["errors"].append(e)
    return results


@atomic()
def initialise_areas():
    from hct_mis_api.apps.core.models import AdminArea

    results = {"errors": []}
    for old_area in AdminArea.objects.filter(admin_area_level__admin_level__gt=0).order_by(
        "admin_area_level__admin_level"
    ):
        try:
            area_type = AreaType.objects.get(original_id=old_area.admin_area_level.id)
            Area.objects.update_or_create(
                name=old_area.title,
                area_type=area_type,
                defaults={
                    "p_code": old_area.p_code,
                },
            )
        except Country.DoesNotExist as e:
            logger.exception(e)
        except Exception as e:
            logger.exception(e)
            results["errors"].append(e)
    return results
