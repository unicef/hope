import xlrd
from django.contrib import admin
from django.core.exceptions import ValidationError, PermissionDenied
from django.db import transaction
from django.forms import forms
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from xlrd import XLRDError

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
    list_display = ("name", "slug")


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
class XLSXKoboTemplateAdmin(admin.ModelAdmin):
    def get_form(self, request, obj=None, change=False, **kwargs):
        if obj is None:
            return XLSImportForm
        return super().get_form(request, obj, change, **kwargs)

    @transaction.atomic
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
                # if file_differences:
                #     form.add_error()
                # validation_results = validate_kobo_template(
                #     survey_sheet=sheets["survey"], choices_sheet=sheets["choices"]
                # )
                # self.send_to_kobo
                # flex_field_update
                # self._handle_choices(sheets)
                # self._handle_fields(sheets["survey"])
            except ValidationError as validation_error:
                form.add_error("xls_file", validation_error)
                transaction.set_rollback(True)
            except XLRDError as file_error:
                form.add_error("xls_file", file_error)
                transaction.set_rollback(True)

            if form.is_valid():
                self.message_user(request, "Your xls file has been imported, ")
                return redirect("..")
        else:
            payload["form"] = form_class()

        return TemplateResponse(request, "core/xls_form.html", payload)
