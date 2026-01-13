from django.db.models import QuerySet
from django_filters import CharFilter, DateFromToRangeFilter, FilterSet

from hope.models import BusinessArea


class UpdatedAtFilter(FilterSet):
    updated_at = DateFromToRangeFilter()


class BusinessAreaFilter(UpdatedAtFilter):
    class Meta:
        model = BusinessArea
        fields = ("active",)


class OfficeSearchFilterMixin(FilterSet):
    """Mixin for FilterSets that support office_search parameter.

    Filters querysets based on UNICEF ID prefixes:
    - HH-XXX: Household
    - IND-XXX: Individual (also supports phone number and name search)
    - PP-XXX: Payment Plan
    - RCPT-XXX: Payment (Receipt)
    - GRV-XXX: Grievance Ticket

    When searching without a prefix, defaults to individual search by phone number or name.
    """

    office_search = CharFilter(method="filter_office_search")

    def filter_office_search(self, queryset: QuerySet, name: str, value: str) -> QuerySet:
        if not value:
            return queryset.none()

        value = value.strip()

        if value.startswith("HH-"):
            return self.filter_by_household_for_office_search(queryset, value)
        if value.startswith("IND-"):
            return self.filter_by_individual_for_office_search(queryset, value)
        if value.startswith("PP-"):
            return self.filter_by_payment_plan_for_office_search(queryset, value)
        if value.startswith("RCPT-"):
            return self.filter_by_payment_for_office_search(queryset, value)
        if value.startswith("GRV-"):
            return self.filter_by_grievance_for_office_search(queryset, value)

        # No prefix - treat as individual search (phone number or name)
        return self.filter_by_individual_for_office_search(queryset, value)
