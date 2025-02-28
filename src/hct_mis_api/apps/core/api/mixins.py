import os
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple, Union

from django.db.models import QuerySet

from requests import Response, session
from requests.adapters import HTTPAdapter
from rest_framework import serializers
from rest_framework.generics import get_object_or_404
from rest_framework.viewsets import GenericViewSet
from urllib3 import Retry

from hct_mis_api.apps.account.api.permissions import HasOneOfPermissions
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.core.utils import decode_id_string

if TYPE_CHECKING:
    from hct_mis_api.apps.program.models import Program


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

    def _post(
        self, endpoint: str, data: Optional[Union[Dict, List]] = None, validate_response: bool = True
    ) -> Tuple[Dict, int]:
        response = self._client.post(f"{self.api_url}{endpoint}", json=data)
        if validate_response:
            response = self.validate_response(response)
        try:
            return response.json(), response.status_code
        except ValueError:
            return {}, response.status_code

    def _get(self, endpoint: str, params: Optional[Dict] = None) -> Tuple[Dict, int]:
        response = self._client.get(f"{self.api_url}{endpoint}", params=params)
        response = self.validate_response(response)
        return response.json(), response.status_code

    def _delete(self, endpoint: str, params: Optional[Dict] = None) -> Tuple[Dict, int]:
        response = self._client.delete(f"{self.api_url}{endpoint}", params=params)
        response = self.validate_response(response)
        try:
            return response.json(), response.status_code
        except ValueError:
            return {}, response.status_code


class BusinessAreaMixin:
    business_area_model_field = "business_area"

    @property
    def business_area_slug(self) -> Optional[str]:
        return self.kwargs.get("business_area_slug")

    def get_business_area(self) -> BusinessArea:
        return get_object_or_404(BusinessArea, slug=self.business_area_slug)

    def get_queryset(self) -> QuerySet:
        return self.queryset.filter(**{f"{self.business_area_model_field}__slug": self.business_area_slug})


class ProgramMixin:
    program_model_field = "program"

    @property
    def program_id(self) -> Optional[str]:
        return decode_id_string(self.kwargs.get("program_pk"))

    def get_program(self) -> "Program":
        from hct_mis_api.apps.program.models import Program

        return get_object_or_404(Program, id=self.program_id)

    def get_queryset(self) -> QuerySet:
        return self.queryset.filter(**{self.program_model_field: self.program_id})


class BusinessAreaProgramMixin(ProgramMixin, BusinessAreaMixin):
    pass


class ActionMixin:
    permission_classes_by_action = {}
    serializer_classes_by_action = {}

    def get_permissions(self) -> Any:
        if self.action in self.permission_classes_by_action:
            return [permission() for permission in self.permission_classes_by_action[self.action]]
        else:
            return super().get_permissions()  # pragma: no cover

    def get_serializer_class(self) -> Any:
        if self.action in self.serializer_classes_by_action:
            return self.serializer_classes_by_action[self.action]
        else:
            return super().get_serializer_class()  # pragma: no cover


class CustomSerializerMixin:
    serializer_classes = {}

    def get_serializer_class(self) -> None:
        if self.action in ["retrieve", "list"] and (
            serializer_class := self.serializer_classes.get(self.request.GET.get("serializer"))
        ):
            return serializer_class
        return super().get_serializer_class()


class DecodeIdForDetailMixin:
    def get_object(self) -> Any:
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        self.kwargs[lookup_url_kwarg] = decode_id_string(self.kwargs[lookup_url_kwarg])
        return super().get_object()


class BaseViewSet(GenericViewSet):
    permission_classes: list = [HasOneOfPermissions]
    PERMISSIONS: list = []


class AdminUrlSerializerMixin:
    admin_url = serializers.SerializerMethodField()

    def resolve_admin_url(self, obj: Any) -> Optional[str]:
        if self.context.request.user.is_superuser:
            return obj.admin_url
        return None
