import logging
from functools import partial
from typing import Any

from django.db import transaction
from django.db.models import QuerySet
from django_filters import rest_framework as filters
from drf_spectacular.utils import extend_schema
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import get_object_or_404
from rest_framework.request import Request
from rest_framework.response import Response

from hope.apps.account.permissions import Permissions, check_permissions
from hope.apps.accountability.api.serializers import (
    FeedbackCreateSerializer,
    FeedbackDetailSerializer,
    FeedbackListSerializer,
    FeedbackMessageCreateSerializer,
    FeedbackMessageSerializer,
    FeedbackUpdateSerializer,
    MessageCreateSerializer,
    MessageDetailSerializer,
    MessageListSerializer,
    MessageSampleSizeSerializer,
    SampleSizeSerializer,
    SurveyCategoryChoiceSerializer,
    SurveyRapidProFlowSerializer,
    SurveySampleSizeSerializer,
    SurveySerializer,
)
from hope.apps.accountability.celery_tasks import (
    export_survey_sample_task,
    send_survey_to_users,
)
from hope.apps.accountability.filters import (
    FeedbackFilter,
    MessagesFilter,
    SurveyFilter,
)
from hope.apps.accountability.models import Feedback, FeedbackMessage, Message, Survey
from hope.apps.accountability.services.feedback_crud_services import (
    FeedbackCrudServices,
)
from hope.apps.accountability.services.message_crud_services import MessageCrudServices
from hope.apps.accountability.services.sampling import Sampling
from hope.apps.accountability.services.survey_crud_services import SurveyCrudServices
from hope.apps.accountability.services.verifiers import MessageArgumentVerifier
from hope.apps.activity_log.models import log_create
from hope.apps.core.api.mixins import (
    BaseViewSet,
    BusinessAreaProgramsAccessMixin,
    CountActionMixin,
    ProgramMixin,
    SerializerActionMixin,
)
from hope.apps.core.models import BusinessArea
from hope.apps.core.services.rapid_pro.api import RapidProAPI, TokenNotProvided
from hope.apps.core.utils import to_choice_object
from hope.apps.household.models import Household
from hope.apps.program.models import Program

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
    BusinessAreaProgramsAccessMixin,
    CountActionMixin,
    SerializerActionMixin,
    FeedbackMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    BaseViewSet,
):
    PERMISSIONS = [
        Permissions.GRIEVANCES_FEEDBACK_VIEW_LIST,
        Permissions.GRIEVANCES_FEEDBACK_VIEW_DETAILS,
    ]
    queryset = Feedback.objects.all()
    http_method_names = ["get", "post", "patch"]
    serializer_classes_by_action = {
        "list": FeedbackListSerializer,
        "retrieve": FeedbackDetailSerializer,
        "create": FeedbackCreateSerializer,
        "partial_update": FeedbackUpdateSerializer,
        "message": FeedbackMessageCreateSerializer,
    }
    permissions_by_action = {
        "list": [
            Permissions.GRIEVANCES_FEEDBACK_VIEW_LIST,
            Permissions.GRIEVANCES_FEEDBACK_VIEW_DETAILS,
        ],
        "retrieve": [
            Permissions.GRIEVANCES_FEEDBACK_VIEW_LIST,
            Permissions.GRIEVANCES_FEEDBACK_VIEW_DETAILS,
        ],
        "create": [Permissions.GRIEVANCES_FEEDBACK_VIEW_CREATE],
        "partial_update": [Permissions.GRIEVANCES_FEEDBACK_VIEW_UPDATE],
        "message": [Permissions.GRIEVANCES_FEEDBACK_MESSAGE_VIEW_CREATE],
    }
    program_model_field = "program"

    def get_object(self) -> Feedback:
        return get_object_or_404(Feedback, id=self.kwargs.get("pk"))

    def get_queryset(self) -> QuerySet[Feedback]:
        queryset = super().get_queryset()
        if program_slug := self.kwargs.get("program_slug"):
            queryset = queryset.filter(program__slug=program_slug)
        return queryset

    @transaction.atomic
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

        if program_id := serializer.validated_data.get("program_id"):
            program = Program.objects.get(id=program_id)

        if program and program.status == Program.FINISHED:
            raise ValidationError("It is not possible to create Feedback for a Finished Program.")

        # additional check for global scope - check if user has permission in the target program
        if (
            not program_slug
            and program
            and not check_permissions(
                self.request.user,
                self.get_permissions_for_action(),
                business_area=business_area,
                program=program.slug,
            )
        ):
            raise PermissionDenied

        input_data = serializer.validated_data
        input_data["business_area"] = business_area
        input_data["program"] = str(program.pk) if program else None
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

        return Response(
            FeedbackDetailSerializer(feedback).data,
            status=status.HTTP_201_CREATED,
            headers=headers,
        )

    @transaction.atomic
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

        business_area = BusinessArea.objects.get(slug=self.kwargs.get("business_area_slug"))
        program = feedback.program

        if program_id := serializer.validated_data.get("program_id"):
            program = Program.objects.get(id=program_id)

        if program and program.status == Program.FINISHED:
            raise ValidationError("It is not possible to update Feedback for a Finished Program.")

        # additional check for global scope - check if user has permission in the target program
        if program and not check_permissions(
            self.request.user,
            self.get_permissions_for_action(),
            business_area=business_area,
            program=program.slug,
        ):
            raise PermissionDenied

        input_data = serializer.validated_data
        input_data["program"] = str(program.pk) if program else None
        updated_feedback = FeedbackCrudServices.update(feedback, input_data)
        log_create(
            Feedback.ACTIVITY_LOG_MAPPING,
            "business_area",
            request.user,
            getattr(feedback.program, "pk", None),
            old_feedback,
            updated_feedback,
        )
        return Response(FeedbackDetailSerializer(updated_feedback).data, status=status.HTTP_200_OK)

    @transaction.atomic
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

        # additional check for global scope - check if user has permission in the target program
        if feedback.program and not check_permissions(
            self.request.user,
            self.get_permissions_for_action(),
            business_area=feedback.business_area,
            program=feedback.program.slug,
        ):
            raise PermissionDenied

        feedback_message = FeedbackMessage.objects.create(
            feedback=feedback,
            description=serializer.validated_data["description"],
            created_by=request.user,
        )
        return Response(
            FeedbackMessageSerializer(feedback_message).data,
            status=status.HTTP_201_CREATED,
        )


