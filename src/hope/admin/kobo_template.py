import logging
from typing import TYPE_CHECKING, Any, Callable

from admin_extra_buttons.api import button
from adminfilters.autocomplete import AutoCompleteFilter
from django import forms
from django.contrib import admin
from django.contrib.messages import ERROR
from django.core.exceptions import PermissionDenied, ValidationError
from django.http import (
    HttpRequest,
    HttpResponse,
    HttpResponsePermanentRedirect,
    HttpResponseRedirect,
)
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.utils.html import format_html
import xlrd
from xlrd import XLRDError

from hope.admin.utils import HOPEModelAdminBase, SoftDeletableAdminMixin
from hope.apps.core.celery_tasks import (
    upload_new_kobo_template_and_update_flex_fields_task,
)
from hope.apps.core.models import XLSXKoboTemplate
from hope.apps.core.validators import KoboTemplateValidator

if TYPE_CHECKING:
    from uuid import UUID


logger = logging.getLogger(__name__)


class XLSImportForm(forms.Form):
    xls_file = forms.FileField()


@admin.register(XLSXKoboTemplate)
class XLSXKoboTemplateAdmin(SoftDeletableAdminMixin, HOPEModelAdminBase):
    list_display = ("file_name", "uploaded_by", "created_at", "file", "import_status")
    list_filter = (
        "status",
        ("uploaded_by", AutoCompleteFilter),
    )
    search_fields = ("file_name",)
    date_hierarchy = "created_at"
    exclude = ("is_removed", "file_name", "status", "template_id")
    readonly_fields = (
        "file_name",
        "uploaded_by",
        "file",
        "import_status",
        "error_description",
        "first_connection_failed_time",
    )

    def import_status(self, obj: Any) -> str:
        if obj.status == self.model.SUCCESSFUL:
            color = "89eb34"
        elif obj.status == self.model.UNSUCCESSFUL:
            color = "e30b0b"
        else:
            color = "7a807b"

        return format_html(
            '<span style="color: #{};">{}</span>',
            color,
            obj.status,
        )

    def get_form(
        self,
        request: HttpRequest,
        obj: Any | None = None,
        change: bool = False,
        **kwargs: Any,
    ) -> Any:
        if obj is None:
            return XLSImportForm
        return super().get_form(request, obj, change, **kwargs)

    @button(permission="core.download_last_valid_file")
    def download_last_valid_file(
        self, request: HttpRequest
    ) -> HttpResponseRedirect | HttpResponsePermanentRedirect | None:
        latest_valid_import = self.model.objects.latest_valid()
        if latest_valid_import:
            return redirect(latest_valid_import.file.url)
        self.message_user(
            request,
            "There is no valid file to download",
            level=ERROR,
        )
        return None

    @button(
        label="Rerun KOBO Import",
        visible=lambda btn: btn.original is not None and btn.original.status != XLSXKoboTemplate.SUCCESSFUL,
        permission="core.rerun_kobo_import",
    )
    def rerun_kobo_import(self, request: HttpRequest, pk: "UUID") -> HttpResponsePermanentRedirect:
        xlsx_kobo_template_object = get_object_or_404(XLSXKoboTemplate, pk=pk)
        upload_new_kobo_template_and_update_flex_fields_task.run(
            xlsx_kobo_template_id=str(xlsx_kobo_template_object.id)
        )
        return redirect(".")

    def add_view(
        self,
        request: HttpRequest,
        form_url: str = "",
        extra_context: dict | None = None,
    ) -> HttpResponsePermanentRedirect | TemplateResponse:
        if not self.has_add_permission(request):
            logger.warning("The user did not have permission to do that")
            raise PermissionDenied

        opts = self.model._meta
        app_label = opts.app_label

        context = {
            **self.admin_site.each_context(request),
            "opts": opts,
            "app_label": app_label,
            "has_file_field": True,
        }
        form_class = self.get_form(request)
        payload = {**context}

        if request.method == "POST":
            form = form_class(request.POST, request.FILES)
            payload["form"] = form
            xls_file = request.FILES["xls_file"]

            try:
                wb = xlrd.open_workbook(file_contents=xls_file.read())
                sheets = {
                    "survey_sheet": wb.sheet_by_name("survey"),
                    "choices_sheet": wb.sheet_by_name("choices"),
                }
                validation_errors = KoboTemplateValidator.validate_kobo_template(**sheets)
                if validation_errors:
                    errors = [f"Field: {error['field']} - {error['message']}" for error in validation_errors]
                    form.add_error(field=None, error=errors)
            except ValidationError as validation_error:
                logger.warning(validation_error)
                form.add_error("xls_file", validation_error)
            except XLRDError as file_error:
                logger.warning(file_error)
                form.add_error("xls_file", file_error)

            if form.is_valid():
                xlsx_kobo_template_object = XLSXKoboTemplate.objects.create(
                    file_name=xls_file.name,
                    uploaded_by=request.user,
                    file=xls_file,
                    status=XLSXKoboTemplate.UPLOADED,
                )
                self.message_user(
                    request,
                    "Core field validation successful, running KoBo Template upload task..., "
                    "Import status will change after task completion",
                )
                upload_new_kobo_template_and_update_flex_fields_task.run(
                    xlsx_kobo_template_id=str(xlsx_kobo_template_object.id)
                )
                return redirect("..")
        else:
            payload["form"] = form_class()

        return TemplateResponse(request, "core/xls_form.html", payload)

    def change_view(
        self,
        request: HttpRequest,
        object_id: str,
        form_url: str = "",
        extra_context: dict[str, Any] | None = None,
    ) -> HttpResponse:
        extra_context = {
            "show_save": False,
            "show_save_and_continue": False,
            "show_delete": True,
        }
        has_add_permission: Callable = self.has_add_permission
        self.has_add_permission: Callable = lambda __: False
        template_response = super().change_view(request, object_id, form_url, extra_context)
        self.has_add_permission = has_add_permission

        return template_response
