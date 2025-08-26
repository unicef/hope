from typing import Any

from constance import config
from django.db.models import Prefetch, Q, QuerySet
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework_extensions.cache.decorators import cache_response

from hope.api.caches import etag_decorator
from hope.apps.account.permissions import Permissions
from hope.apps.core.api.mixins import (
    BaseViewSet,
    BusinessAreaVisibilityMixin,
    CountActionMixin,
    ProgramVisibilityMixin,
    SerializerActionMixin,
)
from hope.apps.core.api.serializers import FieldAttributeSerializer
from hope.models.core import FlexibleAttribute
from hope.apps.household.api.caches import (
    HouseholdListKeyConstructor,
    IndividualListKeyConstructor,
)
from hope.apps.household.api.serializers.household import (
    HouseholdChoicesSerializer,
    HouseholdDetailSerializer,
    HouseholdListSerializer,
    HouseholdMemberSerializer,
    IndividualChoicesSerializer,
    RecipientSerializer,
)
from hope.apps.household.api.serializers.individual import (
    IndividualDetailSerializer,
    IndividualListSerializer,
    IndividualPhotoDetailSerializer,
)
from hope.apps.household.filters import HouseholdFilter, IndividualFilter
from hope.models.household import Household, Individual, IndividualRoleInHousehold
from hope.apps.payment.api.serializers import PaymentListSerializer
from hope.apps.payment.models import Payment, PaymentPlan
from hope.models.program import Program


