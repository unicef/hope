from io import BytesIO
import os
from pathlib import Path
from typing import Any
import zipfile

from admin_extra_buttons.decorators import button
from adminfilters.autocomplete import AutoCompleteFilter
from adminfilters.filters import ChoicesFieldComboFilter
from adminfilters.mixin import AdminAutoCompleteSearchMixin
from django import forms
from django.contrib import admin, messages
from django.contrib.admin.options import get_content_type_for_model
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.db.models import Q, QuerySet
from django.forms import CheckboxSelectMultiple, formset_factory
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django_celery_boost.models import AsyncJobModel
from mptt.forms import TreeNodeMultipleChoiceField

from hope.admin.utils import (
    HOPEModelAdminBase,
    LastSyncDateResetMixin,
    SoftDeletableAdminMixin,
)
from hope.apps.household.documents import HouseholdDocument, get_individual_doc
from hope.apps.household.forms import CreateTargetPopulationTextForm
from hope.apps.registration_datahub.apis.deduplication_engine import DeduplicationEngineAPI
from hope.apps.registration_datahub.services.biometric_deduplication import BiometricDeduplicationService
from hope.apps.targeting.celery_tasks import create_tp_from_list
from hope.apps.utils.elasticsearch_utils import populate_index
from hope.models import (
    AdminAreaLimitedTo,
    Area,
    AsyncJob,
    FileTemp,
    Household,
    Individual,
    Partner,
    Program,
    ProgramCycle,
)


@admin.register(ProgramCycle)
class ProgramCycleAdmin(LastSyncDateResetMixin, HOPEModelAdminBase):
    list_display = (
        "title",
        "program",
        "status",
        "start_date",
        "end_date",
        "created_by",
    )
    date_hierarchy = "start_date"
    list_filter = (
        ("program__business_area", AutoCompleteFilter),
        ("program", AutoCompleteFilter),
        ("created_by", AutoCompleteFilter),
        ("status", ChoicesFieldComboFilter),
    )
    search_fields = ("title", "program__name")
    raw_id_fields = ("program", "created_by")
    exclude = ("unicef_id",)


class ProgramCycleAdminInline(admin.TabularInline):
    model = ProgramCycle
    extra = 0
    fields = readonly_fields = (
        "unicef_id",
        "title",
        "status",
        "start_date",
        "end_date",
        "created_at",
        "updated_at",
        "created_by",
    )
    ordering = ["-start_date"]
    raw_id_fields = ("created_by",)


class PartnerAreaLimitForm(forms.Form):
    partner = forms.ModelChoiceField(queryset=Partner.objects.all(), required=True)
    areas = TreeNodeMultipleChoiceField(
        queryset=Area.objects.filter(area_type__area_level__lte=3),
        widget=CheckboxSelectMultiple(),
        required=True,
    )


class BulkUploadIndividualsPhotosForm(forms.Form):
    file = forms.FileField(widget=forms.ClearableFileInput(attrs={"accept": ".zip"}))

    def clean_file(self):
        file = self.cleaned_data["file"]

        if not file.name.lower().endswith(".zip"):
            raise ValidationError("The uploaded file must be a .zip archive.")

        if not zipfile.is_zipfile(file):
            raise ValidationError("The uploaded file is not a valid ZIP archive.")

        return file


