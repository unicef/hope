from typing import TYPE_CHECKING

from django.db.models import Q

from django_filters import CharFilter, FilterSet

from hct_mis_api.apps.activity_log.models import LogEntry
from hct_mis_api.apps.core.utils import decode_id_string_required

if TYPE_CHECKING:
    from django.db.models.query import QuerySet


class LogEntryFilter(FilterSet):
    business_area = CharFilter(field_name="business_area__slug", required=True)
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
        for value in values:
            if value.lower() == "system":
                q_obj |= Q(user__isnull=True)
            q_obj |= Q(content_type__model__startswith=value)
            q_obj |= Q(object_id__startswith=value)
            q_obj |= Q(action__startswith=value)
            q_obj |= Q(object_repr__startswith=value)
            q_obj |= Q(timestamp__startswith=value)
        return qs.filter(q_obj)

    def filter_by_user_id(self, qs: "QuerySet", name: str, value: str) -> "QuerySet[LogEntry]":
        return qs.filter(user_id=decode_id_string_required(value))

    def filter_by_program_id(self, qs: "QuerySet", name: str, value: str) -> "QuerySet[LogEntry]":
        return qs.filter(programs__id=decode_id_string_required(value))
