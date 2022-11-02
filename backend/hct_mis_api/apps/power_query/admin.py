import logging
from typing import Any, Dict, Optional

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
from .celery_tasks import refresh_reports, run_background_query
from .defaults import SYSTEM_PARAMETRIZER
from .forms import FormatterTestForm
from .models import Dataset, Formatter, Parametrizer, Query, Report, ReportDocument
from .utils import to_dataset
from .widget import FormatterEditor

logger = logging.getLogger(__name__)


class QueryResource(resources.ModelResource):
    class Meta:
        model = Query
        fields = ("name", "description", "target", "code", "info")
        import_id_fields = ("name",)

    def dehydrate_target(self, obj) -> str:
        return f"{obj.target.app_label}.{obj.target.model}"

    def before_import_row(self, row, row_number=None, **kwargs) -> None:
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
    readonly_fields = ("sentry_error_id", "error_message", "info")
    change_form_template = None
    resource_class = QueryResource

    def formfield_for_dbfield(self, db_field, request, **kwargs) -> Optional[forms.fields.Field]:
        if db_field.name == "code":
            kwargs = {"widget": PythonEditor}
        elif db_field.name == "description":
            kwargs = {"widget": forms.Textarea(attrs={"rows": 2, "style": "width:80%"})}
        elif db_field.name == "owner":
            kwargs = {"widget": forms.HiddenInput}

        return super(QueryAdmin, self).formfield_for_dbfield(db_field, request, **kwargs)

    def has_change_permission(self, request, obj=None) -> bool:
        return request.user.is_superuser or (obj and obj.owner == request.user)

    @button()
    def datasets(self, request, pk) -> Optional[HttpResponseRedirect]:
        obj = self.get_object(request, pk)
        try:
            url = reverse("admin:power_query_dataset_changelist")
            return HttpResponseRedirect(f"{url}?query__exact={obj.pk}")
        except Exception as e:
            self.message_user(request, f"{e.__class__.__name__}: {e}", messages.ERROR)
        return None

    @button(visible=settings.DEBUG)
    def run(self, request, pk) -> HttpResponse:
        ctx = self.get_common_context(request, pk, title="Run results")
        if not (query := self.get_object(request, pk)):
            raise Exception("Query not found")
        results = query.execute_matrix(persist=True)
        self.message_user(request, "Done", messages.SUCCESS)
        ctx["results"] = results
        return render(request, "admin/power_query/query/run_result.html", ctx)

    @button()
    def queue(self, request, pk) -> None:
        try:
            run_background_query.delay(pk)
            self.message_user(request, "Query scheduled")
        except Exception as e:
            self.message_user(request, f"{e.__class__.__name__}: {e}", messages.ERROR)

    @button()
    def preview(self, request, pk) -> Optional[HttpResponse]:
        obj: Query = self.get_object(request, pk)
        try:
            context = self.get_common_context(request, pk, title="Results")
            if obj.parametrizer:
                args = obj.parametrizer.get_matrix()[0]
            else:
                args = {}
            ret, extra = obj.run(False, args)
            context["type"] = type(ret).__name__
            context["raw"] = ret
            context["info"] = extra
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
        return None

    def get_changeform_initial_data(self, request) -> Dict[str, Any]:
        ct = ContentType.objects.filter(id=request.GET.get("ct", 0)).first()
        return {"code": "result=conn.all()", "name": ct, "target": ct, "owner": request.user}


@register(Dataset)
class DatasetAdmin(HOPEModelAdminBase):
    search_fields = ("query__name",)
    list_display = ("query", "id", "last_run", "dataset_type", "target_type", "size", "arguments")
    list_filter = (
        ("query__target", AutoCompleteFilter),
        ("query", AutoCompleteFilter),
    )
    change_form_template = None
    readonly_fields = ("last_run", "query", "info")
    date_hierarchy = "last_run"

    def has_add_permission(self, request) -> bool:
        return False

    def arguments(self, obj) -> str:
        return obj.info.get("arguments")

    def dataset_type(self, obj) -> str:
        return obj.info.get("type")

    def target_type(self, obj) -> str:
        return obj.query.target

    @button(visible=lambda btn: "change" in btn.context["request"].path)
    def preview(self, request, pk) -> Optional[HttpResponse]:
        obj = self.get_object(request, pk)
        try:
            context = self.get_common_context(request, pk, title="Results")
            context["dataset"] = to_dataset(obj.data)
            return render(request, "admin/power_query/query/preview.html", context)
        except Exception as e:
            logger.exception(e)
            self.message_user(request, f"{e.__class__.__name__}: {e}", messages.ERROR)
        return None


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
    def test(self, request, pk) -> HttpResponse:
        context = self.get_common_context(request, pk)
        form = FormatterTestForm()
        try:
            if request.method == "POST":
                form = FormatterTestForm(request.POST)
                if form.is_valid():
                    obj: Formatter = context["original"]
                    ctx = {
                        "dataset": form.cleaned_data["query"].datasets.first(),
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
            logger.exception(e)
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

    def has_change_permission(self, request, obj=None) -> bool:
        return request.user.is_superuser or (obj and obj.owner == request.user)

    def get_changeform_initial_data(self, request) -> Dict[str, Any]:
        kwargs = {"owner": request.user}
        if "q" in request.GET:
            q = Query.objects.get(pk=request.GET["q"])
            kwargs["query"] = q
            kwargs["name"] = f"Report for {q.name}"
            kwargs["notify_to"] = [request.user]
        return kwargs

    @button(visible=lambda btn: "change" in btn.context["request"].path)
    def execute(self, request, pk) -> None:
        obj: Report = self.get_object(request, pk)
        try:
            result = obj.execute(run_query=True)
            errors = [r[1] for r in result if isinstance(r[1], Exception)]
            if len(errors) == 0:
                message_level = messages.SUCCESS
            elif len(errors) == len(result):
                message_level = messages.ERROR
            else:
                message_level = messages.WARNING
            self.message_user(request, f"{result}", message_level)
        except Exception as e:
            logger.exception(e)
            self.message_user(request, f"{e.__class__.__name__}: {e}", messages.ERROR)

    @button(visible=lambda btn: btn.path.endswith("/power_query/report/"))
    def refresh(self, request) -> None:
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
    def preview(self, request, pk) -> TemplateResponse:
        context = self.get_common_context(request, pk, title="Execution Plan")
        return TemplateResponse(request, "admin/power_query/queryargs/preview.html", context)

    @button(visible=lambda b: b.context["original"].code in SYSTEM_PARAMETRIZER)
    def refresh(self, request, pk) -> None:
        obj: Parametrizer = self.get_object(request, pk)
        obj.refresh()


@register(ReportDocument)
class ReportDocumentAdmin(LinkedObjectsMixin, HOPEModelAdminBase):
    list_display = ("title", "content_type", "arguments", "size")
    list_filter = (("report", AutoCompleteFilter),)
    readonly_fields = ("arguments", "report", "dataset", "content_type")

    def size(self, obj: ReportDocument) -> int:
        return len(obj.output or "")

    @button()
    def view(self, request, pk) -> HttpResponseRedirect:
        url = reverse("power_query:report", args=[pk])
        return HttpResponseRedirect(url)
