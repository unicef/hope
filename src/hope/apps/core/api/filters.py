from django_filters import DateFromToRangeFilter
from django_filters.rest_framework import FilterSet

from hope.models.business_area import BusinessArea


class UpdatedAtFilter(FilterSet):
    updated_at = DateFromToRangeFilter()


class BusinessAreaFilter(UpdatedAtFilter):
    class Meta:
        model = BusinessArea
        fields = ("active",)
