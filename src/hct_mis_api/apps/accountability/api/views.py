import logging

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


# per program
class PaymentVerificationViewSet(
    CountActionMixin,
    ProgramMixin,
    SerializerActionMixin,
    FeedbackMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    BaseViewSet,
):
    queryset = Feedback.objects.all()
    PERMISSIONS = [Permissions.PAYMENT_VERIFICATION_VIEW_LIST]
    # remove PUT
    serializer_classes_by_action = {
        "list": FeedbackListSerializer,
        "retrieve": FeedbackDetailSerializer,
        "create": FeedbackCreateSerializer,
        "partial_update": FeedbackUpdateSerializer,
    }
    permissions_by_action = {
        "list": [Permissions.PAYMENT_VERIFICATION_VIEW_LIST],
        "retrieve": [Permissions.PAYMENT_VERIFICATION_VIEW_DETAILS],
        "create": [Permissions.PAYMENT_VERIFICATION_CREATE],
        "partial_update": [Permissions.PAYMENT_VERIFICATION_UPDATE],
    }

    def get_object(self) -> Feedback:
        return get_object_or_404(Feedback, id=self.kwargs.get("pk"))

    # def get_queryset(self) -> QuerySet[Feedback]:
    #     # or add filter based on if program_slug is in kwargs
    #     return Feedback.objects.all()


# all programs
# TODO: add new ViewSet
