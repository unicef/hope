import xlrd
from admin_extra_urls.extras import link, ExtraUrlMixin
from adminfilters.filters import ChoicesFieldComboFilter, RelatedFieldComboFilter
from django.contrib import admin
from django.contrib.messages import ERROR
from django.core.exceptions import ValidationError, PermissionDenied
from django.forms import forms
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.utils.html import format_html
from mptt.admin import MPTTModelAdmin
from xlrd import XLRDError

from hct_mis_api.apps.core.airflow_api import AirflowApi
from hct_mis_api.apps.core.models import (
    BusinessArea,
    FlexibleAttribute,
    FlexibleAttributeChoice,
    FlexibleAttributeGroup,
    XLSXKoboTemplate,
)
from hct_mis_api.apps.core.validators import KoboTemplateValidator


class XLSImportForm(forms.Form):
    xls_file = forms.FileField()


@admin.register(BusinessArea)
class BusinessAreaAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "has_data_sharing_agreement", "rapidpro_is_enabled", "kobo_is_enabled")
    search_fields = ("name",)
    list_filter = ("has_data_sharing_agreement",)

    def rapidpro_is_enabled(self, obj):
        return bool(obj.rapid_pro_api_key)

    rapidpro_is_enabled.boolean = True

    def kobo_is_enabled(self, obj):
        return bool(obj.kobo_token)

    kobo_is_enabled.boolean = True


@admin.register(FlexibleAttribute)
class FlexibleAttributeAdmin(admin.ModelAdmin):
    list_display = ("name", "type", "required", "is_removed")
    list_filter = (("type", ChoicesFieldComboFilter),
                   ("group", RelatedFieldComboFilter),
                   "required", "associated_with", "is_removed")
    search_fields = ("name",)
    ordering = ("name",)


@admin.register(FlexibleAttributeGroup)
class FlexibleAttributeGroupAdmin(MPTTModelAdmin):
    list_display = ("name", "required", "repeatable", "is_removed")
    list_filter = ("required", "repeatable", "is_removed")
    search_fields = ("name",)
    ordering = ("name",)


@admin.register(FlexibleAttributeChoice)
class FlexibleAttributeChoiceAdmin(admin.ModelAdmin):
    list_display = ('list_name', 'name',)
    search_fields = ('name',)
    filter_horizontal = ('flex_attributes',)
    ordering = ('list_name',)


@admin.register(XLSXKoboTemplate)
class XLSXKoboTemplateAdmin(ExtraUrlMixin, admin.ModelAdmin):
    list_display = ("original_file_name", "uploaded_by", "created_at", "file", "import_status")

    exclude = ("is_removed", "file_name", "status", "template_id")

    readonly_fields = ("original_file_name", "uploaded_by", "file", "import_status", "error_description")

    def import_status(self, obj):
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

    def original_file_name(self, obj):
        return obj.file_name

    def get_form(self, request, obj=None, change=False, **kwargs):
        if obj is None:
            return XLSImportForm
        return super().get_form(request, obj, change, **kwargs)

    @link()
    def download_last_valid_file(self, request):
        latest_valid_import = self.model.objects.latest_valid()
        if latest_valid_import:
            return redirect(latest_valid_import.file.url)
        self.message_user(
            request,
            "There is no valid file to download",
            level=ERROR,
        )

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
                    status=XLSXKoboTemplate.PROCESSING,
                )
                self.message_user(
                    request,
                    "Core field validation successful, running KoBo Template upload task..., "
                    "Import status will change after task completion",
                )
                AirflowApi.start_dag(
                    dag_id="UploadNewKoboTemplateAndUpdateFlexFields",
                    context={"xlsx_kobo_template_id": str(xlsx_kobo_template_object.id)},
                )
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
