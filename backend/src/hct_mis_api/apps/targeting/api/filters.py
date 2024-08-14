from django_filters import rest_framework as filters

from hct_mis_api.apps.targeting.models import TargetPopulation


class TargetPopulationFilter(filters.FilterSet):
    name = filters.CharFilter(
        field_name="name",
        lookup_expr="startswith",
    )

    class Meta:
        model = TargetPopulation
        fields = ("status", "name")
