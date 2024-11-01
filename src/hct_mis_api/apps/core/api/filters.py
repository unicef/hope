from django_filters import DateFromToRangeFilter
from django_filters.rest_framework import FilterSet


class UpdatedAtFilter(FilterSet):
    updated_at = DateFromToRangeFilter()
