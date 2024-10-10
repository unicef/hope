from django_filters import DateFromToRangeFilter
from django_filters.rest_framework import FilterSet

from hct_mis_api.apps.core.models import BusinessArea


class BusinessAreaFilter(FilterSet):
    updated_at = DateFromToRangeFilter()

    class Meta:
        model = BusinessArea
        fields = (
            "active",
            "updated_at",
        )
