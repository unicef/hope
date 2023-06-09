import logging
from typing import TYPE_CHECKING, Any, Dict, Optional, Sequence

from django import forms
from django.conf import settings
from django.contrib import messages
from django.contrib.admin import register
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
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

from hct_mis_api.apps.power_query.defaults import SYSTEM_PARAMETRIZER
from hct_mis_api.apps.power_query.forms import FormatterTestForm
from hct_mis_api.apps.power_query.models import (
    CeleryEnabled,
    Dataset,
    Formatter,
    Parametrizer,
    Query,
    Report,
    ReportDocument,
)
from hct_mis_api.apps.power_query.utils import to_dataset
from hct_mis_api.apps.power_query.widget import FormatterEditor
from hct_mis_api.apps.steficon.widget import PythonEditor
from hct_mis_api.apps.utils.admin import HOPEModelAdminBase

if TYPE_CHECKING:
    from uuid import UUID

    from django.contrib.admin.options import _ModelT

logger = logging.getLogger(__name__)


class QueryResource(resources.ModelResource):
    class Meta:
        model = Query
        fields = ("name", "description", "target", "code", "info")
        import_id_fields = ("name",)

    def dehydrate_target(self, obj: Any) -> str:
        return f"{obj.target.app_label}.{obj.target.model}"

    def before_import_row(self, row: Dict, row_number: Optional[int] = None, **kwargs: Any) -> Dict:
        ct = row.get("target")
        app_label, model_name = ct.split(".")
        try:
            row["target"] = ContentType.objects.get(app_label=app_label, model=model_name).pk
        except ContentType.DoesNotExist:
            pass
        return row


class CeleryEnabledMixin:
    def get_readonly_fields(self, request: HttpRequest, obj: Optional["_ModelT"] = None) -> Sequence[str]:
        ret = list(super().get_readonly_fields(request, obj))
        ret.append("celery_task")
        return ret

    @button(visible=settings.DEBUG)
    def check_status(self: HOPEModelAdminBase, request: HttpRequest) -> HttpResponse:  # type: ignore
        obj: CeleryEnabled
        for obj in self.get_queryset(request):
            if obj.async_result is None:
                obj.celery_task = None
                obj.save()

    @button(visible=settings.DEBUG)
    def monitor(self: HOPEModelAdminBase, request: HttpRequest) -> HttpResponse:
        ctx = self.get_common_context(request, title="Celery Monitor")
        ctx["flower_address"] = settings.FLOWER_ADDRESS
        ctx["queries"] = Query.objects.all()
        ctx["reports"] = Report.objects.all()
        return render(request, f"admin/power_query/{self.model._meta.model_name}/monitor.html", ctx)

    @button()
    def queue(self: HOPEModelAdminBase, request: HttpRequest, pk: int) -> HttpResponse:  # type: ignore
        obj: CeleryEnabled
        try:
            if not (obj := self.get_object(request, str(pk))):  # type: ignore
                raise Exception("Target not found")
            obj.queue()
            self.message_user(request, f"Run scheduled: {obj.celery_task}")
        except Exception as e:
            self.message_user(request, f"{e.__class__.__name__}: {e}", messages.ERROR)


@register(Query)
class QueryAdmin(LinkedObjectsMixin, HOPEModelAdminBase):
    list_display = ("name", "target", "owner", "active", "success")
    search_fields = ("name",)
    list_filter = (
        ("target", AutoCompleteFilter),
        ("owner", AutoCompleteFilter),
        "active",
        "last_run",
    )
    autocomplete_fields = ("target", "owner")
    readonly_fields = ("sentry_error_id", "error_message", "info")
    change_form_template = None
    resource_class = QueryResource

    def success(self, obj: Query) -> bool:
        return not bool(obj.error_message)

    success.boolean = True

    def formfield_for_dbfield(self, db_field: Any, request: HttpRequest, **kwargs: Any) -> Optional[forms.fields.Field]:
        if db_field.name == "code":
            kwargs = {"widget": PythonEditor}
        elif db_field.name == "description":
            kwargs = {"widget": forms.Textarea(attrs={"rows": 2, "style": "width:80%"})}
        elif db_field.name == "owner":
            kwargs = {"widget": forms.HiddenInput}

        return super().formfield_for_dbfield(db_field, request, **kwargs)

    def has_change_permission(self, request: HttpRequest, obj: Optional[Any] = None) -> bool:
        return request.user.is_superuser or bool(obj and obj.owner == request.user)

    @button()
    def datasets(self, request: HttpRequest, pk: "UUID") -> HttpResponseRedirect:  # type: ignore
        obj = self.get_object(request, str(pk))
        try:
            url = reverse("admin:power_query_dataset_changelist")
            return HttpResponseRedirect(f"{url}?query__exact={obj.pk}")
        except Exception as e:
            self.message_user(request, f"{e.__class__.__name__}: {e}", messages.ERROR)

    @button(visible=settings.DEBUG)
    def run(self, request: HttpRequest, pk: int) -> HttpResponse:
        ctx = self.get_common_context(request, pk, title="Run results")
        if not (query := self.get_object(request, str(pk))):
            raise Exception("Query not found")
        results = query.execute_matrix(persist=True)
        self.message_user(request, "Done", messages.SUCCESS)
        ctx["results"] = results
        return render(request, "admin/power_query/query/run_result.html", ctx)

    @button()
    def preview(self, request: HttpRequest, pk: "UUID") -> HttpResponse:  # type: ignore
        obj: Query
        if not (obj := self.get_object(request, str(pk))):  # type: ignore
            raise Exception("Query not found")
        try:
            context = self.get_common_context(request, pk, title="Results")
            if obj.parametrizer:
                args = obj.parametrizer.get_matrix()[0]
            else:
                args = {}
            ret, extra = obj.run(False, args, use_existing=True)
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

    def get_changeform_initial_data(self, request: HttpRequest) -> Dict[str, Any]:
        ct = ContentType.objects.filter(id=request.GET.get("ct", 0)).first()
        return {"code": "result=conn.all()", "name": ct, "target": ct, "owner": request.user}


