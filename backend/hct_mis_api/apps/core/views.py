import logging

from django import forms
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect

from graphene_django.settings import graphene_settings
from graphql.utils import schema_printer

from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.hope_redirect import get_hope_redirect
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
