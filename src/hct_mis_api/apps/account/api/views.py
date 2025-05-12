from typing import TYPE_CHECKING, Any

from django.db.models import Q, QuerySet

from constance import config
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
from rest_framework.mixins import ListModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_extensions.cache.decorators import cache_response

from hct_mis_api.api.caches import etag_decorator
from hct_mis_api.apps.account.api.caches import UserListKeyConstructor
from hct_mis_api.apps.account.api.serializers import (
    ProfileSerializer,
    UserChoicesSerializer,
    UserSerializer,
)
from hct_mis_api.apps.account.filters import UsersFilter
from hct_mis_api.apps.account.models import User
from hct_mis_api.apps.account.permissions import (
    ALL_GRIEVANCES_CREATE_MODIFY,
    Permissions,
)
from hct_mis_api.apps.core.api.mixins import (
    BaseViewSet,
    CountActionMixin,
    CustomSerializerMixin,
    PermissionActionMixin,
    SerializerActionMixin,
)

if TYPE_CHECKING:
    from rest_framework.request import Request


class UserViewSet(
    CustomSerializerMixin, SerializerActionMixin, PermissionActionMixin, CountActionMixin, ListModelMixin, BaseViewSet
):
    permission_classes_by_action = {
        "profile": [IsAuthenticated],
    }
    permissions_by_action = {
        "list": [Permissions.USER_MANAGEMENT_VIEW_LIST, *ALL_GRIEVANCES_CREATE_MODIFY],
        "choices": [Permissions.USER_MANAGEMENT_VIEW_LIST, *ALL_GRIEVANCES_CREATE_MODIFY],
    }
    queryset = User.objects.all()

    serializer_classes_by_action = {
        "profile": ProfileSerializer,
        "list": UserSerializer,
        "choices": UserChoicesSerializer,
    }
    serializer_classes = {
        "program_users": ProfileSerializer,
    }
    filter_backends = (OrderingFilter, DjangoFilterBackend)
    filterset_class = UsersFilter

    def get_queryset(self) -> QuerySet[User]:
        business_area_slug = self.kwargs.get("business_area_slug")
        return (
            super()
            .get_queryset()
            .filter(
                Q(role_assignments__business_area__slug=business_area_slug)
                | Q(partner__role_assignments__business_area__slug=business_area_slug)
            )
            .order_by("first_name")
        )

    @extend_schema(parameters=[OpenApiParameter(name="program")])
    @action(detail=False, methods=["get"], url_path="profile", url_name="profile")
    def profile(self, request: "Request", *args: Any, **kwargs: Any) -> Response:
        user = request.user
        serializer = self.get_serializer(user)
        return Response(serializer.data)

    @extend_schema(parameters=[OpenApiParameter(name="serializer",  type=str)])
    @etag_decorator(UserListKeyConstructor)
    @cache_response(timeout=config.REST_API_TTL, key_func=UserListKeyConstructor())
    def list(self, request: "Request", *args: Any, **kwargs: Any) -> Response:
        return super().list(request, *args, **kwargs)

    @action(detail=False, methods=["get"])
    def choices(self, request: Any, *args: Any, **kwargs: Any) -> Any:
        return Response(data=self.get_serializer(instance={}).data)
