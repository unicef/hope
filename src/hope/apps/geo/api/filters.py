from django_filters import rest_framework as filters

from hope.apps.core.api.filters import UpdatedAtFilter
from hope.models import Area


class AreaFilter(UpdatedAtFilter):
    level = filters.NumberFilter(
        field_name="area_type__area_level",
    )
    name = filters.CharFilter(
        field_name="name",
        lookup_expr="startswith",
    )
    parent_p_code = filters.CharFilter(field_name="parent__p_code")

    class Meta:
        model = Area
        fields = (
            "id",
            "level",
            "name",
            "parent_id",
            "parent_p_code",
        )
