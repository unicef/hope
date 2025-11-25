from django.db.models import QuerySet
from django_filters import CharFilter, DateFromToRangeFilter, FilterSet

from hope.apps.core.models import BusinessArea


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

        if value.startswith("HH-"):
            return self.filter_by_household(queryset, value)
        if value.startswith("IND-"):
            return self.filter_by_individual(queryset, value)
        if value.startswith("PP-"):
            return self.filter_by_payment_plan(queryset, value)
        if value.startswith("RCPT-"):
            return self.filter_by_payment(queryset, value)
        if value.startswith("GRV-"):
            return self.filter_by_grievance(queryset, value)

        return queryset

    def filter_by_household(self, queryset: QuerySet, unicef_id: str) -> QuerySet:
        return queryset

    def filter_by_individual(self, queryset: QuerySet, unicef_id: str) -> QuerySet:
        return queryset

    def filter_by_payment_plan(self, queryset: QuerySet, unicef_id: str) -> QuerySet:
        return queryset

    def filter_by_payment(self, queryset: QuerySet, unicef_id: str) -> QuerySet:
        return queryset

    def filter_by_grievance(self, queryset: QuerySet, unicef_id: str) -> QuerySet:
        return queryset
