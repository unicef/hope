from typing import Any, Dict

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType

from power_query.defaults import create_defaults
from power_query.models import Formatter, Parametrizer

from hct_mis_api.apps.account.models import Partner, User
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.household.models import Household

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


def hope_create_defaults() -> None:
    if get_user_model().objects.filter(is_superuser=True).exists():
        create_defaults()
        fmt_html = Formatter.objects.get(name="Dataset To HTML")
        for code, params in SYSTEM_PARAMETRIZER.items():
            Parametrizer.objects.update_or_create(
                name=params["name"], code=code, defaults={"system": True, "value": params["value"]()}
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
                "formatter": fmt_html,
                "document_title": "Household by BusinessArea: %(business_area)s",
            },
        )