@register(Dataset)
class DatasetAdmin(HOPEModelAdminBase):
    search_fields = ("query__name",)
    list_display = ("query", "last_run", "dataset_type", "target_type", "size", "arguments")
    list_filter = (
        ("query__target", AutoCompleteFilter),
        ("query", AutoCompleteFilter),
        "last_run",
    )
    change_form_template = None
    readonly_fields = ("last_run", "query", "info")
    date_hierarchy = "last_run"

    def get_queryset(self, request: HttpRequest):  # type: ignore[no-untyped-def]
        return super().get_queryset(request).defer("extra", "value")

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False

    def arguments(self, obj: Any) -> str:
        return obj.info.get("arguments")

    def dataset_type(self, obj: Any) -> str:
        return obj.info.get("type")

    def target_type(self, obj: Any) -> str:
        return obj.query.target

    @button(visible=lambda btn: "change" in btn.context["request"].path)
    def preview(self, request: HttpRequest, pk: "UUID") -> HttpResponse:  # type: ignore
        obj = self.get_object(request, str(pk))
        try:
            context = self.get_common_context(request, pk, title="Results")
            context["dataset"] = to_dataset(obj.data)
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
    def test(self, request: HttpRequest, pk: "UUID") -> HttpResponse:
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
class ReportAdmin(LinkedObjectsMixin, CeleryEnabledMixin, HOPEModelAdminBase):
    list_display = ("name", "formatter", "last_run", "frequence", "owner")
    autocomplete_fields = ("query", "formatter", "owner")
    filter_horizontal = ["limit_access_to"]
    readonly_fields = ("last_run",)
    list_filter = (
        ("owner", AutoCompleteFilter),
        ("query", AutoCompleteFilter),
        ("formatter", AutoCompleteFilter),
        "last_run",
    )
    resource_class = ReportResource
    change_list_template = None
    search_fields = ("name",)

    def has_change_permission(self, request: HttpRequest, obj: Optional[Any] = None) -> bool:
        return request.user.is_superuser or bool(obj and obj.owner == request.user)

    def get_changeform_initial_data(self, request: HttpRequest) -> Dict:
        kwargs: Dict = {"owner": request.user}
        if "q" in request.GET:
            q = Query.objects.get(pk=request.GET["q"])
            kwargs["query"] = q
            kwargs["name"] = f"Report for {q.name}"
            kwargs["notify_to"] = [request.user]
        return kwargs

    # @button()
    # def queue(self, request: HttpRequest, pk: "UUID") -> None:
    #     obj: Report
    #     try:
    #         if not (obj := self.get_object(request, str(pk))):
    #             raise Exception("Report not found")
    #         obj.queue()
    #         self.message_user(request, f"Report scheduled: {obj.celery_task}")
    #     except Exception as e:
    #         self.message_user(request, f"{e.__class__.__name__}: {e}", messages.ERROR)

    @button(visible=lambda btn: "change" in btn.context["request"].path)
    def execute(self, request: HttpRequest, pk: int) -> HttpResponse:  # type: ignore
        obj: Report
        if not (obj := self.get_object(request, str(pk))):  # type: ignore
            raise Exception("Report not found")
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
    def refresh(self, request: HttpRequest) -> HttpResponse:  # type: ignore
        from hct_mis_api.apps.power_query.celery_tasks import refresh_reports

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
    json_enabled = True

    @button()
    def preview(self, request: HttpRequest, pk: "UUID") -> TemplateResponse:
        context = self.get_common_context(request, pk, title="Execution Plan")
        return TemplateResponse(request, "admin/power_query/queryargs/preview.html", context)

    @button(visible=lambda b: b.context["original"].code in SYSTEM_PARAMETRIZER)
    def refresh(self, request: HttpRequest, pk: "UUID") -> HttpResponse:  # type: ignore
        if not (obj := self.get_object(request, str(pk))):
            raise Exception("Parametrizer not found")
        obj.refresh()


@register(ReportDocument)
class ReportDocumentAdmin(LinkedObjectsMixin, HOPEModelAdminBase):
    list_display = ("title", "content_type", "arguments")
    list_filter = (("report", AutoCompleteFilter),)
    filter_horizontal = ("limit_access_to",)
    readonly_fields = ("arguments", "report", "dataset", "content_type")

    def get_queryset(self, request: HttpRequest) -> QuerySet[ReportDocument]:
        return super().get_queryset(request).defer("output")

    def size(self, obj: ReportDocument) -> int:
        return len(obj.output or "")

    @button()
    def view(self, request: HttpRequest, pk: "UUID") -> HttpResponseRedirect:
        if not (obj := self.get_object(request, str(pk))):
            raise Exception("Report document not found")
        url = reverse("power_query:document", args=[obj.report.pk, pk])
        return HttpResponseRedirect(url)

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False
