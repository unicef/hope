from typing import TYPE_CHECKING, Any

from adminfilters.autocomplete import AutoCompleteFilter
from django.contrib import admin, messages
from django.db import transaction
from django.db.models.query import QuerySet
from django.forms import Form
from django.http import HttpRequest, HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import reverse

from hope.admin.utils import HOPEModelAdminBase
from hope.apps.household.forms import UpdateByXlsxStage1Form, UpdateByXlsxStage2Form
from hope.models.xlsx_update_file import XlsxUpdateFile
from hope.apps.household.services.individual_xlsx_update import (
    IndividualXlsxUpdate,
    InvalidColumnsError,
)

if TYPE_CHECKING:
    from django import forms


@admin.register(XlsxUpdateFile)
class XlsxUpdateFileAdmin(HOPEModelAdminBase):
    readonly_fields = (
        "file",
        "business_area",
        "rdi",
        "xlsx_match_columns",
        "uploaded_by",
        "program",
    )
    list_display = ("file", "business_area", "program", "rdi", "uploaded_by")
    list_filter = (
        ("business_area", AutoCompleteFilter),
        ("rdi", AutoCompleteFilter),
        ("program", AutoCompleteFilter),
        ("uploaded_by", AutoCompleteFilter),
    )
    search_fields = ("file",)

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        return super().get_queryset(request).select_related("business_area", "rdi", "program", "uploaded_by")

    def xlsx_update_stage2(self, request: HttpRequest, old_form: Form) -> TemplateResponse:
        xlsx_update_file = XlsxUpdateFile(
            file=old_form.cleaned_data["file"],
            business_area=old_form.cleaned_data["business_area"],
            rdi=old_form.cleaned_data["registration_data_import"],
            program=old_form.cleaned_data["program"],
            uploaded_by=request.user,
        )
        xlsx_update_file.save()
        try:
            updater = IndividualXlsxUpdate(xlsx_update_file)
        except InvalidColumnsError as e:
            self.message_user(request, str(e), messages.ERROR)
            context = self.get_common_context(
                request,
                title="Update Individual by xlsx",
                form=UpdateByXlsxStage1Form(),
            )
            return TemplateResponse(request, "admin/household/individual/xlsx_update.html", context)

        context = self.get_common_context(
            request,
            title="Update Individual by xlsx",
            form=UpdateByXlsxStage2Form(
                xlsx_columns=updater.columns_names,
                initial={"xlsx_update_file": xlsx_update_file},
            ),
        )
        return TemplateResponse(request, "admin/household/individual/xlsx_update_stage2.html", context)

    def xlsx_update_stage3(self, request: HttpRequest, old_form: Form) -> TemplateResponse:
        xlsx_update_file = old_form.cleaned_data["xlsx_update_file"]
        xlsx_update_file.xlsx_match_columns = old_form.cleaned_data["xlsx_match_columns"]
        xlsx_update_file.save()
        updater = IndividualXlsxUpdate(xlsx_update_file)
        report = updater.get_matching_report()
        context = self.get_common_context(
            request,
            title="Update Individual by xlsx Report",
            unique_report_rows=report[IndividualXlsxUpdate.STATUS_UNIQUE],
            multiple_match_report_rows=report[IndividualXlsxUpdate.STATUS_MULTIPLE_MATCH],
            no_match_report_rows=report[IndividualXlsxUpdate.STATUS_NO_MATCH],
            xlsx_update_file=xlsx_update_file.id,
        )
        return TemplateResponse(request, "admin/household/individual/xlsx_update_stage3.html", context)

    def add_view(
        self,
        request: HttpRequest,
        form_url: str = "",
        extra_context: dict | None = None,
    ) -> Any:
        return self.xlsx_update(request)

    def xlsx_update(self, request: HttpRequest) -> Any:
        form: forms.Form
        if request.method == "GET":
            form = UpdateByXlsxStage1Form()
            context = self.get_common_context(request, title="Update Individual by xlsx", form=form)
        elif request.POST.get("stage") == "2":
            form = UpdateByXlsxStage1Form(request.POST, request.FILES)
            context = self.get_common_context(request, title="Update Individual by xlsx", form=form)
            if form.is_valid():
                try:
                    return self.xlsx_update_stage2(request, form)
                except Exception as e:
                    self.message_user(request, f"{e.__class__.__name__}: {str(e)}", messages.ERROR)
            return TemplateResponse(request, "admin/household/individual/xlsx_update.html", context)

        elif request.POST.get("stage") == "3":
            xlsx_update_file = XlsxUpdateFile.objects.get(pk=request.POST["xlsx_update_file"])
            updater = IndividualXlsxUpdate(xlsx_update_file)
            form = UpdateByXlsxStage2Form(request.POST, request.FILES, xlsx_columns=updater.columns_names)
            context = self.get_common_context(request, title="Update Individual by xlsx", form=form)
            if form.is_valid():
                try:
                    return self.xlsx_update_stage3(request, form)
                except Exception as e:
                    self.message_user(request, f"{e.__class__.__name__}: {str(e)}", messages.ERROR)
            return TemplateResponse(request, "admin/household/individual/xlsx_update_stage2.html", context)

        elif request.POST.get("stage") == "4":
            xlsx_update_file_id = request.POST.get("xlsx_update_file")
            xlsx_update_file = XlsxUpdateFile.objects.get(pk=xlsx_update_file_id)
            updater = IndividualXlsxUpdate(xlsx_update_file)
            try:
                with transaction.atomic():
                    updater.update_individuals()
                self.message_user(request, "Done", messages.SUCCESS)
                return HttpResponseRedirect(reverse("admin:household_individual_changelist"))
            except Exception as e:
                self.message_user(request, f"{e.__class__.__name__}: {str(e)}", messages.ERROR)
                report = updater.report_dict
                context = self.get_common_context(
                    request,
                    title="Update Individual by xlsx Report",
                    unique_report_rows=report[IndividualXlsxUpdate.STATUS_UNIQUE],
                    multiple_match_report_rows=report[IndividualXlsxUpdate.STATUS_MULTIPLE_MATCH],
                    no_match_report_rows=report[IndividualXlsxUpdate.STATUS_NO_MATCH],
                    xlsx_update_file=xlsx_update_file.id,
                )
                return TemplateResponse(
                    request,
                    "admin/household/individual/xlsx_update_stage3.html",
                    context,
                )

        return TemplateResponse(request, "admin/household/individual/xlsx_update.html", context)
