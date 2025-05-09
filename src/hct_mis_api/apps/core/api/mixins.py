import os
from typing import TYPE_CHECKING, Any

from requests import Response, session
from requests.adapters import HTTPAdapter
from rest_framework.generics import get_object_or_404
from urllib3 import Retry

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
    def get_business_area(self) -> BusinessArea:
        return get_object_or_404(BusinessArea, slug=self.kwargs.get("business_area"))


class ProgramMixin:
    def get_program(self) -> "Program":
        from hct_mis_api.apps.program.models import Program

        return get_object_or_404(Program, id=decode_id_string(self.kwargs.get("program_id")))


class BusinessAreaProgramMixin(BusinessAreaMixin, ProgramMixin):
    pass


class ActionMixin:
    permission_classes_by_action = {}
    serializer_classes_by_action = {}

    def get_permissions(self) -> Any:
        if self.action in self.permission_classes_by_action:
            return [permission() for permission in self.permission_classes_by_action[self.action]]
        return super().get_permissions()  # pragma: no cover

    def get_serializer_class(self) -> Any:
        if self.action in self.serializer_classes_by_action:
            return self.serializer_classes_by_action[self.action]
        return super().get_serializer_class()  # pragma: no cover
