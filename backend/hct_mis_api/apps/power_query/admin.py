import logging
import pickle

from django.contrib import messages
from django.contrib.admin import ModelAdmin, register
from django.contrib.contenttypes.models import ContentType
from django.db.models import QuerySet
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

import tablib
from admin_extra_urls.decorators import button
from admin_extra_urls.mixins import ExtraUrlMixin
from adminfilters.autocomplete import AutoCompleteFilter
from import_export.admin import ImportExportMixin
from tablib import Dataset

from .forms import ExportForm, QueryForm
from .models import Dataset, Formatter, Query, Report
from .tasks import queue
from .utils import to_dataset

logger = logging.getLogger(__name__)


@register(Query)
class QueryAdmin(ImportExportMixin, ExtraUrlMixin, ModelAdmin):
    list_display = ("name", "target", "description", "owner")
    search_fields = ("name",)
    list_filter = (
        ("target", AutoCompleteFilter),
        ("owner", AutoCompleteFilter),
    )
    autocomplete_fields = ("target", "owner")
    form = QueryForm
    change_form_template = None

    @button()
    def result(self, request, pk):
        obj = self.get_object(request, pk)
        try:
            url = reverse("admin:power_query_dataset_change", args=[obj.dataset.pk])
            return HttpResponseRedirect(url)
        except Exception as e:
            self.message_user(request, f"{e.__class__.__name__}: {e}", messages.ERROR)

    @button()
    def queue(self, request, pk):
        try:
            queue.delay(pk)
            self.message_user(request, "Query scheduled")
        except Exception as e:
            self.message_user(request, f"{e.__class__.__name__}: {e}", messages.ERROR)

    @button()
    def preview(self, request, pk):
        obj: Query = self.get_object(request, pk)
        try:
            context = self.get_common_context(request, pk, title="Results")
            ret = obj.execute(persist=False)
            context["type"] = type(ret).__name__
            if isinstance(ret, QuerySet):
                ret = ret[:100]
                context["queryset"] = ret
            elif isinstance(ret, tablib.Dataset):
                context["dataset"] = ret
            elif isinstance(ret, dict):
                context["result"] = ret
            return render(request, "power_query/preview.html", context)
        except Exception as e:
            self.message_user(request, f"{e.__class__.__name__}: {e}", messages.ERROR)

    def get_changeform_initial_data(self, request):
        ct = ContentType.objects.filter(id=request.GET.get("ct", 0)).first()
        return {"code": "result=conn.all()", "name": ct, "target": ct, "owner": request.user}


@register(Dataset)
class DatasetAdmin(ExtraUrlMixin, ModelAdmin):
    search_fields = ("query__name",)
    list_display = ("query", "dataset_type", "target_type")
    list_filter = (("query__target", AutoCompleteFilter),)
    change_form_template = None
    readonly_fields = ("last_run", "query", "info")
    date_hierarchy = "last_run"

    def has_add_permission(self, request):
        return False

    def dataset_type(self, obj):
        return obj.info.get("type")

    def target_type(self, obj):
        return obj.query.target

    @button(visible=lambda o, r: "change" in r.path)
    def export(self, request, pk):
        obj = self.get_object(request, pk)
        try:
            context = self.get_common_context(request, pk, title="Export")
            if request.method == "POST":
                form = ExportForm(request.POST)
                if form.is_valid():
                    formatter: Formatter = form.cleaned_data["formatter"]
                    report_context = {
                        "dataset": obj,
                        "query": obj.query,
                    }
                    output = formatter.render(report_context)
                    return HttpResponse(output)
            else:
                form = ExportForm()
            context["form"] = form
            return render(request, "admin/power_query/dataset/export.html", context)
        except Exception as e:
            logger.exception(e)
            self.message_user(request, f"{e.__class__.__name__}: {e}", messages.ERROR)

    @button(visible=lambda o, r: "change" in r.path)
    def preview(self, request, pk):
        obj = self.get_object(request, pk)
        try:
            context = self.get_common_context(request, pk, title="Results")
            data = pickle.loads(obj.result)
            context["dataset"] = to_dataset(data)
            return render(request, "power_query/preview.html", context)
        except Exception as e:
            self.message_user(request, f"{e.__class__.__name__}: {e}", messages.ERROR)


@register(Formatter)
class FormatterAdmin(ImportExportMixin, ExtraUrlMixin, ModelAdmin):
    list_display = ("name", "content_type")
    search_fields = ("name",)
    list_filter = ("content_type",)


@register(Report)
class ReportAdmin(ImportExportMixin, ExtraUrlMixin, ModelAdmin):
    list_display = ("name", "query", "formatter")
    autocomplete_fields = ("query", "formatter")
    filter_horizontal = ("notify_to",)

    @button(visible=lambda o, r: "change" in r.path)
    def execute(self, request, pk):
        obj: Report = self.get_object(request, pk)
        try:
            obj.execute()
        except Exception as e:
            self.message_user(request, f"{e.__class__.__name__}: {e}", messages.ERROR)

    @button(visible=lambda o, r: "change" in r.path)
    def view(self, request, pk):
        try:
            obj = self.get_object(request, pk)
            data = pickle.loads(obj.result)
            return HttpResponse(data)
        except Exception as e:
            self.message_user(request, f"{e.__class__.__name__}: {e}", messages.ERROR)
