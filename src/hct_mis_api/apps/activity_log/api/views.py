import logging

from django.db.models import QuerySet

from django_filters import rest_framework as filters
from drf_spectacular.utils import extend_schema
from rest_framework import mixins
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.request import Request
from rest_framework.response import Response

from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.activity_log.api.serializers import LogEntrySerializer
from hct_mis_api.apps.activity_log.filters import LogEntryFilter
from hct_mis_api.apps.activity_log.models import LogEntry
from hct_mis_api.apps.core.api.mixins import (
    BaseViewSet,
    CountActionMixin,
    SerializerActionMixin,
)
from hct_mis_api.apps.core.api.serializers import ChoiceSerializer
from hct_mis_api.apps.core.utils import to_choice_object

logger = logging.getLogger(__name__)


class LogEntryViewSet(
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
    serializer_classes_by_action = {
        "list": LogEntrySerializer,
    }

    def get_queryset(self) -> QuerySet[LogEntry]:
        qs = LogEntry.objects.filter(business_area__slug=self.kwargs.get("business_area_slug"))
        if program_slug := self.kwargs.get("program_slug"):
            qs = qs.filter(programs__slug=program_slug)
        return qs

    @action(detail=False, methods=["get"], url_path="action-choices")
    @extend_schema(responses={200: ChoiceSerializer(many=True)})
    def log_entry_action_choices(self, request: Request) -> Response:
        return Response(to_choice_object(LogEntry.LOG_ENTRY_ACTION_CHOICES))
