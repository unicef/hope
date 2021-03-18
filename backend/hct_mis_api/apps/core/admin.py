import logging

from django import forms
from django.contrib import admin, messages
from django.contrib.messages import ERROR
from django.core.exceptions import PermissionDenied, ValidationError
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.utils.html import format_html

import xlrd
from admin_extra_urls.api import ExtraUrlMixin, button
from xlrd import XLRDError

from hct_mis_api.apps.core.celery_tasks import upload_new_kobo_template_and_update_flex_fields_task
from hct_mis_api.apps.core.models import (
    AdminArea,
    AdminAreaLevel,
    BusinessArea,
    CountryCodeMap,
    FlexibleAttribute,
    FlexibleAttributeChoice,
    FlexibleAttributeGroup,
    XLSXKoboTemplate,
)
from hct_mis_api.apps.core.validators import KoboTemplateValidator
from hct_mis_api.apps.payment.rapid_pro.api import RapidProAPI

logger = logging.getLogger(__name__)


class XLSImportForm(forms.Form):
    xls_file = forms.FileField()


class TestRapidproForm(forms.Form):
    phone_number = forms.CharField(
        label="Phone number",
        required=True,
    )
    flow_name = forms.CharField(label="Name of the test flow", initial="Test", required=True)


@admin.register(BusinessArea)
class BusinessAreaAdmin(ExtraUrlMixin, admin.ModelAdmin):
    list_display = ("name", "slug")

    @button(label="Test RapidPro Connection")
    def _test_rapidpro_connection(self, request, pk):
        context = self.get_common_context(request, pk)
        context["business_area"] = self.object
        context["title"] = f"Test `{self.object.name}` RapidPRO connection"

        api = RapidProAPI(self.object.slug)

        if request.method == "GET":
            phone_number = request.GET.get("phone_number", None)
            flow_uuid = request.GET.get("flow_uuid", None)
            flow_name = request.GET.get("flow_name", None)
            timestamp = request.GET.get("timestamp", None)

            if all([phone_number, flow_uuid, flow_name, timestamp]):
                error, result = api.test_connection_flow_run(flow_uuid, phone_number, timestamp)
                context["run_result"] = result
                context["phone_number"] = phone_number
                context["flow_uuid"] = flow_uuid
                context["flow_name"] = flow_name
                context["timestamp"] = timestamp

                if error:
                    messages.error(request, error)
                else:
                    messages.success(request, "Connection successful")
            else:
                context["form"] = TestRapidproForm()
        else:
            form = TestRapidproForm(request.POST)
            if form.is_valid():
                phone_number = form.cleaned_data["phone_number"]
                flow_name = form.cleaned_data["flow_name"]
                context["phone_number"] = phone_number
                context["flow_name"] = flow_name

                error, response = api.test_connection_start_flow(flow_name, phone_number)
                if response:
                    context["flow_uuid"] = response["flow"]["uuid"]
                    context["flow_status"] = response["status"]
                    context["timestamp"] = response["created_on"]

                if error:
                    messages.error(request, error)
                else:
                    messages.success(request, "Connection successful")

            context["form"] = form

        return TemplateResponse(request, "core/test_rapidpro.html", context)


@admin.register(AdminArea)
class AdminAreaAdmin(admin.ModelAdmin):
    list_display = ("title", "parent")


@admin.register(AdminAreaLevel)
class AdminAreaLevelAdmin(admin.ModelAdmin):
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

    @button()
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
            logger.error("The user did not have permission to do that")
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
                logger.exception(validation_error)
                form.add_error("xls_file", validation_error)
            except XLRDError as file_error:
                logger.exception(file_error)
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
                upload_new_kobo_template_and_update_flex_fields_task.delay(
                    xlsx_kobo_template_id=str(xlsx_kobo_template_object.id)
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


@admin.register(CountryCodeMap)
class CountryCodeMapAdmin(ExtraUrlMixin, admin.ModelAdmin):
    list_display = ("country", "alpha2", "alpha3", "ca_code")
    search_fields = ("country",)

    def alpha2(self, obj):
        return obj.country.countries.alpha2(obj.country.code)

    def alpha3(self, obj):
        return obj.country.countries.alpha3(obj.country.code)
