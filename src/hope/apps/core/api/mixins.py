import os
from functools import cached_property
from typing import TYPE_CHECKING, Any

from django.db.models import Q, QuerySet

from drf_spectacular.utils import extend_schema, inline_serializer
from requests import Response, session
from requests.adapters import HTTPAdapter
from rest_framework import serializers, status
from rest_framework.authentication import get_authorization_header
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response as DRFResponse
from rest_framework.viewsets import GenericViewSet
from urllib3 import Retry

from hope.api.auth import HOPEAuthentication, HOPEPermission
from hope.api.models import Grant
from hope.apps.account.api.permissions import BaseRestPermission
from hope.apps.core.models import BusinessArea

if TYPE_CHECKING:
    from hope.apps.program.models import Program


class BaseAPI:
    API_KEY_ENV_NAME = ""
    API_URL_ENV_NAME = ""

    class APIException(Exception):
        pass

    class APIMissingCredentialsException(Exception):
        pass

    API_EXCEPTION_CLASS = APIException
    API_MISSING_CREDENTIALS_EXCEPTION_CLASS = APIMissingCredentialsException

    def __init__(self) -> None:
        self.api_key = os.getenv(self.API_KEY_ENV_NAME)
        self.api_url = os.getenv(self.API_URL_ENV_NAME)

        if not self.api_key or not self.api_url:
            raise self.API_MISSING_CREDENTIALS_EXCEPTION_CLASS(f"Missing {self.__class__.__name__} Key/URL")

        self._client = session()
        retries = Retry(total=3, backoff_factor=1, status_forcelist=[502, 503, 504], allowed_methods=None)
        self._client.mount(self.api_url, HTTPAdapter(max_retries=retries))
        self._client.headers.update({"Authorization": f"Token {self.api_key}"})

    def validate_response(self, response: Response) -> Response:
        if not response.ok:
            raise self.API_EXCEPTION_CLASS(
                f"{self.__class__.__name__} Invalid response: {response}, {response.content!r}, {response.url}"
            )

        return response

    def _post(self, endpoint: str, data: dict | list | None = None, validate_response: bool = True) -> tuple[dict, int]:
        response = self._client.post(f"{self.api_url}{endpoint}", json=data)
        if validate_response:
            response = self.validate_response(response)
        try:
            return response.json(), response.status_code
        except ValueError:
            return {}, response.status_code

    def _get(self, endpoint: str, params: dict | None = None) -> tuple[dict, int]:
        response = self._client.get(f"{self.api_url}{endpoint}", params=params)
        response = self.validate_response(response)
        return response.json(), response.status_code

    def _delete(self, endpoint: str, params: dict | None = None) -> tuple[dict, int]:
        response = self._client.delete(f"{self.api_url}{endpoint}", params=params)
        response = self.validate_response(response)
        try:
            return response.json(), response.status_code
        except ValueError:
            return {}, response.status_code


class BusinessAreaMixin:
    business_area_model_field = "business_area"

    @property
    def business_area_slug(self) -> str | None:
        return self.kwargs.get("business_area_slug")

    @cached_property
    def business_area(self) -> BusinessArea:
        return get_object_or_404(BusinessArea, slug=self.business_area_slug)

    def get_queryset(self) -> QuerySet:
        return super().get_queryset().filter(**{f"{self.business_area_model_field}__slug": self.business_area_slug})


class ProgramMixin:
    program_model_field = "program"

    @cached_property
    def business_area(self) -> BusinessArea:
        return self.program.business_area

    @property
    def business_area_slug(self) -> str | None:
        return self.kwargs.get("business_area_slug")

    @property
    def program_slug(self) -> str | None:
        return self.kwargs.get("program_slug")

    @cached_property
    def program(self) -> "Program":
        from hope.apps.program.models import Program

        return get_object_or_404(Program, slug=self.program_slug, business_area__slug=self.business_area_slug)

    def get_serializer_context(self) -> dict:
        context = super().get_serializer_context()
        context["program"] = self.program
        context["business_area"] = self.business_area
        return context

    def get_queryset(self) -> QuerySet:
        return (
            super()
            .get_queryset()
            .filter(
                **{
                    f"{self.program_model_field}__slug__in": [self.program_slug],
                    f"{self.program_model_field}__business_area__slug": self.business_area_slug,
                }
            )
        )


class BusinessAreaProgramsAccessMixin(BusinessAreaMixin):
    #  Applies BusinessAreaMixin and also filters the queryset based on the user's partner's permissions across programs.

    def get_queryset(self) -> QuerySet:
        queryset = super().get_queryset()

        program_ids = self.request.user.get_program_ids_for_permissions_in_business_area(
            self.business_area.id,
            self.PERMISSIONS,
        )

        return queryset.filter(
            Q(**{f"{self.program_model_field}__in": program_ids}) | Q(**{f"{self.program_model_field}__isnull": True})
        )


