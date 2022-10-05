import logging
import pickle

from django import forms
from django.conf import settings
from django.contrib import messages
from django.contrib.admin import register
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import QuerySet
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.template.response import TemplateResponse
from django.urls import reverse

import tablib
from admin_extra_buttons.decorators import button
from adminfilters.autocomplete import AutoCompleteFilter
from import_export import fields, resources
from import_export.admin import ImportExportMixin
from import_export.widgets import ForeignKeyWidget
from smart_admin.mixins import LinkedObjectsMixin

from ..steficon.widget import PythonEditor
from ..utils.admin import HOPEModelAdminBase
from .celery_tasks import queue, refresh_reports
from .defaults import SYSTEM_QUERYARGS
from .forms import ExportForm, FormatterTestForm
from .models import Dataset, Formatter, Parametrizer, Query, Report, ReportResult
from .utils import to_dataset
from .widget import FormatterEditor

logger = logging.getLogger(__name__)


class QueryResource(resources.ModelResource):
    class Meta:
        model = Query
        fields = ("name", "description", "target", "code", "info")
        import_id_fields = ("name",)

    def dehydrate_target(self, obj):
        return f"{obj.target.app_label}.{obj.target.model}"

    def before_import_row(self, row, row_number=None, **kwargs):
        ct = row.get("target")
        app_label, model_name = ct.split(".")
        try:
            row["target"] = ContentType.objects.get(app_label=app_label, model=model_name).pk
        except ContentType.DoesNotExist:
            pass
        return row


@register(Query)
class QueryAdmin(LinkedObjectsMixin, HOPEModelAdminBase):
    list_display = ("name", "target", "description", "owner")
    search_fields = ("name",)
    list_filter = (
        ("target", AutoCompleteFilter),
        ("owner", AutoCompleteFilter),
    )
    autocomplete_fields = ("target", "owner")
    readonly_fields = ("error", "info")
    change_form_template = None
    resource_class = QueryResource

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name == "code":
            kwargs = {"widget": PythonEditor}
        elif db_field.name == "description":
            kwargs = {"widget": forms.Textarea(attrs={"rows": 2, "style": "width:80%"})}
        elif db_field.name == "owner":
            kwargs = {"widget": forms.HiddenInput}

        return super(QueryAdmin, self).formfield_for_dbfield(db_field, request, **kwargs)

    def get_readonly_fields(self, request, obj=None):
        return super().get_readonly_fields(request, obj)

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser or (obj and obj.owner == request.user)

    def status(self, obj):
        return obj.ready and not obj.error

    status.boolean = True

    def is_ready(self, obj):
        return obj.ready

    is_ready.boolean = True

    # @button(visible=lambda btn: "/change" in btn.context["request"].path)
    # def create_report(self, request, pk):
    #     obj = self.get_object(request, pk)
    #     url = reverse("admin:power_query_report_add")
    #     return HttpResponseRedirect(f"{url}?q={obj.pk}")
    #
    # @button(visible=lambda btn: btn.context["original"].ready and "/change" in btn.context["request"].path)
    # def result(self, request, pk):
    #     obj = self.get_object(request, pk)
    #     try:
    #         url = reverse("admin:power_query_dataset_change", args=[obj.dataset.pk])
    #         return HttpResponseRedirect(url)
    #     except Exception as e:
    #         self.message_user(request, f"{e.__class__.__name__}: {e}", messages.ERROR)
    #
    @button(visible=settings.DEBUG)
    def run(self, request, pk):
        query: Query = self.get_object(request, pk)
        result = query.execute_matrix(persist=True)
        self.message_user(request, f"{result}", messages.SUCCESS)

    @button()
    def queue(self, request, pk):
        try:
            queue.delay(pk)
            self.message_user(request, "Query scheduled")
        except Exception as e:
            self.message_user(request, f"{e.__class__.__name__}: {e}", messages.ERROR)

    @button(visible=lambda btn: btn.context["original"].ready and "/change" in btn.context["request"].path)
    def preview(self, request, pk):
        obj: Query = self.get_object(request, pk)
        try:
            context = self.get_common_context(request, pk, title="Results")
            ret, info = obj.execute(persist=False)
            context["type"] = type(ret).__name__
            context["raw"] = ret
            context["info"] = info
            context["title"] = f"Result of {obj.name} ({type(ret).__name__})"
            if isinstance(ret, QuerySet):
                ret = ret[:100]
                context["queryset"] = ret
            elif isinstance(ret, tablib.Dataset):
                context["dataset"] = ret[:100]
            elif isinstance(ret, (dict, list, tuple)):
                context["result"] = ret[:100]
            else:
                self.message_user(request, f"Query does not returns a valid result. It returned {type(ret)}")
            return render(request, "admin/power_query/query/preview.html", context)
        except Exception as e:
            self.message_user(request, f"{e.__class__.__name__}: {e}", messages.ERROR)

    def get_changeform_initial_data(self, request):
        ct = ContentType.objects.filter(id=request.GET.get("ct", 0)).first()
        return {"code": "result=conn.all()", "name": ct, "target": ct, "owner": request.user}


