import logging

from django import forms
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.generic import View

from graphene_django.settings import graphene_settings
from graphql.utils import schema_printer

from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.forms import StorageFileForm
from hct_mis_api.apps.core.hope_redirect import get_hope_redirect
from hct_mis_api.apps.core.models import StorageFile
from hct_mis_api.apps.core.permissions_views_mixins import UploadFilePermissionMixin
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.reporting.models import DashboardReport

logger = logging.getLogger(__name__)


def homepage(request):
    return HttpResponse("", status=200)


def schema(request):
    schema = graphene_settings.SCHEMA
    my_schema_str = schema_printer.print_schema(schema)
    return HttpResponse(my_schema_str, content_type="application/graphlq", status=200)


def logout_view(request):
    logout(request)
    return redirect("/login")


class CommandForm(forms.Form):
    command = forms.CharField(label="Command", max_length=255, required=True)
    no_input = forms.BooleanField(label="No input", required=False)


def trigger_error(request):
    division_by_zero = 1 / 0  # noqa: F841


@login_required
def download_dashboard_report(request, report_id):
    report = get_object_or_404(DashboardReport, id=report_id)
    if not request.user.has_permission(Permissions.DASHBOARD_EXPORT.name, report.business_area):
        logger.error("Permission Denied: You need dashboard export permission to access this file")
        raise PermissionDenied("Permission Denied: You need dashboard export permission to access this file")
    return redirect(report.file.url)


@login_required
def hope_redirect(request):
    ent = request.GET.get("ent")
    caid = request.GET.get("caid")
    sourceid = request.GET.get("sourceid")
    programid = request.GET.get("programid")
    hope_redirect = get_hope_redirect(request.user, ent, caid, sourceid, programid)
    return redirect(hope_redirect.url())


class UploadFile(UploadFilePermissionMixin, View):
    login_url = "/login"
    redirect_field_name = "next"

    def get(self, request):
        user = request.user
        return render(request, self.template_name, {"form": StorageFileForm(user=user)})

    def post(self, request):
        user = request.user
        form = StorageFileForm(request.POST, request.FILES, user=user)
        if form.is_valid():
            new_file = StorageFile(
                created_by=user, file=request.FILES["file"], business_area_id=request.POST["business_area"]
            )
            new_file.save()
            messages.success(request, f"File {new_file.file.name} has been successfully uploaded.")
            return HttpResponseRedirect(reverse("upload-file"))
        else:
            messages.error(request, self.format_form_error(form))
            return render(request, self.template_name, {"form": StorageFileForm(user=user)})

    @property
    def template_name(self):
        return "core/upload_file.html"

    @staticmethod
    def format_form_error(form):
        return form.errors.get_json_data()["__all__"][0]["message"]


def load_programs(request):
    business_area_id = request.GET.get('business_area_id')

    logger.info(business_area_id)

    programs = Program.objects.filter(Q(business_area_id=business_area_id) & Q(status=Program.ACTIVE))
    return render(request, "core/program_dropdown_list_options.html", {"programs": programs})
