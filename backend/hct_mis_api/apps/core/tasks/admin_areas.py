import logging

from django.conf import settings
from django.contrib.gis.geos.collections import MultiPolygon, Point, Polygon
from django.core.mail import send_mail

from hct_mis_api.apps.core.celery import app
from hct_mis_api.apps.core.datamart.api import DatamartAPI
from hct_mis_api.apps.core.models import AdminArea, AdminAreaLevel

logger = logging.getLogger(__name__)


def handle_geom(geometry):
    if geometry["type"] == "Polygon":
        poly = geometry
    elif geometry["type"] == "MultiPolygon":
        poly = MultiPolygon([Polygon(polygon) for polygon in geometry["coordinates"][0]])
    return poly


@app.task
def load_admin_area(country, geom, page_size, max_records, notify_to=None):
    results = {"created": 0, "updated": 0, "errors": []}
    api = DatamartAPI()
    for loc in api.get_locations(gis=geom, page_size=page_size, max_records=max_records, country=country):
        try:
            admin_area_level = AdminAreaLevel.objects.get(datamart_id=loc["gateway"])
            if loc["parent"]:
                parent, __ = AdminArea.objects.get_or_create(external_id=loc["parent"])
            else:
                parent = None
            values = {
                "title": loc["name"],
                "p_code": loc["p_code"],
                "admin_area_level": admin_area_level,
                "parent": parent,
            }
            if geom:
                values["geom"] = handle_geom(loc["geom"])
                values["point"] = Point(*loc["point"]["coordinates"])

            __, created = AdminArea.objects.update_or_create(external_id=loc["id"], defaults=values)
            if created:
                results["created"] += 1
            else:
                results["updated"] += 1
        except Exception as e:
            logger.exception(e)
            results["updated"].append((loc, f"{e.__class__.__name__}: {str(e)}"))
    if app.current_worker_task and notify_to:
        send_mail(
            "Admin Area Successfully Loaded",
            f"""
All locations for {country} have been successfully loaded in HOPE

Created: {results['created']}
Updated: {results['updated']}
Errors: {results['errors'].length}


""",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=notify_to,
        )
    return results
