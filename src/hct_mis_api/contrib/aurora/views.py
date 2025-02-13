from typing import Any, Dict

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import Http404, HttpRequest
from django.http.response import HttpResponseBase
from django.utils.functional import cached_property
from django.views.generic import TemplateView
from django.views.generic.edit import ProcessFormView

from admin_extra_buttons.utils import HttpResponseRedirectToReferrer
from constance import config
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.generics import ListAPIView
from rest_framework_extensions.cache.decorators import cache_response
from sentry_sdk import set_tag

from hct_mis_api.api.caches import etag_decorator
from hct_mis_api.api.endpoints.base import HOPEAPIView
from hct_mis_api.api.filters import ProjectFilter, RegistrationFilter
from hct_mis_api.contrib.aurora.api import (
    OrganizationSerializer,
    ProjectSerializer,
    RegistrationSerializer,
)
from hct_mis_api.contrib.aurora.caches import AuroraKeyConstructor
from hct_mis_api.contrib.aurora.models import Organization, Project, Registration
from hct_mis_api.contrib.aurora.utils import fetch_metadata


class FetchDataView(ProcessFormView):
    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponseRedirectToReferrer:
        return HttpResponseRedirectToReferrer(request)

    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponseRedirectToReferrer:
        if "_fetch" in request.POST:
            aurora_token = request.user.custom_fields.get("aurora_token")
            try:
                fetch_metadata(aurora_token)
                messages.add_message(request, messages.SUCCESS, "Data fetched")
            except Exception as e:
                messages.add_message(request, messages.ERROR, str(e))
        return HttpResponseRedirectToReferrer(request)


class RegistrationDataView(PermissionRequiredMixin, TemplateView):
    template_name = "dataset_list.html"
    permission_required = [
        "registration.can_view_data",
        "registration.can_manage_registration",
    ]
    raise_exception = False

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        kwargs["registration"] = self.registration
        kwargs["drf_page_size"] = settings.REST_FRAMEWORK["PAGE_SIZE"]
        return super().get_context_data(**kwargs)

    @cached_property
    def registration(self) -> Registration:
        if "slug" in self.kwargs:
            filters = {"slug": self.kwargs["slug"]}
        elif "pk" in self.kwargs:
            filters = {"pk": self.kwargs["pk"]}
        else:
            raise Http404
        base = Registration.objects.select_related("flex_form", "validator", "project", "project__organization")
        try:
            reg = base.get(**filters)
            set_tag("registration.organization", reg.project.organization.name)
            set_tag("registration.project", reg.project.name)
            set_tag("registration.slug", reg.name)
            return reg
        except Registration.DoesNotExist:  # pragma: no coalidateer
            raise Http404


class OrganizationListView(HOPEAPIView, ListAPIView):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer

    @etag_decorator(AuroraKeyConstructor)
    @cache_response(timeout=config.REST_API_TTL, key_func=AuroraKeyConstructor())
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class ProjectListView(HOPEAPIView, ListAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProjectFilter

    @etag_decorator(AuroraKeyConstructor)
    @cache_response(timeout=config.REST_API_TTL, key_func=AuroraKeyConstructor())
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class RegistrationListView(HOPEAPIView, ListAPIView):
    queryset = Registration.objects.all()
    serializer_class = RegistrationSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = RegistrationFilter

    @etag_decorator(AuroraKeyConstructor)
    @cache_response(timeout=config.REST_API_TTL, key_func=AuroraKeyConstructor())
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
