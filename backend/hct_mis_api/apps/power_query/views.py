from calendar import timegm
from hashlib import md5

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse, HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.utils.cache import get_conditional_response
from django.utils.http import http_date

from .models import Report, ReportDocument
from .utils import basicauth


@login_required()
def report_list(request):
    reports: [Report] = Report.objects.all()
    return render(request, "power_query/list.html", {"reports": reports})


@login_required()
def report(request, pk):
    report: Report = get_object_or_404(Report, pk=pk)
    if request.user.has_perm("power_query.view_report", report):
        if not report.documents.exists():
            return HttpResponse("This report is not currently available", status=400)
        return render(request, "power_query/detail.html", {"report": report})
    else:
        raise PermissionDenied()


@login_required()
def document(request, report, pk):
    doc: ReportDocument = get_object_or_404(ReportDocument, pk=pk, report_id=report)
    res_etag = md5(doc.data.encode()).hexdigest()
    res_last_modified = timegm(doc.timestamp.utctimetuple())

    if not request.user.has_perm("power_query.view_reportdocument", doc):
        return HttpResponseForbidden()

    response = get_conditional_response(
        request,
        etag=res_etag,
        last_modified=res_last_modified,
    )
    if response is None:
        response = HttpResponse(doc.data, content_type=doc.content_type)
        if doc.content_type == "xls":
            response["Content-Disposition"] = f"attachment; filename={doc.title}.xls"
        else:
            response.headers["Cache-Control"] = "private"
            response.headers["Last-Modified"] = http_date(res_last_modified)
            response.headers["ETag"] = res_etag
    return response


@basicauth
def data(request, pk):
    doc: ReportDocument = get_object_or_404(ReportDocument, pk=pk)
    report: Report = doc.report
    if request.user.has_perm("power_query.view_reportdocument", doc):
        if doc.data is None:
            content_types = request.headers.get("Accept", "*/*").split(",")
            if "text/html" in content_types:
                return HttpResponse("This report is not currently available", status=400)
            elif "application/json" in content_types:
                return JsonResponse({"error": "This report is not currently available"}, status=400)
            else:
                return HttpResponse("This report is not currently available", content_type="text/plain", status=400)
        # data = pickle.loads(result.data)
        return HttpResponse(doc.data, content_type=report.formatter.get_content_type_display())
    else:
        return HttpResponseForbidden()
