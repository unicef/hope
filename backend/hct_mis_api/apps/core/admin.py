import xlrd
from datetime import datetime
from admin_extra_urls.extras import link, ExtraUrlMixin, action
from django.contrib import admin, messages
from django.conf.urls import url
from django.contrib.messages import ERROR
from django.core.exceptions import ValidationError, PermissionDenied
from django import forms
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.utils.html import format_html
from django.http import HttpResponseRedirect
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
from hct_mis_api.apps.payment.rapid_pro.api import RapidProAPI


class XLSImportForm(forms.Form):
    xls_file = forms.FileField()


class TestRapidproForm(forms.Form):
    phone_number = forms.CharField(
        label="Phone number",
        required=True,
    )
    flow_name = forms.CharField(label="Name of the test flow", initial="Test", required=True)
    check_result = forms.BooleanField(label="Check result", widget=forms.HiddenInput(), initial=False, required=False)
    # start_flow_at = forms.DateTimeField(widget=forms.HiddenInput(), required=False)
    flow_uuid = forms.CharField(widget=forms.HiddenInput(), required=False)


@admin.register(BusinessArea)
class BusinessAreaAdmin(ExtraUrlMixin, admin.ModelAdmin):
    list_display = ("name", "slug")
    # change_form_template = "core/business_area_changeform.html"

    def get_context(self, request, pk=None, **kwargs):
        opts = self.model._meta
        app_label = opts.app_label
        self.object = None

        context = {
            **self.admin_site.each_context(request),
            **kwargs,
            "opts": opts,
            "app_label": app_label,
        }
        if pk:
            self.object = self.get_object(request, pk)
            context["business_area"] = self.object
            context["title"] = f"Test `{self.object.name}` RapidPRO connection"

        return context

    @action(label="Test RapidPro Connection")
    def _test_rapidpro_connection(self, request, pk):
        context = self.get_context(request, pk)

        if request.method == "GET":
            context["form"] = TestRapidproForm()
            context["flow_started"] = None
            context["flow_uuid"] = ""
            return TemplateResponse(request, "core/test_rapidpro.html", context)
        else:
            form = TestRapidproForm(request.POST)
            print(form)
            if form.is_valid():
                phone_number = form.cleaned_data.get("phone_number", None)
                flow_name = form.cleaned_data.get("flow_name", None)
                context["phone_number"] = phone_number
                context["flow_name"] = flow_name
                api = RapidProAPI(context["business_area"].slug)
                if not form.cleaned_data.get("flow_uuid", None):
                    print('FLOW HAS NOT STARTED SO STARTING')
                    context["start_flow_at"] = datetime.now()
                    error, flow_uuid = api.test_connection_start_flow(flow_name, phone_number)
                    # error, flow_uuid = None, 'sfwefe'
                    context["flow_uuid"] = flow_uuid

                    if error:
                        messages.error(request, error)
                        context["flow_started"] = False
                    else:
                        messages.success(request, "Connection successful")
                        context["flow_started"] = True
                else:
                    print("SHOUD ONLY CHECK RESULTS")
                    start_flow_at = form.cleaned_data.get("start_flow_at")
                    flow_uuid = form.cleaned_data.get("flow_uuid")
                    context['flow_uuid'] = flow_uuid
                    context["flow_started"] = True

                    error, result = api.test_connection_flow_run(flow_uuid, phone_number)
                    # error, result = None, ['dwdw']
                    context["run_result"] = result
                    if error:
                        messages.error(request, error)

                # print(phone_number, flow_name)
                # print(form.cleaned_data.get("check_result"))
            else:
                print("FORM INVALID")
                # api = RapidProAPI(context["business_area"].slug)
                # error = api.test_connection_flow(flow_name, phone_number)
                # if error:
                #     messages.error(request, error)
                # else:
                #     messages.success(request, "Connection successful")
            #     target_population = form.cleaned_data["target_population"]
            #     context["title"] = f"Test results of `{self.object.name}` against `{target_population}`"
            #     context["target_population"] = target_population
            #     elements = []
            #     context["elements"] = elements
            #     entries = context["target_population"].selections.all()[:100]
            #     if entries:
            #         for tp in entries:
            #             value = context["rule"].execute(hh=tp.household)
            #             tp.vulnerability_score = value
            #             elements.append(tp)
            #         self.message_user(request, "%s scores calculated" % len(elements))
            #     else:
            #         self.message_user(request, "No records found", messages.WARNING)
            context["form"] = form
            return TemplateResponse(request, "core/test_rapidpro.html", context)

    # def response_change(self, request, obj):
    #     if "_test_rapidpro_connection" in request.POST:
    #         api = RapidProAPI(obj.slug)
    #         error = api.test_connection_flow()
    #         if error:
    #             messages.error(request, error)
    #         else:
    #             messages.success(request, "Connection successful")
    #         return HttpResponseRedirect(".")
    #     return super().response_change(request, obj)


# class BusinessAreaTestRapidproAdmin(admin.AdminSite):
#     def get_urls(self):
#         urls = super(BusinessAreaTestRapidproAdmin, self).get_urls()
#         custom_urls = [url(r"test-rapidpro$", test_rapidpro_view, name="test_rapidpro")]
#         return urls + custom_urls


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
