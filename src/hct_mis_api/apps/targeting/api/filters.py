from django_filters import rest_framework as filters

from hct_mis_api.apps.core.api.filters import UpdatedAtFilter
from hct_mis_api.apps.targeting.models import TargetPopulation


class TargetPopulationFilter(UpdatedAtFilter):
    name = filters.CharFilter(
        field_name="name",
        lookup_expr="startswith",
    )

    class Meta:
        model = TargetPopulation
        fields = ("status", "name")