@register(Dataset)
class DatasetAdmin(HOPEModelAdminBase):
    search_fields = ("query__name",)
    list_display = ("query", "last_run", "dataset_type", "target_type", "size", "arguments")
    list_filter = (
        ("query__target", AutoCompleteFilter),
        ("query", AutoCompleteFilter),
    )
    change_form_template = None
    readonly_fields = ("last_run", "query", "info")
    date_hierarchy = "last_run"

    def has_add_permission(self, request):
        return False

    def arguments(self, obj):
        return obj.info.get("arguments")

    def dataset_type(self, obj):
        return obj.info.get("type")

    def target_type(self, obj):
        return obj.query.target

    @button(visible=lambda btn: "change" in btn.context["request"].path)
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
                    if formatter.content_type == "xls":
                        response = HttpResponse(output, content_type=formatter.content_type)
                        response["Content-Disposition"] = "attachment; filename=Dataset Report.xls"
                        return response
                    return HttpResponse(output)
            else:
                context["extra_buttons"] = ""
                form = ExportForm()
            context["form"] = form
            return render(request, "admin/power_query/dataset/export.html", context)
        except Exception as e:
            logger.exception(e)
            self.message_user(request, f"{e.__class__.__name__}: {e}", messages.ERROR)

    @button(visible=lambda btn: "change" in btn.context["request"].path)
    def preview(self, request, pk):
        obj = self.get_object(request, pk)
        try:
            context = self.get_common_context(request, pk, title="Results")
            data = pickle.loads(obj.result)
            context["dataset"] = to_dataset(data)
            return render(request, "admin/power_query/query/preview.html", context)
        except Exception as e:
            logger.exception(e)
            self.message_user(request, f"{e.__class__.__name__}: {e}", messages.ERROR)


class FormatterResource(resources.ModelResource):
    class Meta:
        model = Report
        fields = ("name", "content_type", "code")
        import_id_fields = ("name",)


@register(Formatter)
class FormatterAdmin(ImportExportMixin, HOPEModelAdminBase):
    list_display = ("name", "content_type")
    search_fields = ("name",)
    list_filter = ("content_type",)
    resource_class = FormatterResource
    change_form_template = None

    formfield_overrides = {
        models.TextField: {"widget": FormatterEditor(theme="abcdef")},
    }

    @button(visible=lambda btn: "change" in btn.context["request"].path)
    def test(self, request, pk):
        context = self.get_common_context(request, pk)
        form = FormatterTestForm()
        try:
            if request.method == "POST":
                form = FormatterTestForm(request.POST)
                if form.is_valid():
                    obj: Formatter = context["original"]
                    ctx = {
                        "dataset": form.cleaned_data["query"].dataset,
                        "report": "None",
                    }
                    if obj.content_type == "xls":
                        output = obj.render(ctx)
                        response = HttpResponse(output, content_type=obj.content_type)
                        response["Content-Disposition"] = "attachment; filename=Report.xls"
                        return response
                    else:
                        context["results"] = str(obj.render(ctx))
                else:
                    form = FormatterTestForm()
        except Exception as e:
            self.message_user(request, f"{e.__class__.__name__}: {e}", messages.ERROR)
        context["form"] = form
        return render(request, "admin/power_query/formatter/test.html", context)


class ReportResource(resources.ModelResource):
    query = fields.Field(widget=ForeignKeyWidget(Query, "name"))
    formatter = fields.Field(widget=ForeignKeyWidget(Formatter, "name"))

    class Meta:
        model = Report
        fields = ("name", "query", "formatter")
        import_id_fields = ("name",)


@register(Report)
class ReportAdmin(LinkedObjectsMixin, HOPEModelAdminBase):
    list_display = ("name", "query", "formatter", "last_run")
    autocomplete_fields = ("query", "formatter")
    filter_horizontal = ("limit_access_to",)
    readonly_fields = ("last_run",)
    list_filter = (("query", AutoCompleteFilter), ("formatter", AutoCompleteFilter))
    resource_class = ReportResource
    change_list_template = None
    search_fields = ("name",)

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser or (obj and obj.owner == request.user)

    def get_changeform_initial_data(self, request):
        kwargs = {"owner": request.user}
        if "q" in request.GET:
            q = Query.objects.get(pk=request.GET["q"])
            kwargs["query"] = q
            kwargs["name"] = f"Report for {q.name}"
            kwargs["notify_to"] = [request.user]
        return kwargs

    @button(visible=lambda btn: "change" in btn.context["request"].path)
    def execute(self, request, pk):
        obj: Report = self.get_object(request, pk)
        try:
            result = obj.execute()
            self.message_user(request, f"{result}")
        except Exception as e:
            logger.exception(e)
            self.message_user(request, f"{e.__class__.__name__}: {e}", messages.ERROR)

    @button(visible=lambda btn: btn.path.endswith("/power_query/report/"))
    def refresh(self, request):
        try:
            refresh_reports.delay()
            self.message_user(request, "Reports refresh queued", messages.SUCCESS)
        except Exception as e:
            self.message_user(request, f"{e.__class__.__name__}: {e}", messages.ERROR)


@register(Parametrizer)
class QueryArgsAdmin(LinkedObjectsMixin, HOPEModelAdminBase):
    list_display = ("name", "code", "system")
    list_filter = ("system",)
    search_fields = ("name", "code")

    @button()
    def preview(self, request, pk):
        context = self.get_common_context(request, pk, title="Execution Plan")
        return TemplateResponse(request, "admin/power_query/queryargs/preview.html", context)

    @button(visible=lambda b: b.context["original"].system)
    def refresh(self, request, pk):
        obj = self.get_object(request, pk)
        obj.value = SYSTEM_QUERYARGS[obj.code]["value"]()
        obj.save()


@register(ReportResult)
class ReportResultAdmin(LinkedObjectsMixin, HOPEModelAdminBase):
    list_display = ("title", "report", "info", "size")
    list_filter = (("report", AutoCompleteFilter),)

    def info(self, obj: ReportResult):
        return obj.dataset.info

    def size(self, obj: ReportResult):
        return len(obj.output or "")

    @button()
    def view(self, request, pk):
        url = reverse("power_query:report", args=[pk])
        return HttpResponseRedirect(url)
