from typing import Any, Dict

from django.contrib.contenttypes.models import ContentType

from hct_mis_api.apps.account.models import Partner, User
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.household.models import Household
from power_query.defaults import create_defaults as base_create_defaults
from power_query.models import Formatter, Parametrizer

SYSTEM_PARAMETRIZER: Dict[str, Dict[str, Any]] = {
    "active-business-areas": {
        "name": "Active Business Areas",
        "value": lambda: {
            "business_area": list(BusinessArea.objects.filter(active=True).values_list("slug", flat=True))
        },
    },
    "all-partners": {
        "name": "All Partners",
        "value": lambda: {"partner": list(Partner.objects.values_list("name", flat=True))},
    },
}


def create_defaults() -> None:
    base_create_defaults()
    for code, params in SYSTEM_PARAMETRIZER.items():
        Parametrizer.objects.update_or_create(
            name=params["name"],
            code=code,
            defaults={"system": True, "value": params["value"]()},
        )
    from power_query.models import Query, Report

    q, __ = Query.objects.update_or_create(
        name="Households by BusinessArea",
        defaults=dict(
            target=ContentType.objects.get_for_model(Household),
            code="""ba=BusinessAreaManager.get(slug=args['business_area'])
result=conn.filter(business_area=ba)
extra={"ba": ba}
""",
            parametrizer=Parametrizer.objects.get(code="active-business-areas"),
            owner=User.objects.filter(is_superuser=True).first(),
        ),
    )

    Report.objects.update_or_create(
        name="Household by BusinessArea",
        defaults={
            "query": q,
            "formatter": Formatter.objects.get(name="Dataset To HTML"),
            "document_title": "Household by BusinessArea: %(business_area)s",
        },
    )