class ProgramAdminForm(forms.ModelForm):
    class Meta:
        model = Program
        fields = (
            "data_collecting_type",
            "beneficiary_group",
            "business_area",
            "admin_areas",
            "name",
            "programme_code",
            "status",
            "slug",
            "description",
            "start_date",
            "end_date",
            "sector",
            "budget",
            "frequency_of_payments",
            "scope",
            "partner_access",
            "cash_plus",
            "population_goal",
            "administrative_areas_of_implementation",
            "biometric_deduplication_enabled",
            "collision_detector",
            "is_visible",
            "household_count",
            "individual_count",
            "is_removed",
            "last_sync_at",
            "version",
            "sanction_lists",
            "reconciliation_window_in_days",
            "send_reconciliation_window_expiry_notifications",
        )

    def _handle_biometric_deduplication_set(self, action: str) -> None:
        try:
            service = BiometricDeduplicationService()
            if action == "create":
                service.create_deduplication_set(self.instance)
                if self.instance.pk:
                    service.mark_rdis_as_pending(self.instance)
            elif action == "delete":
                service.delete_deduplication_set(self.instance)
        except (
            DeduplicationEngineAPI.API_EXCEPTION_CLASS,
            DeduplicationEngineAPI.API_MISSING_CREDENTIALS_EXCEPTION_CLASS,
        ) as exc:
            raise ValidationError(f"BiometricDeduplicationService Error: {exc}") from exc

    def clean(self) -> dict[str, Any]:
        cleaned_data = super().clean()
        if self.errors:
            return cleaned_data

        if "biometric_deduplication_enabled" in self.changed_data:
            enable = cleaned_data.get("biometric_deduplication_enabled")
            if self.instance.pk:
                original_enabled = self.instance.biometric_deduplication_enabled
                if enable is True and original_enabled is False:
                    self._handle_biometric_deduplication_set("create")
                elif enable is False and original_enabled is True:
                    self._handle_biometric_deduplication_set("delete")
            elif enable is True:
                self._handle_biometric_deduplication_set("create")

        return cleaned_data


