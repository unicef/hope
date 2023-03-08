from typing import Any

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import Http404, HttpRequest, HttpResponse, JsonResponse
from django.utils.functional import cached_property
from django.views.generic import TemplateView
from django.views.generic.edit import ProcessFormView

from admin_extra_buttons.utils import HttpResponseRedirectToReferrer
from sentry_sdk import set_tag

from .models import Registration
from .utils import fetch


class FetchDataView(ProcessFormView):
    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        return HttpResponseRedirectToReferrer(request)

    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        if "_fetch" in request.POST:
            messages.add_message(request, messages.SUCCESS, "Data fetched")
            fetch()
        return HttpResponseRedirectToReferrer(request)


class RegistrationDataView(PermissionRequiredMixin, TemplateView):
    template_name = "registration/dataset_list.html"
    permission_required = [
        "registration.can_view_data",
        "registration.can_manage_registration",
    ]
    raise_exception = False

    def get_context_data(self, **kwargs):
        kwargs["registration"] = self.registration
        kwargs["drf_page_size"] = settings.REST_FRAMEWORK["PAGE_SIZE"]
        return super().get_context_data(**kwargs)

    @cached_property
    def registration(self):
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
