import logging

import xlrd
from admin_extra_urls.api import ExtraUrlMixin, action
from adminfilters.filters import TextFieldFilter, ForeignKeyFieldFilter
from django.contrib import admin, messages
from django.contrib.messages import ERROR
from django.core.exceptions import ValidationError, PermissionDenied
from django.forms import forms
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.utils.html import format_html
from xlrd import XLRDError

from hct_mis_api.apps.core.airflow_api import AirflowApi
from hct_mis_api.apps.core.models import (
    BusinessArea,
    FlexibleAttribute,
    FlexibleAttributeChoice,
    FlexibleAttributeGroup,
    XLSXKoboTemplate,
    AdminArea,
    AdminAreaLevel,
)
from hct_mis_api.apps.core.validators import KoboTemplateValidator

logger = logging.getLogger(__name__)


class XLSImportForm(forms.Form):
    xls_file = forms.FileField()


@admin.register(BusinessArea)
class BusinessAreaAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")


@admin.register(AdminArea)
class AdminAreaAdmin(admin.ModelAdmin):
    list_display = ("title", "parent")


@admin.register(AdminAreaLevel)
class AdminAreaAdmin(admin.ModelAdmin):
    list_display = ("name", "business_area")


@admin.register(FlexibleAttribute)
class FlexibleAttributeAdmin(admin.ModelAdmin):
    pass


@admin.register(FlexibleAttributeGroup)
class FlexibleAttributeGroupAdmin(admin.ModelAdmin):
    pass


@admin.register(FlexibleAttributeChoice)
class FlexibleAttributeChoiceAdmin(admin.ModelAdmin):
    pass


@admin.register(XLSXKoboTemplate)
class XLSXKoboTemplateAdmin(ExtraUrlMixin, admin.ModelAdmin):
    list_display = ("original_file_name", "uploaded_by", "created_at", "file", "_status")

    exclude = ("is_removed", "file_name", "status", "template_id")
    readonly_fields = ("original_file_name", "uploaded_by", "file", "_status", "error_description")
    list_filter = (
        "status",
        ForeignKeyFieldFilter.factory("uploaded_by_username__istartswith", "Uploaded By"),
    )
    search_fields = ("file_name",)
    date_hierarchy = "created_at"
    ordering = ("-created_at",)

    COLORS = {
        XLSXKoboTemplate.SUCCESSFUL: "89eb34",
        XLSXKoboTemplate.UNSUCCESSFUL: "e30b0b",
        XLSXKoboTemplate.PROCESSING: "7a807b",
        XLSXKoboTemplate.UPLOADED: "FFAE19",
    }

    def _status(self, obj):
        return format_html(
            '<span style="color: #{};">{}</span>',
            self.COLORS[obj.status],
            obj.status,
        )

    def original_file_name(self, obj):
        return obj.file_name

    def get_form(self, request, obj=None, change=False, **kwargs):
        if obj is None:
            return XLSImportForm
        return super().get_form(request, obj, change, **kwargs)

    @action()
    def download_last_valid_file(self, request):
        latest_valid_import = self.model.objects.latest_valid()
        if latest_valid_import:
            return redirect(latest_valid_import.file.url)
        self.message_user(
            request,
            "There is no valid file to download",
            level=ERROR,
        )

    @action(visible=lambda o: o and o.status == XLSXKoboTemplate.UPLOADED)
    def post_to_kobo(self, request, pk, obj=None):
        if obj is None:
            obj = self.get_object(request, pk)
        try:
            AirflowApi.start_dag(
                dag_id="UploadNewKoboTemplateAndUpdateFlexFields",
                context={"xlsx_kobo_template_id": str(obj.id)},
            )
            obj.status = XLSXKoboTemplate.PROCESSING
            obj.save()
            self.message_user(
                request,
                "Running KoBo Template upload task..., " "Import status will change after task completion",
            )
        except Exception as e:
            logger.exception(e)
            self.message_user(request, str(e), messages.ERROR)

    def add_view(self, request, form_url="", extra_context=None):
        if not self.has_add_permission(request):
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
                form.add_error("xls_file", validation_error)
            except XLRDError as file_error:
                form.add_error("xls_file", file_error)

            if form.is_valid():
                xlsx_kobo_template_object = XLSXKoboTemplate.objects.create(
                    file_name=xls_file.name,
                    uploaded_by=request.user,
                    file=xls_file,
                    status=XLSXKoboTemplate.UPLOADED,
                )
                self.message_user(request, "Core field validation successful. File uploaded")
                self.post_to_kobo(request, pk=xlsx_kobo_template_object.pk, obj=xlsx_kobo_template_object)

                return redirect("..")
        else:
            payload["form"] = form_class()

        return TemplateResponse(request, "core/xls_form.html", payload)

    def change_view(self, request, object_id=None, form_url="", extra_context=None):
        extra_context = dict(show_save=False, show_save_and_continue=False, show_delete=True)
        has_add_permission = self.has_add_permission
        self.has_add_permission = lambda __: False
        template_response = super().change_view(request, object_id, form_url, extra_context)
        self.has_add_permission = has_add_permission

        return template_response
