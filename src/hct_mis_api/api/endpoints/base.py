from typing import Any, Dict

from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.http import Http404, HttpRequest
from django.http.response import HttpResponseBase
from django.utils.functional import cached_property

from constance import config
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ViewSetMixin

from hct_mis_api.api.auth import HOPEAuthentication, HOPEPermission
from hct_mis_api.api.models import APILogEntry, Grant
from hct_mis_api.apps.core.models import BusinessArea


class RejectPolicy(models.TextChoices):
    STRICT = "STRICT", "Strict"
    LAX = "LAX", "Lax"


class SelectedBusinessAreaMixin:
    @cached_property
    def selected_business_area(self) -> BusinessArea:
        try:
            return self.request.auth.valid_for.all().get(slug=self.kwargs.get("business_area", None))
        except ObjectDoesNotExist:
            raise Http404


class HOPEAPIView(APIView):
    permission_classes = [HOPEPermission]
    authentication_classes = [HOPEAuthentication]
    permission = Grant.API_READ_ONLY
    log_http_methods = ["POST", "PUT", "DELETE"]

    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponseBase:
        ret = super().dispatch(request, *args, **kwargs)
        if request.method.upper() in self.log_http_methods and (ret.status_code < 300 or ret.status_code > 400):
            if request.auth:
                log = APILogEntry.objects.create(
                    token=request.auth,
                    url=request.path,
                    method=request.method.upper(),
                    status_code=ret.status_code,
                )
                assert log.pk

        return ret

    def handle_exception(self, exc: Exception) -> Any:
        if isinstance(exc, PermissionDenied):
            perm_name = self.permission.name if self.permission else ""
            exc = PermissionDenied("%s %s" % (exc.detail, perm_name))

        return super().handle_exception(exc)


class HOPEAPIViewSet(ViewSetMixin, HOPEAPIView):
    pass


class HOPEAPIBusinessAreaView(SelectedBusinessAreaMixin, HOPEAPIView):
    pass


class HOPEAPIBusinessAreaViewSet(SelectedBusinessAreaMixin, HOPEAPIViewSet):
    pass


class ConstanceSettingsAPIView(HOPEAPIView):
    def get(self, request: HttpRequest) -> Response:
        rest_settings: Dict[str, Any] = {}
        for setting_name in dir(config):
            if setting_name.startswith("REST_"):
                setting_value = getattr(config, setting_name)
                rest_setting_name = setting_name[len("REST_") :]
                rest_settings[rest_setting_name] = setting_value

        return Response(rest_settings, status=status.HTTP_200_OK)
