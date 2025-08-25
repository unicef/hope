from django_filters import rest_framework as filters

from hope.apps.core.api.filters import UpdatedAtFilter
from hope.models.geo import Area


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
