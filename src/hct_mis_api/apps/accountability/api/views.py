import logging
from typing import Any

from django.db.models import QuerySet

from django_filters import rest_framework as filters
from drf_spectacular.utils import extend_schema
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import get_object_or_404
from rest_framework.request import Request
from rest_framework.response import Response

from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.accountability.api.serializers import (
    FeedbackCreateSerializer,
    FeedbackDetailSerializer,
    FeedbackListSerializer,
    FeedbackMessageCreateSerializer,
    FeedbackMessageSerializer,
    FeedbackUpdateSerializer,
)
from hct_mis_api.apps.accountability.filters import FeedbackFilter
from hct_mis_api.apps.accountability.models import Feedback, FeedbackMessage
from hct_mis_api.apps.accountability.services.feedback_crud_services import (
    FeedbackCrudServices,
)
from hct_mis_api.apps.activity_log.models import log_create
from hct_mis_api.apps.core.api.mixins import (
    BaseViewSet,
    CountActionMixin,
    ProgramMixin,
    SerializerActionMixin,
)
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.program.models import Program

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
    PERMISSIONS = [Permissions.GRIEVANCES_FEEDBACK_VIEW_LIST, Permissions.GRIEVANCES_FEEDBACK_VIEW_DETAILS]
    http_method_names = ["get", "post", "patch"]
    serializer_classes_by_action = {
        "list": FeedbackListSerializer,
        "retrieve": FeedbackDetailSerializer,
        "create": FeedbackCreateSerializer,
        "partial_update": FeedbackUpdateSerializer,
        "message": FeedbackMessageCreateSerializer,
    }
    permissions_by_action = {
        "list": [Permissions.GRIEVANCES_FEEDBACK_VIEW_LIST, Permissions.GRIEVANCES_FEEDBACK_VIEW_DETAILS],
        "retrieve": [Permissions.GRIEVANCES_FEEDBACK_VIEW_LIST, Permissions.GRIEVANCES_FEEDBACK_VIEW_DETAILS],
        "create": [Permissions.GRIEVANCES_FEEDBACK_VIEW_CREATE],
        "partial_update": [Permissions.GRIEVANCES_FEEDBACK_VIEW_UPDATE],
        "message": [Permissions.GRIEVANCES_FEEDBACK_MESSAGE_VIEW_CREATE],
    }

    def get_object(self) -> Feedback:
        return get_object_or_404(Feedback, id=self.kwargs.get("pk"))

    def get_queryset(self) -> QuerySet[Feedback]:
        qs = Feedback.objects.filter(business_area__slug=self.kwargs.get("business_area_slug"))
        if program_slug := self.kwargs.get("program_slug"):
            qs = qs.filter(program__slug=program_slug)
        return qs

    @extend_schema(
        responses={
            201: FeedbackDetailSerializer,
        },
    )
    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        business_area = BusinessArea.objects.get(slug=self.kwargs.get("business_area_slug"))
        program_slug = self.kwargs.get("program_slug")
        program = None
        if program_slug:
            program = Program.objects.get(slug=program_slug)

        if program and program.status == Program.FINISHED:
            raise ValidationError("In order to proceed this action, program status must not be finished")

        input_data = serializer.validated_data
        input_data["business_area"] = business_area
        input_data["program"] = program
        feedback = FeedbackCrudServices.create(request.user, business_area, input_data)
        log_create(
            Feedback.ACTIVITY_LOG_MAPPING,
            "business_area",
            request.user,
            getattr(feedback.program, "pk", None),
            None,
            feedback,
        )
        headers = self.get_success_headers(serializer.data)

        return Response(FeedbackDetailSerializer(feedback).data, status=status.HTTP_201_CREATED, headers=headers)

    @extend_schema(
        responses={
            200: FeedbackDetailSerializer,
        },
    )
    def update(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        feedback = self.get_object()
        old_feedback = self.get_object()
        serializer = self.get_serializer(feedback, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        program_slug = self.kwargs.get("program_slug")
        program = None
        if program_slug:
            program = Program.objects.get(slug=program_slug)

        if program and program.status == Program.FINISHED:
            raise ValidationError("In order to proceed this action, program status must not be finished")

        input_data = serializer.validated_data
        updated_feedback = FeedbackCrudServices.update(feedback, input_data)
        log_create(
            Feedback.ACTIVITY_LOG_MAPPING,
            "business_area",
            request.user,
            getattr(feedback.program, "pk", None),
            old_feedback,
            updated_feedback,
        )
        return Response(FeedbackDetailSerializer(feedback).data, status=status.HTTP_200_OK)

    @extend_schema(
        request=FeedbackMessageCreateSerializer,
        responses={
            201: FeedbackMessageSerializer,
        },
    )
    @action(detail=True, methods=["post"])
    def message(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        feedback = self.get_object()

        feedback_message = FeedbackMessage.objects.create(
            feedback=feedback, description=serializer.validated_data["description"], created_by=request.user
        )
        return Response(FeedbackMessageSerializer(feedback_message).data, status=status.HTTP_201_CREATED)
