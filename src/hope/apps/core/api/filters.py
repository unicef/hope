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
    - IND-XXX: Individual
    - PP-XXX: Payment Plan
    - RCPT-XXX: Payment (Receipt)
    - GRV-XXX: Grievance Ticket
    """

    office_search = CharFilter(method="filter_office_search")

    def filter_office_search(self, queryset: QuerySet, name: str, value: str) -> QuerySet:
        if not value:
            return queryset

        value = value.strip()

        prefix_map = {
            "HH-": self.filter_by_household_for_office_search,
            "IND-": self.filter_by_individual_for_office_search,
            "PP-": self.filter_by_payment_plan_for_office_search,
            "RCPT-": self.filter_by_payment_for_office_search,
            "GRV-": self.filter_by_grievance_for_office_search,
        }

        for prefix, handler in prefix_map.items():
            if value.startswith(prefix):
                return handler(queryset, value)

        return queryset.none()
