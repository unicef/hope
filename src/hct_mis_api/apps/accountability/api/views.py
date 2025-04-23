import logging

from django.db.models import QuerySet
from django_filters import rest_framework as filters
from rest_framework import mixins
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import get_object_or_404

from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.accountability.api.serializers import (
    FeedbackCreateSerializer,
    FeedbackDetailSerializer,
    FeedbackListSerializer,
    FeedbackUpdateSerializer,
)
from hct_mis_api.apps.accountability.filters import FeedbackFilter
from hct_mis_api.apps.accountability.models import Feedback
from hct_mis_api.apps.core.api.mixins import (
    BaseViewSet,
    CountActionMixin,
    ProgramMixin,
    SerializerActionMixin,
)

logger = logging.getLogger(__name__)


class FeedbackMixin:
    serializer_class = FeedbackListSerializer
    filter_backends = (
        filters.DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    )
    filterset_class = FeedbackFilter
    search_fields = (
        "unicef_id",
        "id",
    )


class FeedbackViewSet(
    CountActionMixin,
    ProgramMixin,
    SerializerActionMixin,
    FeedbackMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    BaseViewSet,
):
    queryset = Feedback.objects.all()
    PERMISSIONS = [Permissions.PAYMENT_VERIFICATION_VIEW_LIST]
    http_method_names = ["get", "post", "patch"]
    serializer_classes_by_action = {
        "list": FeedbackListSerializer,
        "retrieve": FeedbackDetailSerializer,
        "create": FeedbackCreateSerializer,
        "partial_update": FeedbackUpdateSerializer,
    }
    permissions_by_action = {
        "list": [Permissions.GRIEVANCES_FEEDBACK_VIEW_LIST, Permissions.GRIEVANCES_FEEDBACK_VIEW_DETAILS],
        "retrieve": [Permissions.GRIEVANCES_FEEDBACK_VIEW_LIST, Permissions.GRIEVANCES_FEEDBACK_VIEW_DETAILS],
        "create": [Permissions.GRIEVANCES_FEEDBACK_VIEW_CREATE],
        "partial_update": [Permissions.GRIEVANCES_FEEDBACK_VIEW_UPDATE],
    }

    def get_object(self) -> Feedback:
        return get_object_or_404(Feedback, id=self.kwargs.get("pk"))

    def get_queryset(self) -> QuerySet["Feedback"]:
        print("==>> ", self.kwargs)
        # TODO: add new ViewSet
        # or add filter based on if program_slug is in kwargs
        return Feedback.objects.all()
