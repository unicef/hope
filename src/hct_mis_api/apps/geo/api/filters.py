from django_filters import rest_framework as filters

from hct_mis_api.apps.core.api.filters import UpdatedAtFilter
from hct_mis_api.apps.geo.models import Area


class AreaFilter(UpdatedAtFilter):
    level = filters.NumberFilter(
        field_name="area_type__area_level",
    )
    name = filters.CharFilter(
        field_name="name",
        lookup_expr="startswith",
    )
    updated_at = filters.DateTimeFilter()

    class Meta:
        model = Area
        fields = ("level", "name")
