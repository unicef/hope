from django.db.models import QuerySet

from django_filters import CharFilter, FilterSet

from hct_mis_api.apps.core.filters import IntegerFilter
from hct_mis_api.apps.geo.models import Area


class AreaFilter(FilterSet):
    business_area = CharFilter(method="business_area_filter")
    level = IntegerFilter(
        field_name="area_type__area_level",
    )

    class Meta:
        model = Area
        fields = {
            "name": ["exact", "istartswith"],
        }

    def business_area_filter(self, qs, name, value) -> QuerySet:
        return qs.filter(area_type__country__name__iexact=value)
