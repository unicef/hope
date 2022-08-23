from django.db import models
from django_filters import FilterSet


class ElasticSearchFilterSet(FilterSet):
    USE_ALL_FIELDS_AS_ELASTIC_SEARCH = True
    USE_SPECIFIC_FIELDS_AS_ELASTIC_SEARCH = tuple()

    def elasticsearch_filter_queryset(self):
        raise NotImplemented

    def prepare_filters(self, allowed_fields):
        raise NotImplemented

    def filter_queryset(self, queryset):
        if self.USE_ALL_FIELDS_AS_ELASTIC_SEARCH or self.USE_SPECIFIC_FIELDS_AS_ELASTIC_SEARCH:
            grievance_ids = self.elasticsearch_filter_queryset()
            queryset = queryset.filter(id__in=grievance_ids)

        if self.USE_ALL_FIELDS_AS_ELASTIC_SEARCH:
            return queryset

        for name, value in self.form.cleaned_data.items():
            if name in self.USE_SPECIFIC_FIELDS_AS_ELASTIC_SEARCH:
                continue
            queryset = self.filters[name].filter(queryset, value)
            assert isinstance(
                queryset, models.QuerySet
            ), "Expected '%s.%s' to return a QuerySet, but got a %s instead." % (
                type(self).__name__,
                name,
                type(queryset).__name__,
            )
        return queryset
