import pickle

from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from .models import Report


def report(request, pk):
    report = get_object_or_404(Report, pk=pk)
    if request.user.is_superuser or report.available_to.filter(pk=request.user.pk):
        data = pickle.loads(report.result)
        return HttpResponse(data, content_type=report.formatter.content_type)
    else:
        raise PermissionDenied()


def api(request, pk):
    pass
