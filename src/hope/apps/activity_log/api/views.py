import logging
from typing import Any

from django.db.models import QuerySet
from django_filters import rest_framework as filters
from drf_spectacular.utils import extend_schema
from rest_framework import mixins
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.request import Request
from rest_framework.response import Response

from hope.apps.account.permissions import Permissions
from hope.apps.activity_log.api.serializers import LogEntrySerializer
from hope.apps.activity_log.filters import LogEntryFilter
from models.activity_log import LogEntry
from hope.apps.core.api.mixins import (
    BaseViewSet,
    BusinessAreaProgramsAccessMixin,
    CountActionMixin,
    SerializerActionMixin,
)
from hope.apps.core.api.serializers import ChoiceSerializer
from hope.apps.core.utils import to_choice_object

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
        SearchFilter,
        OrderingFilter,
    )
    filterset_class = LogEntryFilter
    search_fields = ("object_id",)
    PERMISSIONS = [Permissions.ACTIVITY_LOG_VIEW]
    queryset = LogEntry.objects.all()
    serializer_classes_by_action = {
        "list": LogEntrySerializer,
    }
    program_model_field = "programs"

    def get_queryset(self) -> QuerySet[LogEntry]:
        queryset = super().get_queryset()
        if program_slug := self.kwargs.get("program_slug"):
            queryset = queryset.filter(programs__slug=program_slug)
        return queryset

    @extend_schema(responses={200: ChoiceSerializer(many=True)})
    @action(detail=False, methods=["get"], url_path="action-choices")
    def log_entry_action_choices(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return Response(to_choice_object(LogEntry.LOG_ENTRY_ACTION_CHOICES))
