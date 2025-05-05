from typing import Any

from django.db.models import Prefetch, QuerySet

from constance import config
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.response import Response
from rest_framework_extensions.cache.decorators import cache_response

from hct_mis_api.api.caches import etag_decorator
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.api.mixins import (
    BaseViewSet,
    BusinessAreaVisibilityMixin,
    CountActionMixin,
    ProgramVisibilityMixin,
    SerializerActionMixin,
)
from hct_mis_api.apps.household.api.caches import (
    HouseholdListKeyConstructor,
    IndividualListKeyConstructor,
)
from hct_mis_api.apps.household.api.serializers.household import (
    HouseholdChoicesSerializer,
    HouseholdDetailSerializer,
    HouseholdListSerializer,
    HouseholdMemberSerializer,
    IndividualChoicesSerializer,
)
from hct_mis_api.apps.household.api.serializers.individual import (
    IndividualDetailSerializer,
    IndividualListSerializer,
)
from hct_mis_api.apps.household.filters import HouseholdFilter, IndividualFilter
from hct_mis_api.apps.household.models import (
    Household,
    Individual,
    IndividualRoleInHousehold,
)
from hct_mis_api.apps.payment.api.serializers import PaymentListSerializer
from hct_mis_api.apps.payment.models import Payment
from hct_mis_api.apps.program.models import Program


class HouseholdViewSet(
    ProgramVisibilityMixin,
    SerializerActionMixin,
    CountActionMixin,
    RetrieveModelMixin,
    ListModelMixin,
    BaseViewSet,
):
    queryset = Household.all_merge_status_objects.order_by("created_at")
    serializer_classes_by_action = {
        "list": HouseholdListSerializer,
        "retrieve": HouseholdDetailSerializer,
        "members": HouseholdMemberSerializer,
        "payments": PaymentListSerializer,
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
            .order_by("created_at")
        )

    @etag_decorator(HouseholdListKeyConstructor)
    @cache_response(timeout=config.REST_API_TTL, key_func=HouseholdListKeyConstructor())
    def list(self, request: Any, *args: Any, **kwargs: Any) -> Any:
        return super().list(request, *args, **kwargs)

    @action(detail=True, methods=["get"])
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
        payments = Payment.objects.filter(household=hh)

        page = self.paginate_queryset(payments)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(payments, many=True)
        return Response(serializer.data)


class HouseholdGlobalViewSet(
    BusinessAreaVisibilityMixin,
    SerializerActionMixin,
    CountActionMixin,
    ListModelMixin,
    BaseViewSet,
):
    queryset = Household.all_merge_status_objects.exclude(status=Program.DRAFT).all()
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
    queryset = Individual.all_merge_status_objects.order_by("created_at")
    serializer_classes_by_action = {
        "list": IndividualListSerializer,
        "retrieve": IndividualDetailSerializer,
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
    }
    filter_backends = (OrderingFilter, DjangoFilterBackend)
    filterset_class = IndividualFilter
    admin_area_model_fields = ["household__admin1", "household__admin2", "household__admin3"]

    def get_queryset(self) -> QuerySet:
        if self.program.status == Program.DRAFT:
            return Individual.objects.none()

        return super().get_queryset().select_related("household", "household__admin2").order_by("created_at")

    @etag_decorator(IndividualListKeyConstructor)
    @cache_response(timeout=config.REST_API_TTL, key_func=IndividualListKeyConstructor())
    def list(self, request: Any, *args: Any, **kwargs: Any) -> Any:
        return super().list(request, *args, **kwargs)


class IndividualGlobalViewSet(
    BusinessAreaVisibilityMixin,
    SerializerActionMixin,
    CountActionMixin,
    ListModelMixin,
    BaseViewSet,
):
    queryset = Individual.all_merge_status_objects.exclude(status=Program.DRAFT).all()
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
    admin_area_model_fields = ["household__admin1", "household__admin2", "household__admin3"]

    def get_queryset(self) -> QuerySet:
        return super().get_queryset().select_related("household", "household__admin2").order_by("created_at")

    @action(detail=False, methods=["get"])
    def choices(self, request: Any, *args: Any, **kwargs: Any) -> Any:
        return Response(data=self.get_serializer(instance={}).data)
