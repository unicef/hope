from typing import Any

from adminfilters.autocomplete import AutoCompleteFilter
from django.contrib import admin, messages
from django.core.exceptions import ValidationError
from django.db import Error, transaction
from django.db.models.query import QuerySet
from django.http import HttpRequest, HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import reverse

from hope.admin.utils import HOPEModelAdminBase
from hope.apps.household.services.individual_xlsx_update import (
    IndividualXlsxUpdate,
    InvalidColumnsError,
)
from hope.models import XlsxUpdateFile


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

    def add_view(
        self,
        request: HttpRequest,
        form_url: str = "",
        extra_context: dict | None = None,
    ) -> Any:
        return self.xlsx_update(request)

    def _stage1(self, request: HttpRequest) -> TemplateResponse:
        from hope.apps.household.forms import UpdateByXlsxStage1Form  # pragma: no cover

        form = UpdateByXlsxStage1Form()
        context = self.get_common_context(request, title="Update Individual by xlsx", form=form)
        return TemplateResponse(request, "admin/household/individual/xlsx_update.html", context)

    def _stage2(self, request: HttpRequest) -> TemplateResponse:
        from hope.apps.household.forms import UpdateByXlsxStage1Form, UpdateByXlsxStage2Form  # pragma: no cover

        form = UpdateByXlsxStage1Form(request.POST, request.FILES)
        context = self.get_common_context(request, title="Update Individual by xlsx", form=form)
        if not form.is_valid():
            return TemplateResponse(request, "admin/household/individual/xlsx_update.html", context)

        xlsx_update_file = XlsxUpdateFile(
            file=form.cleaned_data["file"],
            business_area=form.cleaned_data["business_area"],
            rdi=form.cleaned_data["registration_data_import"],
            program=form.cleaned_data["program"],
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

        posted_match_columns = request.POST.getlist("xlsx_match_columns")
        if posted_match_columns:
            xlsx_update_file.xlsx_match_columns = posted_match_columns
            xlsx_update_file.save()
            return self._render_stage3_report(request, updater, xlsx_update_file)

        context = self.get_common_context(
            request,
            title="Update Individual by xlsx",
            form=UpdateByXlsxStage2Form(
                xlsx_columns=updater.columns_names,
                initial={"xlsx_update_file": xlsx_update_file},
            ),
        )
        return TemplateResponse(request, "admin/household/individual/xlsx_update_stage2.html", context)

    def _stage3(self, request: HttpRequest) -> TemplateResponse:
        from hope.apps.household.forms import UpdateByXlsxStage2Form  # pragma: no cover

        xlsx_update_file = XlsxUpdateFile.objects.get(pk=request.POST["xlsx_update_file"])
        updater = IndividualXlsxUpdate(xlsx_update_file)
        form = UpdateByXlsxStage2Form(request.POST, request.FILES, xlsx_columns=updater.columns_names)
        context = self.get_common_context(request, title="Update Individual by xlsx", form=form)
        if form.is_valid():
            try:
                xlsx_update_file.xlsx_match_columns = form.cleaned_data["xlsx_match_columns"]
                xlsx_update_file.save()
                return self._render_stage3_report(request, updater, xlsx_update_file)
            except InvalidColumnsError as e:
                self.message_user(request, f"{e.__class__.__name__}: {str(e)}", messages.ERROR)
        return TemplateResponse(request, "admin/household/individual/xlsx_update_stage2.html", context)

    def _render_stage3_report(
        self, request: HttpRequest, updater: IndividualXlsxUpdate, xlsx_update_file: XlsxUpdateFile
    ) -> TemplateResponse:
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

    def _stage4(self, request: HttpRequest) -> TemplateResponse | HttpResponseRedirect:
        xlsx_update_file_id = request.POST.get("xlsx_update_file")
        xlsx_update_file = XlsxUpdateFile.objects.get(pk=xlsx_update_file_id)
        updater = IndividualXlsxUpdate(xlsx_update_file)
        try:
            with transaction.atomic():
                updater.update_individuals()
            self.message_user(request, "Done", messages.SUCCESS)
            return HttpResponseRedirect(reverse("admin:household_individual_changelist"))
        except (ValidationError, Error) as e:
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

    def xlsx_update(self, request: HttpRequest) -> Any:
        if request.method == "GET":
            return self._stage1(request)

        stage = request.POST.get("stage")
        if stage == "2":
            return self._stage2(request)
        if stage == "3":
            return self._stage3(request)
        if stage == "4":
            return self._stage4(request)

        return self._stage1(request)
