import logging

from django.db.models import QuerySet
from django_filters import rest_framework as filters
from rest_framework import mixins
from rest_framework.filters import OrderingFilter

from hope.apps.account.permissions import Permissions
from hope.apps.activity_log.api.serializers import LogEntrySerializer
from hope.apps.activity_log.filters import LogEntryFilter
from hope.apps.core.api.mixins import (
    BaseViewSet,
    BusinessAreaProgramsAccessMixin,
    CountActionMixin,
    SerializerActionMixin,
)
from hope.models import LogEntry

logger = logging.getLogger(__name__)


class LogEntryViewSet(
    BusinessAreaProgramsAccessMixin,
    CountActionMixin,
    SerializerActionMixin,
    mixins.ListModelMixin,
    BaseViewSet,
):
    filter_backends = (
        filters.DjangoFilterBackend,
        OrderingFilter,
    )
    filterset_class = LogEntryFilter
    PERMISSIONS = [Permissions.ACTIVITY_LOG_VIEW]
    queryset = LogEntry.objects.all()
    serializer_classes_by_action = {
        "list": LogEntrySerializer,
    }
    program_model_field = "programs"
    program_model_field_is_many = True

    def get_queryset(self) -> QuerySet[LogEntry]:
        queryset = super().get_queryset()
        if code := self.kwargs.get("program_code"):
            queryset = queryset.filter(programs__code=code)
        return queryset
