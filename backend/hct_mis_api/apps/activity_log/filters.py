from django.db.models import Q

from django_filters import CharFilter, FilterSet

from hct_mis_api.apps.activity_log.models import LogEntry


class LogEntryFilter(FilterSet):
    business_area = CharFilter(field_name="business_area__slug", required=True)
    search = CharFilter(method="search_filter")
    module = CharFilter(field_name="content_type__model")

    class Meta:
        model = LogEntry
        fields = ("object_id",)

    def search_filter(self, qs, name, value):
        values = value.split(" ")
        q_obj = Q()
        for value in values:
            if value.lower() == "system":
                q_obj |= Q(user__isnull=True)
            q_obj |= Q(content_type__model__startswith=value)
            q_obj |= Q(object_id__startswith=value)
            q_obj |= Q(action__startswith=value)
            q_obj |= Q(object_repr__startswith=value)
            q_obj |= Q(user__first_name__startswith=value)
            q_obj |= Q(user__last_name__startswith=value)
            q_obj |= Q(user__email__startswith=value)
            q_obj |= Q(timestamp__startswith=value)
        return qs.filter(q_obj)