class MessageViewSet(
    CountActionMixin,
    SerializerActionMixin,
    ProgramMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    BaseViewSet,
):
    queryset = Message.objects.all()
    filter_backends = (
        filters.DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    )
    filterset_class = MessagesFilter
    search_fields = (
        "unicef_id",
        "id",
    )
    http_method_names = ["get", "post"]
    serializer_classes_by_action = {
        "list": MessageListSerializer,
        "retrieve": MessageDetailSerializer,
        "create": MessageCreateSerializer,
        "sample_size": MessageSampleSizeSerializer,
    }
    permissions_by_action = {
        "list": [Permissions.ACCOUNTABILITY_COMMUNICATION_MESSAGE_VIEW_LIST],
        "retrieve": [Permissions.ACCOUNTABILITY_COMMUNICATION_MESSAGE_VIEW_DETAILS],
        "create": [Permissions.ACCOUNTABILITY_COMMUNICATION_MESSAGE_VIEW_CREATE],
        "sample_size": [Permissions.ACCOUNTABILITY_COMMUNICATION_MESSAGE_VIEW_CREATE],
    }

    @transaction.atomic
    @extend_schema(
        responses={
            201: MessageDetailSerializer,
        },
    )
    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        business_area = BusinessArea.objects.get(slug=self.kwargs.get("business_area_slug"))
        program = Program.objects.get(slug=self.program_slug)

        input_data = serializer.validated_data
        input_data["program"] = str(program.pk)

        message = MessageCrudServices.create(request.user, business_area, input_data)

        log_create(
            Message.ACTIVITY_LOG_MAPPING,
            "business_area",
            request.user,
            str(self.program.id),
            None,
            message,
        )
        serializer = MessageDetailSerializer(instance=message)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @transaction.atomic
    @extend_schema(responses=SampleSizeSerializer)
    @action(detail=False, methods=["post"], url_path="sample-size")
    def sample_size(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        input_data = serializer.validated_data
        verifier = MessageArgumentVerifier(input_data)
        verifier.verify()

        households = MessageCrudServices._get_households(input_data)
        sampling = Sampling(input_data, households)
        number_of_recipients, sample_size = sampling.generate_sampling()
        return Response(
            SampleSizeSerializer(
                {
                    "number_of_recipients": number_of_recipients,
                    "sample_size": sample_size,
                }
            ).data,
            status=status.HTTP_202_ACCEPTED,
        )


class SurveyViewSet(
    ProgramMixin,
    CountActionMixin,
    SerializerActionMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    BaseViewSet,
):
    PERMISSIONS = [
        Permissions.ACCOUNTABILITY_SURVEY_VIEW_LIST,
        Permissions.ACCOUNTABILITY_SURVEY_VIEW_DETAILS,
    ]
    http_method_names = ["get", "post"]
    serializer_classes_by_action = {
        "list": SurveySerializer,
        "retrieve": SurveySerializer,
        "create": SurveySerializer,
        "export_sample": SurveySerializer,
        "sample_size": SurveySampleSizeSerializer,
    }
    permissions_by_action = {
        "list": [Permissions.ACCOUNTABILITY_SURVEY_VIEW_LIST],
        "retrieve": [
            Permissions.ACCOUNTABILITY_SURVEY_VIEW_LIST,
            Permissions.ACCOUNTABILITY_SURVEY_VIEW_DETAILS,
        ],
        "create": [Permissions.ACCOUNTABILITY_SURVEY_VIEW_CREATE],
        "export_sample": [Permissions.ACCOUNTABILITY_SURVEY_VIEW_DETAILS],
        "sample_size": [Permissions.ACCOUNTABILITY_SURVEY_VIEW_CREATE],
    }
    queryset = Survey.objects.all()
    serializer_class = SurveySerializer
    filter_backends = (
        filters.DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    )
    filterset_class = SurveyFilter
    search_fields = (
        "title",
        "unicef_id",
        "id",
    )

    @transaction.atomic
    @extend_schema(
        responses={
            201: SurveySerializer,
        },
    )
    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        business_area = BusinessArea.objects.get(slug=self.business_area_slug)
        program = Program.objects.get(slug=self.program_slug)

        input_data = serializer.validated_data
        input_data["business_area"] = business_area
        input_data["program"] = str(program.pk)

        survey = SurveyCrudServices.create(request.user, business_area, input_data)  # type: ignore
        transaction.on_commit(partial(send_survey_to_users.delay, survey.id))
        log_create(
            Survey.ACTIVITY_LOG_MAPPING,
            "business_area",
            request.user,
            program.pk,
            None,
            survey,
        )
        serializer = self.get_serializer(instance=survey)
        headers = self.get_success_headers(serializer.data)

        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @extend_schema(
        request=None,
        responses={202: SurveySerializer},
    )
    @action(detail=True, methods=["get"], url_path="export-sample")
    def export_sample(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        survey = self.get_object()
        export_survey_sample_task.delay(survey.id, request.user.id)
        serializer = self.get_serializer(survey)
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)

    @extend_schema(responses=SurveyCategoryChoiceSerializer(many=True))
    @action(detail=False, methods=["get"], url_path="category-choices")
    def category_choices(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return Response(to_choice_object(Survey.CATEGORY_CHOICES))

    @extend_schema(responses=SurveyRapidProFlowSerializer(many=True))
    @action(detail=False, methods=["get"], url_path="available-flows", pagination_class=None)
    def available_flows(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        try:
            api = RapidProAPI(self.business_area_slug, RapidProAPI.MODE_SURVEY)  # type: ignore
        except TokenNotProvided:
            raise ValidationError("Token is not provided.")
        return Response(api.get_flows())

    @transaction.atomic
    @extend_schema(responses=SampleSizeSerializer)
    @action(detail=False, methods=["post"], url_path="sample-size")
    def sample_size(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        input_data = serializer.validated_data
        if payment_plan := input_data.get("payment_plan"):
            households = Household.objects.filter(payment__parent=payment_plan)
        elif program := self.program:
            households = program.households_with_payments_in_program
        else:
            raise ValidationError("Target population or program should be provided.")

        sampling = Sampling(input_data, households)
        number_of_recipients, sample_size = sampling.generate_sampling()
        return Response(
            SampleSizeSerializer(
                {
                    "number_of_recipients": number_of_recipients,
                    "sample_size": sample_size,
                }
            ).data,
            status=status.HTTP_202_ACCEPTED,
        )
