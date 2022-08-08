import pickle

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404

from .models import Report
from .utils import basicauth


@login_required()
def report(request, pk):
    report: Report = get_object_or_404(Report, pk=pk)
    if request.user.is_superuser or report.available_to.filter(pk=request.user.pk):
        if report.result is None:
            return HttpResponse("This report is not currently available", status=400)
        data = pickle.loads(report.result)
        if report.formatter.content_type == "xls":
            response = HttpResponse(data, content_type=report.formatter.content_type)
            response["Content-Disposition"] = f"attachment; filename={report.name}.xls"
            return response
        else:
            return HttpResponse(data, content_type=report.formatter.content_type)
    else:
        raise PermissionDenied()


@basicauth
def fetch(request, pk):
    report: Report = get_object_or_404(Report, pk=pk)
    if request.user.is_superuser or report.available_to.filter(pk=request.user.pk):
        if report.result is None:
            content_types = request.headers.get("Accept", "*/*").split(",")
            if "text/html" in content_types:
                return HttpResponse("This report is not currently available", status=400)
            elif "application/json" in content_types:
                return JsonResponse({"error": "This report is not currently available"}, status=400)
            else:
                return HttpResponse("This report is not currently available", content_type="text/plain", status=400)
        data = pickle.loads(report.result)
        return HttpResponse(data, content_type=report.formatter.get_content_type_display())
    else:
        raise PermissionDenied()