@admin.register(Program)
class ProgramAdmin(
    SoftDeletableAdminMixin,
    LastSyncDateResetMixin,
    AdminAutoCompleteSearchMixin,
    HOPEModelAdminBase,
):
    form = ProgramAdminForm
    list_display = (
        "name",
        "programme_code",
        "status",
        "start_date",
        "end_date",
        "business_area",
        "data_collecting_type",
        "beneficiary_group",
        "sector",
        "scope",
        "frequency_of_payments",
        "partner_access",
        "biometric_deduplication_enabled",
        "cash_plus",
        "is_visible",
    )
    date_hierarchy = "start_date"
    list_filter = (
        ("status", ChoicesFieldComboFilter),
        ("business_area", AutoCompleteFilter),
        ("data_collecting_type", AutoCompleteFilter),
        ("beneficiary_group", AutoCompleteFilter),
        ("scope", ChoicesFieldComboFilter),
        ("sector", ChoicesFieldComboFilter),
        "frequency_of_payments",
        ("partner_access", ChoicesFieldComboFilter),
        "biometric_deduplication_enabled",
        "cash_plus",
        "is_visible",
    )
    filter_horizontal = ("sanction_lists",)
    search_fields = ("name", "programme_code")
    autocomplete_fields = ("business_area", "data_collecting_type", "beneficiary_group", "admin_areas")

    inlines = (ProgramCycleAdminInline,)
    ordering = ("name",)

    def get_queryset(self, request: HttpRequest) -> QuerySet[Program]:
        return (
            super().get_queryset(request).select_related("data_collecting_type", "business_area", "beneficiary_group")
        )

    @button(
        permission="payment.add_paymentplan",
    )
    def create_target_population_from_list(self, request: HttpRequest, pk: str) -> HttpResponse | None:
        context = self.get_common_context(request, title="Create TargetPopulation")
        program = Program.objects.get(pk=pk)
        business_area = program.business_area

        if "apply" in request.POST:
            form = CreateTargetPopulationTextForm(request.POST, read_only=True, program=program)
            if request.POST["criteria"] and form.is_valid():
                context["ba_name"] = business_area.name
                context["programme_name"] = program.name
                context["total"] = len(form.cleaned_data["criteria"])

        elif "confirm" in request.POST:
            create_tp_from_list.delay(request.POST.dict(), str(request.user.pk), str(program.pk))
            message = f"Creation of target population <b>{request.POST['name']}</b> scheduled."
            messages.success(request, message)
            url = reverse("admin:targeting_targetpopulation_changelist")
            return HttpResponseRedirect(url)

        else:
            form = CreateTargetPopulationTextForm(
                initial={
                    "action": "create_tp_from_list",
                },
                program=program,
            )

        context["form"] = form
        return TemplateResponse(
            request,
            "admin/program/program/create_target_population_from_text.html",
            context,
        )

    @button(permission="account.can_change_area_limits")
    def area_limits(self, request: HttpRequest, pk: int) -> TemplateResponse | HttpResponseRedirect:
        context = self.get_common_context(request, pk, title="Admin Area Limits")
        program: Program = context["original"]
        is_editable = program.partner_access == Program.SELECTED_PARTNERS_ACCESS
        PartnerAreaLimitFormSet = formset_factory(PartnerAreaLimitForm, extra=0, can_delete=True)  # noqa

        if request.method == "POST" and is_editable:
            partner_area_form_set = PartnerAreaLimitFormSet(request.POST, prefix="program_areas")
            if partner_area_form_set.is_valid():
                partners_for_limits_to_update = []
                partners_for_limits_to_delete = []

                for partner_area_form in partner_area_form_set:
                    form_data = partner_area_form.cleaned_data
                    if not form_data:
                        continue

                    partner = form_data["partner"]
                    if form_data.get("DELETE"):
                        partners_for_limits_to_delete.append(partner)
                    else:
                        areas_ids = [str(area.id) for area in form_data["areas"]]
                        partners_for_limits_to_update.append((partner, areas_ids))

                if partners_for_limits_to_delete:
                    AdminAreaLimitedTo.objects.filter(
                        partner__in=partners_for_limits_to_delete, program=program
                    ).delete()

                for partner, areas_ids in partners_for_limits_to_update:
                    program_partner, _ = AdminAreaLimitedTo.objects.get_or_create(
                        partner=partner,
                        program=program,
                    )
                    program_partner.areas.set(areas_ids)

                return HttpResponseRedirect(reverse("admin:program_program_area_limits", args=[pk]))

        admin_area_limits = program.admin_area_limits.select_related("partner").prefetch_related("areas")
        partner_area_data = [
            {
                "partner": area_limit.partner,
                "areas": [str(area.id) for area in area_limit.areas.all()],
            }
            for area_limit in admin_area_limits
        ]

        partner_area_form_set = PartnerAreaLimitFormSet(initial=partner_area_data, prefix="program_areas")

        context["program_area_formset"] = partner_area_form_set
        context["business_area"] = program.business_area
        context["areas"] = Area.objects.filter(
            area_type__country__business_areas__id=program.business_area.id, area_type__area_level__lte=3
        ).select_related("area_type__country")

        # it's only possible to create area limits for partners that have a role in this program
        context["partners"] = (
            Partner.objects.filter(
                Q(role_assignments__program=program)
                | (Q(role_assignments__business_area=program.business_area) & Q(role_assignments__program__isnull=True))
            )
            .exclude(parent__name="UNICEF")
            .select_related("parent")
            .order_by("name")
            .distinct()
        )
        context["program"] = program

        if is_editable:
            return TemplateResponse(request, "admin/program/program/program_area_limits.html", context)
        return TemplateResponse(request, "admin/program/program/program_area_limits_readonly.html", context)

    @button(permission="account.can_reindex_programs")
    def reindex_program(self, request: HttpRequest, pk: int) -> HttpResponseRedirect:
        program = Program.objects.get(pk=pk)
        populate_index(
            Individual.all_merge_status_objects.filter(program=program),
            get_individual_doc(program.business_area.slug),
        )
        populate_index(
            Household.all_merge_status_objects.filter(program=program),
            HouseholdDocument,
        )
        messages.success(request, f"Program {program.name} reindexed.")
        return HttpResponseRedirect(reverse("admin:program_program_changelist"))

    @button(label="Bulk Upload Individual Photos", permission="program.can_bulk_upload_individual_photos")
    def bulk_upload_individuals_photos(self, request: HttpRequest, pk: int) -> TemplateResponse:
        program = Program.objects.get(pk=pk)
        context: dict = self.get_common_context(request, processed=False)
        context["pk"] = pk
        if request.method == "GET":
            form = BulkUploadIndividualsPhotosForm()
            context["form"] = form
        else:
            form = BulkUploadIndividualsPhotosForm(data=request.POST, files=request.FILES)
            if form.is_valid():
                try:
                    zip_file = form.cleaned_data["file"]
                    file_temp = FileTemp.objects.create(
                        object_id=program.pk,
                        content_type=get_content_type_for_model(program),
                        file=zip_file,
                    )
                    job = AsyncJob.objects.create(
                        program=program,
                        owner=request.user,
                        type=AsyncJobModel.JobType.JOB_TASK,
                        action="hope.admin.program.bulk_upload_individuals_photos_action",
                        config={"file_id": str(file_temp.pk)},
                        description=f"Bulk upload individuals photos for program {program.pk}",
                    )
                    job.queue()
                    self.message_user(
                        request,
                        f"Photos import task scheduled [{job.pk}]AsyncJob",
                        messages.SUCCESS,
                    )
                except Exception as e:  # noqa
                    self.message_user(request, f"Error scheduling task: {e}", messages.ERROR)

            else:
                self.message_user(request, "Form validation error", messages.ERROR)
                context["form"] = form
        return TemplateResponse(request, "admin/program/program/bulk_upload_individuals_photos.html", context)