class ProgramVisibilityMixin(ProgramMixin):
    #  Applies ProgramMixin and also filters the queryset based on the user's partner's area limits for the program.

    def get_queryset(self) -> QuerySet:
        queryset = super().get_queryset()

        if area_limits := self.request.user.partner.get_area_limits_for_program(self.program.id):
            areas_null = Q(**{f"{field}__isnull": True for field in self.admin_area_model_fields})
            areas_query = Q()
            for field in self.admin_area_model_fields:
                areas_query |= Q(**{f"{field}__in": area_limits})
            queryset = queryset.filter(Q(areas_null | Q(areas_query)))

        return queryset


class BusinessAreaVisibilityMixin(BusinessAreaMixin):
    #  Applies BusinessAreaMixin and also filters the queryset based on the user's partner's area limits.

    program_model_field = "program"

    def get_queryset(self) -> QuerySet:
        from hope.apps.program.models import Program

        queryset = super().get_queryset()
        user = self.request.user
        program_ids = user.get_program_ids_for_permissions_in_business_area(
            self.business_area.id,
            self.get_permissions_for_action(),
        )

        filter_q = Q()
        for program_id in Program.objects.filter(id__in=program_ids).values_list("id", flat=True):
            program_q = Q(**{f"{self.program_model_field}__id__in": [program_id]})
            areas_null = Q(**{f"{field}__isnull": True for field in self.admin_area_model_fields})
            # apply admin area limits if partner has restrictions
            areas_query = Q()
            if area_limits := user.partner.get_area_limits_for_program(program_id):
                for field in self.admin_area_model_fields:
                    areas_query |= Q(**{f"{field}__in": area_limits})

            filter_q |= Q(program_q & areas_null) | Q(program_q & areas_query)
        return (
            queryset.filter(Q(filter_q) | Q(**{f"{self.program_model_field}__isnull": True}))
            if filter_q
            else queryset.none()
        )  # filter_q empty if no access to any program


class PermissionActionMixin:
    permission_classes_by_action = {}

    def get_permissions(self) -> Any:
        if self.action in self.permission_classes_by_action:
            return [permission() for permission in self.permission_classes_by_action[self.action]]
        return super().get_permissions()  # pragma: no cover


class SerializerActionMixin:
    serializer_classes_by_action = {}

    def get_serializer_class(self) -> Any:
        if self.action in self.serializer_classes_by_action:
            return self.serializer_classes_by_action[self.action]
        return super().get_serializer_class()  # pragma: no cover


class ActionMixin(PermissionActionMixin, SerializerActionMixin):
    pass


class CustomSerializerMixin:
    serializer_classes = {}

    def get_serializer_class(self) -> None:
        if self.action in ["retrieve", "list"] and (
            serializer_class := self.serializer_classes.get(self.request.GET.get("serializer"))
        ):
            return serializer_class
        return super().get_serializer_class()


class BaseViewSet(GenericViewSet):
    permission_classes: list = [BaseRestPermission]
    PERMISSIONS: list = []

    def get_permissions_for_action(self) -> Any:
        if hasattr(self, "permissions_by_action"):
            if self.action in self.permissions_by_action:
                return self.permissions_by_action[self.action]
            if self.action == "count":
                return self.permissions_by_action["list"]
        return self.PERMISSIONS


class AdminUrlSerializerMixin:
    admin_url = serializers.SerializerMethodField()

    def resolve_admin_url(self, obj: Any) -> str | None:
        if self.context.request.user.is_superuser:
            return obj.admin_url
        return None


class CountActionMixin:
    #  Adds a count action to the viewset that returns the count of the queryset.
    ordering_fields = "__all__"

    @extend_schema(
        responses={
            status.HTTP_200_OK: inline_serializer("CountResponse", fields={"count": serializers.IntegerField()})
        },
        filters=True,
    )
    @action(
        detail=False,
        methods=["get"],
    )
    def count(self, request: Any, *args: Any, **kwargs: Any) -> Any:
        queryset = self.filter_queryset(self.get_queryset())
        queryset_count = queryset.count()
        return DRFResponse({"count": queryset_count})


class PermissionsMixin:
    #  Mixin to allow using the same viewset for both internal and external endpoints.
    #  If the request is authenticated with a token, it will use the HOPEPermission and check permission assigned to variable token_permission.

    token_permission = Grant.API_READ_ONLY

    def is_external_request(self) -> bool:
        # condition for the swagger
        if not self.request:  # pragma: no cover
            return False

        auth_header = get_authorization_header(self.request).split()
        return auth_header and auth_header[0].lower() == b"token"

    def get_authenticators(self) -> list[Any]:
        if self.is_external_request():
            self.authentication_classes = [HOPEAuthentication]
        return super().get_authenticators()  # pragma: no cover

    def get_permissions(self) -> Any:
        if self.is_external_request():
            self.permission_classes = [HOPEPermission]
            self.permission = self.token_permission
        return super().get_permissions()  # pragma: no cover
