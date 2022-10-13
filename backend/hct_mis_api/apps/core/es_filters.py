from django.conf import settings

from django_filters import FilterSet


class ElasticSearchFilterSet(FilterSet):
    USE_ALL_FIELDS_AS_POSTGRES_DB = settings.GRIEVANCE_POSTGRES_ENABLED
    USE_SPECIFIC_FIELDS_AS_ELASTIC_SEARCH = tuple()

    def elasticsearch_filter_queryset(self):
        raise NotImplemented

    def prepare_filters(self, allowed_fields):
        raise NotImplemented

    def filter_queryset(self, queryset):
        if not self.USE_ALL_FIELDS_AS_POSTGRES_DB and self.USE_SPECIFIC_FIELDS_AS_ELASTIC_SEARCH:
            grievance_ids = self.elasticsearch_filter_queryset()
            queryset = queryset.filter(id__in=grievance_ids)

            for name, value in self.form.cleaned_data.items():
                if name in self.USE_SPECIFIC_FIELDS_AS_ELASTIC_SEARCH:
                    continue
                queryset = self.filters[name].filter(queryset, value)
            return queryset
        else:
            return super().filter_queryset(queryset)