def _collect_zip_entries(
    data: bytes, job: "AsyncJob"
) -> tuple[list[tuple[str, str, str]], set[str], list[str]]:
    entries: list[tuple[str, str, str]] = []
    individual_unicef_ids: set[str] = set()
    invalid_filenames: list[str] = []

    try:
        with zipfile.ZipFile(BytesIO(data)) as zf:
            for name in zf.namelist():
                if name.endswith("/"):
                    continue

                filename = Path(name).name
                stem, ext = os.path.splitext(filename)

                if ext.lower() not in (".jpg", ".jpeg"):
                    continue

                individual_unicef_id = stem.strip()
                if not individual_unicef_id.startswith("IND-"):
                    invalid_filenames.append(filename)
                    continue

                entries.append((name, filename, individual_unicef_id))
                individual_unicef_ids.add(individual_unicef_id)
    except zipfile.BadZipFile as exc:
        job.errors = {"file": f"Invalid ZIP archive: {exc}"}
        job.save(update_fields=["errors"])
        raise ValueError(f"Invalid ZIP archive: {exc}") from exc

    return entries, individual_unicef_ids, invalid_filenames


def bulk_upload_individuals_photos_action(job: "AsyncJob") -> int:
    """Update individual photos from the ZIP attached to this job.

    - Collect all JPEG filenames (IND-...*.jpg) from job.file.file.
    - Bulk-load Individuals by their unicef_id (or your ID field).
    - Save each image into individual.photo.
    - Store errors in job.errors.
    """
    job.errors = {}

    file_id = job.config.get("file_id")
    file = FileTemp.objects.filter(pk=file_id).first()
    if not file:
        job.errors = {"file": "This job requires the file."}
        job.save(update_fields=["errors"])
        raise ValueError("BulkUploadIndividualsPhotosJob requires a file.")

    file_field = file.file
    missing_individuals: list[str] = []
    updated_count = 0

    # read ZIP once into memory
    with file_field.open("rb") as f:
        data = f.read()

    entries, individual_unicef_ids, invalid_filenames = _collect_zip_entries(data, job)

    if not entries:
        job.errors = {"file": "No valid JPEG files found in archive."}
        job.save(update_fields=["errors"])
        return 0

    individuals = Individual.objects.filter(program=job.program, unicef_id__in=individual_unicef_ids).only(
        "id", "unicef_id", "photo"
    )

    individuals_by_unicef_id = {ind.unicef_id: ind for ind in individuals}

    with zipfile.ZipFile(BytesIO(data)) as zf:
        for member_name, filename, individual_id in entries:
            individual = individuals_by_unicef_id.get(individual_id)
            if not individual:
                missing_individuals.append(filename)
                continue

            with zf.open(member_name) as img_fp:
                img_bytes = img_fp.read()

            individual.photo.save(
                filename,
                ContentFile(img_bytes),
                save=True,
            )
            updated_count += 1

    if invalid_filenames:
        job.errors["invalid_filenames"] = sorted(set(invalid_filenames))
    if missing_individuals:
        job.errors["missing_individuals"] = sorted(set(missing_individuals))
    job.save(update_fields=["errors"])

    if not updated_count:
        raise ValueError(f"None photos matched to an individual: {job.errors}")
    return updated_count
