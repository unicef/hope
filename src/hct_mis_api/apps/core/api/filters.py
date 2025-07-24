from django_filters import DateFromToRangeFilter
from django_filters.rest_framework import FilterSet

from hct_mis_api.apps.core.models import BusinessArea


class UpdatedAtFilter(FilterSet):
    updated_at = DateFromToRangeFilter()


class BusinessAreaFilter(UpdatedAtFilter):
    class Meta:
        model = BusinessArea
        fields = ("active",)