class HouseholdViewSet(
    ProgramVisibilityMixin,
    SerializerActionMixin,
    CountActionMixin,
    RetrieveModelMixin,
    ListModelMixin,
    BaseViewSet,
):
    queryset = Household.all_merge_status_objects.all()
    serializer_classes_by_action = {
        "list": HouseholdListSerializer,
        "retrieve": HouseholdDetailSerializer,
        "members": HouseholdMemberSerializer,
        "payments": PaymentListSerializer,
        "all_flex_fields_attributes": FieldAttributeSerializer,
        "all_accountability_communication_message_recipients": RecipientSerializer,
        "recipients": RecipientSerializer,
    }
    permissions_by_action = {
        "list": [
            Permissions.POPULATION_VIEW_HOUSEHOLDS_LIST,
            Permissions.RDI_VIEW_DETAILS,
        ],
        "retrieve": [
            Permissions.POPULATION_VIEW_HOUSEHOLDS_DETAILS,
            Permissions.RDI_VIEW_DETAILS,
        ],
        "members": [
            Permissions.POPULATION_VIEW_HOUSEHOLDS_DETAILS,
            Permissions.RDI_VIEW_DETAILS,
        ],
        "payments": [
            Permissions.POPULATION_VIEW_HOUSEHOLDS_DETAILS,
            Permissions.PM_VIEW_DETAILS,
        ],
        "all_flex_fields_attributes": [
            Permissions.POPULATION_VIEW_HOUSEHOLDS_DETAILS,
            Permissions.RDI_VIEW_DETAILS,
        ],
        "all_accountability_communication_message_recipients": [
            Permissions.ACCOUNTABILITY_COMMUNICATION_MESSAGE_VIEW_LIST,
            Permissions.ACCOUNTABILITY_COMMUNICATION_MESSAGE_VIEW_DETAILS,
            Permissions.ACCOUNTABILITY_COMMUNICATION_MESSAGE_VIEW_DETAILS_AS_CREATOR,
        ],
        "recipients": [Permissions.ACCOUNTABILITY_SURVEY_VIEW_DETAILS],
    }
    filter_backends = (OrderingFilter, DjangoFilterBackend)
    filterset_class = HouseholdFilter
    admin_area_model_fields = ["admin1", "admin2", "admin3"]

    def get_queryset(self) -> QuerySet:
        if self.program.status == Program.DRAFT:
            return Household.objects.none()

        return (
            super()
            .get_queryset()
            .select_related("head_of_household", "program", "admin1", "admin2")
            .prefetch_related("program__sanction_lists")
            .order_by("created_at")
        )

    @etag_decorator(HouseholdListKeyConstructor)
    @cache_response(timeout=config.REST_API_TTL, key_func=HouseholdListKeyConstructor())
    def list(self, request: Any, *args: Any, **kwargs: Any) -> Any:
        return super().list(request, *args, **kwargs)

    @extend_schema(responses={200: HouseholdMemberSerializer(many=True)})
    @action(detail=True, methods=["get"], filter_backends=())
    def members(self, request: Any, *args: Any, **kwargs: Any) -> Any:
        instance = self.get_object()
        individuals_ids = list(instance.individuals(manager="all_merge_status_objects").values_list("id", flat=True))
        collectors_ids = list(instance.representatives(manager="all_merge_status_objects").values_list("id", flat=True))
        ids = set(individuals_ids + collectors_ids)
        members = (
            Individual.all_merge_status_objects.filter(id__in=ids)
            .order_by("created_at")
            .prefetch_related(
                Prefetch(
                    "households_and_roles",
                    queryset=IndividualRoleInHousehold.all_merge_status_objects.filter(household=instance.id),
                )
            )
        )

        page = self.paginate_queryset(members)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(members, many=True)
        return Response(serializer.data)

    @action(
        detail=True,
        methods=["post"],
    )
    def withdraw(self, request: Any, *args: Any, **kwargs: Any) -> Any:
        instance = self.get_object()
        instance.withdraw()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(
        responses={
            200: PaymentListSerializer(many=True),
        },
    )
    @action(detail=True, methods=["get"])
    def payments(self, request: Any, *args: Any, **kwargs: Any) -> Any:
        hh = self.get_object()
        payments = Payment.objects.filter(
            Q(household=hh) & ~Q(parent__status__in=PaymentPlan.PRE_PAYMENT_PLAN_STATUSES)
        )

        page = self.paginate_queryset(payments)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(payments, many=True)
        return Response(serializer.data)

    @extend_schema(
        responses={
            200: FieldAttributeSerializer(many=True),
        },
    )
    @action(detail=False, methods=["get"], url_path="all-flex-fields-attributes")
    def all_flex_fields_attributes(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        qs = (
            FlexibleAttribute.objects.filter(associated_with=FlexibleAttribute.ASSOCIATED_WITH_HOUSEHOLD)
            .prefetch_related("choices")
            .order_by("created_at")
        )
        return Response(FieldAttributeSerializer(qs, many=True).data, status=status.HTTP_200_OK)

    @extend_schema(responses={200: RecipientSerializer(many=True)})
    @action(
        detail=False,
        methods=["get"],
        url_path="all-accountability-communication-message-recipients",
    )
    def all_accountability_communication_message_recipients(self, request: Any, *args: Any, **kwargs: Any) -> Any:
        recipients = self.filter_queryset(
            self.get_queryset().exclude(
                head_of_household__phone_no_valid=False,
                head_of_household__phone_no_alternative_valid=False,
            )
        )

        page = self.paginate_queryset(recipients)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(recipients, many=True)
        return Response(serializer.data)

    @extend_schema(responses={200: RecipientSerializer(many=True)})
    @action(detail=False, methods=["get"])
    def recipients(self, request: Any, *args: Any, **kwargs: Any) -> Any:
        recipients = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(recipients)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(recipients, many=True)
        return Response(serializer.data)


class HouseholdGlobalViewSet(
    BusinessAreaVisibilityMixin,
    SerializerActionMixin,
    CountActionMixin,
    ListModelMixin,
    BaseViewSet,
):
    queryset = Household.all_merge_status_objects.exclude(program__status=Program.DRAFT).all()
    serializer_classes_by_action = {
        "list": HouseholdListSerializer,
        "choices": HouseholdChoicesSerializer,
    }
    PERMISSIONS = [
        Permissions.RDI_VIEW_DETAILS,
        Permissions.POPULATION_VIEW_HOUSEHOLDS_LIST,
    ]
    filter_backends = (OrderingFilter, DjangoFilterBackend)
    filterset_class = HouseholdFilter
    admin_area_model_fields = ["admin1", "admin2", "admin3"]

    def get_queryset(self) -> QuerySet:
        return (
            super()
            .get_queryset()
            .select_related("head_of_household", "program", "admin1", "admin2")
            .order_by("created_at")
        )

    @action(detail=False, methods=["get"])
    def choices(self, request: Any, *args: Any, **kwargs: Any) -> Any:
        return Response(data=self.get_serializer(instance={}).data)


class IndividualViewSet(
    ProgramVisibilityMixin,
    SerializerActionMixin,
    CountActionMixin,
    RetrieveModelMixin,
    ListModelMixin,
    BaseViewSet,
):
    queryset = Individual.all_merge_status_objects.all()
    serializer_classes_by_action = {
        "list": IndividualListSerializer,
        "retrieve": IndividualDetailSerializer,
        "photos": IndividualPhotoDetailSerializer,
        "all_flex_fields_attributes": FieldAttributeSerializer,
    }
    permissions_by_action = {
        "list": [
            Permissions.RDI_VIEW_DETAILS,
            Permissions.POPULATION_VIEW_INDIVIDUALS_LIST,
        ],
        "retrieve": [
            Permissions.RDI_VIEW_DETAILS,
            Permissions.POPULATION_VIEW_INDIVIDUALS_DETAILS,
        ],
        "photos": [
            Permissions.RDI_VIEW_DETAILS,
            Permissions.POPULATION_VIEW_INDIVIDUALS_DETAILS,
        ],
        "all_flex_fields_attributes": [
            Permissions.RDI_VIEW_DETAILS,
            Permissions.POPULATION_VIEW_INDIVIDUALS_DETAILS,
        ],
    }
    filter_backends = (OrderingFilter, DjangoFilterBackend)
    filterset_class = IndividualFilter
    admin_area_model_fields = [
        "household__admin1",
        "household__admin2",
        "household__admin3",
    ]

    def get_queryset(self) -> QuerySet:
        if self.program.status == Program.DRAFT:
            return Individual.objects.none()

        return (
            super()
            .get_queryset()
            .select_related(
                "household",
                "household__admin1",
                "household__admin2",
                "household__admin3",
                "household__admin4",
                "household__country",
                "household__country_origin",
                "household__head_of_household",
                "program",
            )
            .prefetch_related("accounts", "program__sanction_lists")
            .order_by("created_at")
        )

    @etag_decorator(IndividualListKeyConstructor)
    @cache_response(timeout=config.REST_API_TTL, key_func=IndividualListKeyConstructor())
    def list(self, request: Any, *args: Any, **kwargs: Any) -> Any:
        return super().list(request, *args, **kwargs)

    @action(detail=True, methods=["get"])
    def photos(self, request: Any, *args: Any, **kwargs: Any) -> Any:
        individual = self.get_object()
        return Response(IndividualPhotoDetailSerializer(individual).data, status=status.HTTP_200_OK)

    @extend_schema(
        responses={
            200: FieldAttributeSerializer(many=True),
        },
    )
    @action(detail=False, methods=["get"], url_path="all-flex-fields-attributes")
    def all_flex_fields_attributes(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        qs = (
            FlexibleAttribute.objects.filter(associated_with=FlexibleAttribute.ASSOCIATED_WITH_INDIVIDUAL)
            .exclude(type=FlexibleAttribute.PDU)
            .prefetch_related("choices")
            .order_by("created_at")
        )
        return Response(FieldAttributeSerializer(qs, many=True).data, status=status.HTTP_200_OK)


class IndividualGlobalViewSet(
    BusinessAreaVisibilityMixin,
    SerializerActionMixin,
    CountActionMixin,
    ListModelMixin,
    BaseViewSet,
):
    queryset = Individual.all_merge_status_objects.exclude(program__status=Program.DRAFT).all()
    serializer_classes_by_action = {
        "list": IndividualListSerializer,
        "choices": IndividualChoicesSerializer,
    }
    PERMISSIONS = [
        Permissions.RDI_VIEW_DETAILS,
        Permissions.POPULATION_VIEW_INDIVIDUALS_LIST,
    ]
    filter_backends = (OrderingFilter, DjangoFilterBackend)
    filterset_class = IndividualFilter
    admin_area_model_fields = [
        "household__admin1",
        "household__admin2",
        "household__admin3",
    ]

    def get_queryset(self) -> QuerySet:
        return super().get_queryset().select_related("household", "household__admin2", "program").order_by("created_at")

    @action(detail=False, methods=["get"])
    def choices(self, request: Any, *args: Any, **kwargs: Any) -> Any:
        return Response(data=self.get_serializer(instance={}).data)
