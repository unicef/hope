from typing import Any, Dict

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import Http404, HttpRequest
from django.utils.functional import cached_property
from django.views.generic import TemplateView
from django.views.generic.edit import ProcessFormView

from admin_extra_buttons.utils import HttpResponseRedirectToReferrer
from sentry_sdk import set_tag

from hct_mis_api.aurora.models import Registration
from hct_mis_api.aurora.utils import fetch_metadata


class FetchDataView(ProcessFormView):
    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponseRedirectToReferrer:
        return HttpResponseRedirectToReferrer(request)

    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponseRedirectToReferrer:
        if "_fetch" in request.POST:
            messages.add_message(request, messages.SUCCESS, "Data fetched")
            aurora_token = request.user.custom_fields.get("aurora_token")
            fetch_metadata(aurora_token)
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
