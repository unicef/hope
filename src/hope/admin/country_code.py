import logging
from typing import TYPE_CHECKING, Any

from django.contrib import admin
from django.http import HttpRequest

from hope.admin.utils import HOPEModelAdminBase
from hope.apps.core.models import CountryCodeMap

if TYPE_CHECKING:
    from django.db.models.query import QuerySet


logger = logging.getLogger(__name__)


@admin.register(CountryCodeMap)
class CountryCodeMapAdmin(HOPEModelAdminBase):
    list_display = ("country", "alpha2", "alpha3", "ca_code")
    search_fields = ("country", "alpha2", "alpha3", "ca_code")
    raw_id_fields = ("country",)

    def alpha2(self, obj: Any) -> str:
        return obj.country.iso_code2

    def alpha3(self, obj: Any) -> str:
        return obj.country.iso_code3

    def get_queryset(self, request: HttpRequest) -> "QuerySet":
        return (
            super()
            .get_queryset(request)
            .select_related(
                "country",
            )
        )
