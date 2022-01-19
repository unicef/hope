import pickle

from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from .models import Report


def report(request, pk):
    report = get_object_or_404(Report, pk=pk)
    data = pickle.loads(report.result)
    return HttpResponse(data, content_type=report.formatter.content_type)


def api(request, pk):
    pass
