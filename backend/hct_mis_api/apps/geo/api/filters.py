from django_filters import rest_framework as filters

from hct_mis_api.apps.geo.models import Area


class AreaFilter(filters.FilterSet):
    level = filters.NumberFilter(
        field_name="area_type__area_level",
    )
    name = filters.CharFilter(
        field_name="name",
        lookup_expr="startswith",
    )

    class Meta:
        model = Area
        fields = ("level", "name")
