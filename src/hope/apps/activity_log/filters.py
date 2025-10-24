from typing import TYPE_CHECKING

from django.db.models import Q
from django_filters import CharFilter, FilterSet

from hope.apps.activity_log.models import LogEntry

if TYPE_CHECKING:
    from django.db.models.query import QuerySet


class LogEntryFilter(FilterSet):
    business_area = CharFilter(field_name="business_area__slug")
    search = CharFilter(method="search_filter")
    module = CharFilter(field_name="content_type__model")
    user_id = CharFilter(method="filter_by_user_id")
    program_id = CharFilter(method="filter_by_program_id")

    class Meta:
        model = LogEntry
        fields = ("object_id", "user")

    def search_filter(self, qs: "QuerySet", name: str, value: str) -> "QuerySet[LogEntry]":
        values = value.split(" ")
        q_obj = Q()
        for element in values:
            if element.lower() == "system":
                q_obj |= Q(user__isnull=True)
            q_obj |= Q(content_type__model__startswith=element)
            q_obj |= Q(object_id__startswith=element)
            q_obj |= Q(action__startswith=element)
            q_obj |= Q(object_repr__startswith=element)
            q_obj |= Q(timestamp__startswith=element)
        return qs.filter(q_obj)

    def filter_by_user_id(self, qs: "QuerySet", name: str, value: str) -> "QuerySet[LogEntry]":
        return qs.filter(user_id=value)

    def filter_by_program_id(self, qs: "QuerySet", name: str, value: str) -> "QuerySet[LogEntry]":
        return qs.filter(programs__id=value)
