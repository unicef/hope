from django_filters import FilterSet

from hct_mis_api.apps.targeting.models import TargetPopulation


class TargetPopulationFilter(FilterSet):
    class Meta:
        model = TargetPopulation
        fields = {
            "status": ("exact",),
            "name": ("startswith",),
        }
