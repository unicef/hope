import logging

from django.db.transaction import atomic

from django_countries import countries

from hct_mis_api.apps.geo.missing_countries import missing_countries
from hct_mis_api.apps.geo.models import Area, AreaType, Country

logger = logging.getLogger(__name__)


@atomic()
def initialise_area_types():
    from hct_mis_api.apps.core.models import AdminAreaLevel

    results = {"errors": []}
    for level in AdminAreaLevel.objects.filter(admin_level__gt=0).order_by("admin_level"):
        try:
            country = Country.objects.get(short_name=level.country_name)
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
                p_code=old_area.p_code,
                name=old_area.title,
                defaults={
                    "original_id": old_area.id,
                    "area_type": area_type,
                    "parent": Area.objects.filter(p_code=old_area.parent.p_code).first(),
                },
            )
        except AreaType.DoesNotExist as e:
            logger.exception(e)
        except Exception as e:
            logger.exception(e)
            results["errors"].append(e)
    return results


def initialise_countries():
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


def copy_admin_area_data():
    areas = {}
    from django.db import models
    from hct_mis_api.apps.grievance.models import GrievanceTicket
    from hct_mis_api.apps.household.models import Household
    from hct_mis_api.apps.program.models import Program
    from hct_mis_api.apps.reporting.models import DashboardReport
    from hct_mis_api.apps.reporting.models import Report

    models_to_update = (
        GrievanceTicket,
        Household,
        Program,
        DashboardReport,
        Report,
    )
    for Model in models_to_update:
        try:
            for field in Model._meta.get_fields():
                if type(field) == models.ForeignKey:
                    opts = field.related_model._meta
                    if opts.app_label == "geo" and opts.model_name == "area":
                        old_field_name = field.name[:-4]
                        geo_name = field.name
                        records = Model.objects.all()
                        for record in records:
                            source = getattr(record, old_field_name)
                            if source:
                                p_code = source.p_code
                                if p_code not in areas.keys():
                                    areas[p_code] = Area.objects.get(p_code=p_code)
                                setattr(record, geo_name, areas[p_code])
                        Model.objects.bulk_update(records, [geo_name])
        except Exception as e:
            raise


def copy_country_data():
    from django.db import models
    from hct_mis_api.apps.sanction_list.models import SanctionListIndividual
    from hct_mis_api.apps.sanction_list.models import SanctionListIndividualDocument
    from hct_mis_api.apps.sanction_list.models import SanctionListIndividualNationalities
    from hct_mis_api.apps.sanction_list.models import SanctionListIndividualCountries
    from hct_mis_api.apps.household.models import Agency
    from hct_mis_api.apps.household.models import DocumentType
    from hct_mis_api.apps.household.models import Household
    from hct_mis_api.apps.core.models import CountryCodeMap

    models_to_update = (
        CountryCodeMap,
        Household,
        DocumentType,
        Agency,
        SanctionListIndividualCountries,
        SanctionListIndividualNationalities,
        SanctionListIndividualDocument,
        SanctionListIndividual,
    )
    countries = {}
    for Model in models_to_update:
        try:
            for field in Model._meta.get_fields():
                if type(field) == models.ForeignKey:
                    opts = field.related_model._meta
                    if opts.app_label == "geo" and opts.model_name == "country":
                        old_field_name = field.name[:-4]
                        geo_name = field.name
                        records = Model.objects.all()
                        for record in records:
                            source = getattr(record, old_field_name).code
                            if source:
                                if source not in countries:
                                    countries[source] = Country.objects.get(iso_code2=source)
                                setattr(record, geo_name, countries[source])
                        Model.objects.bulk_update(records, [geo_name])
        except Exception as e:
            raise
