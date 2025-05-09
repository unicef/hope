import logging
from typing import TYPE_CHECKING, Any, Callable

from django import forms
from django.contrib import admin, messages
from django.contrib.admin import SimpleListFilter, TabularInline
from django.contrib.admin.templatetags.admin_urls import add_preserved_filters
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.messages import ERROR
from django.contrib.postgres.aggregates import ArrayAgg
from django.contrib.postgres.fields import JSONField
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.validators import RegexValidator
from django.db import transaction
from django.forms import inlineformset_factory
from django.http import (
    HttpRequest,
    HttpResponse,
    HttpResponsePermanentRedirect,
    HttpResponseRedirect,
)
from django.shortcuts import get_object_or_404, redirect
from django.template.defaultfilters import slugify
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe

import xlrd
from admin_extra_buttons.api import button
from admin_extra_buttons.mixins import ExtraButtonsMixin, confirm_action
from admin_sync.mixin import GetManyFromRemoteMixin
from adminfilters.autocomplete import AutoCompleteFilter
from adminfilters.filters import ChoicesFieldComboFilter
from adminfilters.mixin import AdminAutoCompleteSearchMixin, AdminFiltersMixin
from jsoneditor.forms import JSONEditor
from xlrd import XLRDError

from hct_mis_api.apps.account.models import Partner, RoleAssignment
from hct_mis_api.apps.administration.widgets import JsonWidget
from hct_mis_api.apps.core.celery_tasks import (
    upload_new_kobo_template_and_update_flex_fields_task,
)
from hct_mis_api.apps.core.forms import DataCollectingTypeForm
from hct_mis_api.apps.core.models import (
    BusinessArea,
    CountryCodeMap,
    DataCollectingType,
    FlexibleAttribute,
    FlexibleAttributeChoice,
    FlexibleAttributeGroup,
    PeriodicFieldData,
    StorageFile,
    XLSXKoboTemplate,
)
from hct_mis_api.apps.core.services.rapid_pro.api import RapidProAPI
from hct_mis_api.apps.core.validators import KoboTemplateValidator
from hct_mis_api.apps.household.models import DocumentType
from hct_mis_api.apps.payment.forms import AcceptanceProcessThresholdForm
from hct_mis_api.apps.payment.models import AcceptanceProcessThreshold
from hct_mis_api.apps.utils.admin import (
    HOPEModelAdminBase,
    LastSyncDateResetMixin,
    SoftDeletableAdminMixin,
)
from hct_mis_api.apps.utils.security import is_root
from mptt.admin import MPTTModelAdmin

if TYPE_CHECKING:
    from uuid import UUID

    from django.contrib.admin import ModelAdmin
    from django.db.models.query import QuerySet


logger = logging.getLogger(__name__)


class XLSImportForm(forms.Form):
    xls_file = forms.FileField()


class TestRapidproForm(forms.Form):
    phone_number = forms.CharField(
        label="Phone number",
        required=True,
    )
    flow_name = forms.CharField(label="Name of the test flow", initial="Test", required=True)


class BusinessOfficeCodeValidator(RegexValidator):
    message = "Business office code must start with 'BO' and contains only chars"
    regex = "BO[A-Z]{2}"


class BusinessOfficeForm(forms.ModelForm):
    name = forms.CharField()
    code = forms.CharField(max_length=4, validators=[BusinessOfficeCodeValidator()])

    class Meta:
        model = BusinessArea
        fields = ("code", "name")


class BusinessofficeFilter(SimpleListFilter):
    template = "adminfilters/combobox.html"
    title = "Business Ofiice"
    parameter_name = "bo"

    def lookups(self, request: HttpRequest, model_admin: "ModelAdmin") -> list[tuple[int, str]]:
        return [(1, "Is a Business Office"), (2, "Is a Business Area")]

    def value(self) -> str:
        return self.used_parameters.get(self.parameter_name)

    def queryset(self, request: HttpRequest, queryset: "QuerySet") -> "QuerySet":
        if self.value() == "2":
            return queryset.filter(parent_id__isnull=True)
        if self.value() == "1":
            return queryset.exclude(parent_id__isnull=True)
        return queryset


class AcceptanceProcessThresholdFormset(forms.models.BaseInlineFormSet):
    @classmethod
    def validate_ranges(cls, ranges: list[list[int | None]]) -> None:
        ranges = sorted(ranges)  # sorted by range min value

        if ranges[0][0] != 0:
            raise forms.ValidationError("Ranges need to start from 0")

        for r1, r2 in zip(ranges, ranges[1:]):
            if not r1[1] or (r1[1] and r2[0] and r1[1] > r2[0]):  # [1, None) [10, 100) or [1, 10) [8, 20)
                raise forms.ValidationError(
                    f"Provided ranges overlap [{r1[0]}, {r1[1] or '∞'}) [{r2[0]}, {r2[1] or '∞'})"
                )

            if r1[1] != r2[0]:
                raise forms.ValidationError(
                    f"Whole range of [0 , ∞] is not covered, please cover range between [{r1[0]}, {r1[1] or '∞'}) [{r2[0]}, {r2[1] or '∞'})"
                )

        if ranges[-1][1] is not None:
            raise forms.ValidationError("Last range should cover ∞ (please leave empty value)")

    def clean(self) -> None:
        super().clean()
        ranges = []
        for idx, form in enumerate(self.forms):
            data = form.data.dict()
            _min = data[f"acceptance_process_thresholds-{idx}-payments_range_usd_0"]
            _max = data[f"acceptance_process_thresholds-{idx}-payments_range_usd_1"]
            _deleted = data.get(f"acceptance_process_thresholds-{idx}-DELETE") == "on"
            if not _deleted:
                ranges.append(
                    [
                        int(_min),
                        int(_max) if _max else None,
                    ]
                )

        if not ranges:
            return

        self.validate_ranges(ranges)


AcceptanceProcessThresholdInlineFormSet = inlineformset_factory(
    BusinessArea,
    AcceptanceProcessThreshold,
    form=AcceptanceProcessThresholdForm,
    formset=AcceptanceProcessThresholdFormset,
)


class AcceptanceProcessThresholdInline(TabularInline):
    model = AcceptanceProcessThreshold
    extra = 0
    formset = AcceptanceProcessThresholdInlineFormSet  # type: ignore
    ordering = [
        "payments_range_usd",
    ]
    verbose_name_plural = (
        "Acceptance Process Thresholds in USD- "
        "Please leave empty value to set max range as ∞, whole range [0, ∞) need to be covered. "
        "Example: [0, 100000) [100000, )"
    )


@admin.register(BusinessArea)
class BusinessAreaAdmin(
    GetManyFromRemoteMixin, LastSyncDateResetMixin, AdminAutoCompleteSearchMixin, HOPEModelAdminBase
):
    inlines = [
        AcceptanceProcessThresholdInline,
    ]
    list_display = (
        "name",
        "slug",
        "code",
        "region_name",
        "region_code",
        "active",
        "has_data_sharing_agreement",
        "screen_beneficiary",
        "postpone_deduplication",
        "is_split",
        "parent",
        "enable_email_notification",
        "is_accountability_applicable",
    )
    search_fields = ("name", "slug")
    list_filter = (
        "has_data_sharing_agreement",
        "active",
        "region_name",
        BusinessofficeFilter,
        "has_data_sharing_agreement",
        "screen_beneficiary",
        "postpone_deduplication",
        "is_split",
        "enable_email_notification",
        "is_accountability_applicable",
    )
    readonly_fields = ("parent", "is_split", "document_types_valid_for_deduplication")
    filter_horizontal = ("countries", "partners")

    def document_types_valid_for_deduplication(self, obj: Any) -> list:
        return list(DocumentType.objects.filter(valid_for_deduplication=True).values_list("label", flat=True))

    def formfield_for_dbfield(self, db_field: Any, request: HttpRequest, **kwargs: Any) -> Any:
        if db_field.name == "custom_fields":
            if is_root(request):
                kwargs = {"widget": JSONEditor}
            else:
                kwargs = {"widget": JsonWidget}
            return db_field.formfield(**kwargs)
        return super().formfield_for_dbfield(db_field, request, **kwargs)

    @button(label="Create Business Office", permission="core.can_split")
    def split_business_area(self, request: HttpRequest, pk: "UUID") -> HttpResponseRedirect | TemplateResponse:
        context = self.get_common_context(request, pk)
        opts = self.object._meta
        if request.POST:
            form = context["form"] = BusinessOfficeForm(request.POST)
            if form.is_valid():
                with transaction.atomic():
                    self.object.is_split = True
                    name = form.cleaned_data["name"]
                    office = BusinessArea.objects.create(
                        code=form.cleaned_data["code"],
                        name=form.cleaned_data["name"],
                        parent=self.object,
                        region_code=self.object.region_code,
                        region_name=self.object.region_name,
                        long_name=f"Business Office: {name}",
                        slug=slugify(name),
                    )
                preserved_filters = self.get_preserved_filters(request)

                redirect_url = reverse(
                    f"admin:{opts.app_label}_{opts.model_name}_change",
                    args=(office.pk,),
                    current_app=self.admin_site.name,
                )
                redirect_url = add_preserved_filters(
                    {"preserved_filters": preserved_filters, "opts": opts}, redirect_url
                )
                return HttpResponseRedirect(redirect_url)
        else:
            context["form"] = BusinessOfficeForm()

        return TemplateResponse(request, "core/admin/split_ba.html", context)

    @button(label="Partners", permission="account.can_change_allowed_partners")
    def allowed_partners(self, request: HttpRequest, pk: int) -> TemplateResponse | HttpResponseRedirect:
        business_area = get_object_or_404(BusinessArea, pk=pk)

        class AllowedPartnersForm(forms.Form):
            partners = forms.ModelMultipleChoiceField(
                queryset=Partner.objects.exclude(
                    id__in=Partner.objects.filter(parent__isnull=False).values_list("parent_id", flat=True)
                ),
                required=False,
                widget=FilteredSelectMultiple("Partners", is_stacked=False),
            )

        if request.method == "POST":
            form = AllowedPartnersForm(request.POST)
            if form.is_valid():
                selected_partners = form.cleaned_data["partners"]
                # Get the current allowed partners for the business area
                previous_allowed_partners = set(Partner.objects.filter(allowed_business_areas=business_area))

                # Identify which partners were removed
                removed_partners = previous_allowed_partners - set(selected_partners)
                # Check if there are any removed partners with existing role assignments in this business area
                for partner in removed_partners:
                    if RoleAssignment.objects.filter(partner=partner, business_area=business_area).exists():
                        self.message_user(
                            request,
                            f"You cannot remove {partner.name} because it has existing role assignments in this business area.",
                            messages.ERROR,
                        )
                        return HttpResponseRedirect(request.get_full_path())

                for partner in Partner.objects.all():
                    if partner in selected_partners:
                        partner.allowed_business_areas.add(business_area)
                    else:
                        partner.allowed_business_areas.remove(business_area)
                messages.success(request, "Allowed partners successfully updated.")
                return HttpResponseRedirect(request.get_full_path())

        else:
            form = AllowedPartnersForm(
                initial={"partners": Partner.objects.filter(allowed_business_areas=business_area)}
            )

        context = self.get_common_context(request, pk)
        context.update(
            {
                "business_area": business_area,
                "form": form,
            }
        )

        return TemplateResponse(request, "core/admin/allowed_partners.html", context)

    @button(permission="account.view_user")
    def members(self, request: HttpRequest, pk: "UUID") -> TemplateResponse:
        context = self.get_common_context(request, pk, title="Members")
        context["members"] = (
            context["original"]
            .role_assignments.values(
                "user__id",
                "user__email",
                "user__username",
                "user__custom_fields__kobo_username",
            )
            .annotate(roles=ArrayAgg("role__name"))
            .order_by("user__username")
        )
        return TemplateResponse(request, "core/admin/ba_members.html", context)

    @button(label="Test RapidPro Connection", permission="core.ping_rapidpro")
    def _test_rapidpro_connection(self, request: HttpRequest, pk: "UUID") -> TemplateResponse:
        context: dict = self.get_common_context(request, pk)
        context["business_area"] = self.object
        context["title"] = f"Test `{self.object.name}` RapidPRO connection"

        if request.method == "GET":
            context["form"] = TestRapidproForm()
        else:
            form = TestRapidproForm(request.POST)
            try:
                if form.is_valid():
                    api = RapidProAPI(self.object.slug, RapidProAPI.MODE_VERIFICATION)
                    phone_number = form.cleaned_data["phone_number"]
                    flow_name = form.cleaned_data["flow_name"]
                    context["phone_number"] = phone_number
                    context["flow_name"] = flow_name

                    error, response = api.test_connection_start_flow(flow_name, phone_number)
                    if response:
                        for entry in response:
                            context["flow_uuid"] = entry.response["flow"]["uuid"]
                            context["flow_status"] = entry.response["status"]
                            context["timestamp"] = entry.response["created_on"]

                    if error:
                        messages.error(request, error)
                    else:
                        messages.success(request, "Connection successful")
            except Exception as e:
                self.message_user(request, f"{e.__class__.__name__}: {e}", messages.ERROR)
            context["form"] = form

        return TemplateResponse(request, "core/test_rapidpro.html", context)

    @button(permission=is_root)
    def mark_submissions(self, request: HttpRequest, pk: "UUID") -> HttpResponseRedirect:
        business_area = self.get_queryset(request).get(pk=pk)
        if request.method == "POST":
            from hct_mis_api.apps.registration_data.services.mark_submissions import (
                MarkSubmissions,
            )

            try:
                task = MarkSubmissions(business_area)
                result = task.execute()
                self.message_user(request, result["message"], messages.SUCCESS)
            except Exception as e:
                logger.exception(e)
                self.message_user(request, str(e), messages.ERROR)
            return HttpResponseRedirect(reverse("admin:core_businessarea_change", args=[business_area.id]))
        return confirm_action(
            self,
            request,
            self.mark_submissions,
            mark_safe(
                """<h1>DO NOT CONTINUE IF YOU ARE NOT SURE WHAT YOU ARE DOING</h1>
                <h3>All ImportedSubmission for not merged rdi will be marked.</h3>
                """
            ),
            "Successfully executed",
        )


class FlexibleAttributeInline(admin.TabularInline):
    model = FlexibleAttribute
    fields = readonly_fields = ("name", "associated_with", "required")
    extra = 0


@admin.register(FlexibleAttribute)
class FlexibleAttributeAdmin(AdminFiltersMixin, GetManyFromRemoteMixin, SoftDeletableAdminMixin):
    list_display = ("name", "type", "required", "program", "pdu_data", "group")
    list_filter = (
        ("type", ChoicesFieldComboFilter),
        ("associated_with", ChoicesFieldComboFilter),
        "required",
        ("group", AutoCompleteFilter),
    )
    search_fields = ("name",)
    formfield_overrides = {
        JSONField: {"widget": JSONEditor},
    }
    raw_id_fields = ("group", "program", "pdu_data")

    def get_queryset(self, request: HttpRequest) -> "QuerySet":
        return super().get_queryset(request).select_related("group", "program", "pdu_data")


@admin.register(PeriodicFieldData)
class PeriodicFieldDataAdmin(admin.ModelAdmin):
    list_filter = ("subtype", "number_of_rounds")
    list_display = ("__str__", "subtype", "number_of_rounds")


@admin.register(FlexibleAttributeGroup)
class FlexibleAttributeGroupAdmin(AdminFiltersMixin, GetManyFromRemoteMixin, SoftDeletableAdminMixin, MPTTModelAdmin):
    inlines = (FlexibleAttributeInline,)
    list_display = ("name", "parent", "required", "repeatable", "is_removed")
    # autocomplete_fields = ("parent",)
    raw_id_fields = ("parent",)
    list_filter = (
        ("parent", AutoCompleteFilter),
        "repeatable",
        "required",
    )
    search_fields = ("name",)
    formfield_overrides = {
        JSONField: {"widget": JSONEditor},
    }


@admin.register(FlexibleAttributeChoice)
class FlexibleAttributeChoiceAdmin(GetManyFromRemoteMixin, SoftDeletableAdminMixin):
    list_display = (
        "list_name",
        "name",
    )
    search_fields = ("name", "list_name")
    filter_horizontal = ("flex_attributes",)
    formfield_overrides = {
        JSONField: {"widget": JSONEditor},
    }


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

    def get_form(self, request: HttpRequest, obj: Any | None = None, change: bool = False, **kwargs: Any) -> Any:
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
        self, request: HttpRequest, form_url: str = "", extra_context: dict | None = None
    ) -> HttpResponsePermanentRedirect | TemplateResponse:
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
        self, request: HttpRequest, object_id: str, form_url: str = "", extra_context: dict[str, Any] | None = None
    ) -> HttpResponse:
        extra_context = {"show_save": False, "show_save_and_continue": False, "show_delete": True}
        has_add_permission: Callable = self.has_add_permission
        self.has_add_permission: Callable = lambda __: False
        template_response = super().change_view(request, object_id, form_url, extra_context)
        self.has_add_permission = has_add_permission

        return template_response


@admin.register(CountryCodeMap)
class CountryCodeMapAdmin(HOPEModelAdminBase):
    list_display = ("country", "alpha2", "alpha3", "ca_code")
    search_fields = ("country", "alpha2", "alpha3", "ca_code")
    raw_id_fields = ("country",)

    def alpha2(self, obj: Any) -> str:
        return obj.country.iso_code2

    def alpha3(self, obj: Any) -> str:
        return obj.country.iso_code3

    def get_queryset(self, request: HttpRequest) -> "QuerySet":
        return (
            super()
            .get_queryset(request)
            .select_related(
                "country",
            )
        )


@admin.register(StorageFile)
class StorageFileAdmin(ExtraButtonsMixin, admin.ModelAdmin):
    list_display = ("file_name", "file", "business_area", "file_size", "created_by", "created_at")

    def has_change_permission(self, request: HttpRequest, obj: Any | None = None) -> bool:
        return request.user.can_download_storage_files()

    def has_delete_permission(self, request: HttpRequest, obj: Any | None = None) -> bool:
        return request.user.can_download_storage_files()

    def has_view_permission(self, request: HttpRequest, obj: Any | None = None) -> bool:
        return request.user.can_download_storage_files()

    def has_add_permission(self, request: HttpRequest) -> bool:
        return request.user.can_download_storage_files()


@admin.register(DataCollectingType)
class DataCollectingTypeAdmin(AdminFiltersMixin, admin.ModelAdmin):
    form = DataCollectingTypeForm

    list_display = (
        "label",
        "code",
        "type",
        "active",
        "deprecated",
        "individual_filters_available",
        "household_filters_available",
        "recalculate_composition",
        "weight",
    )
    list_filter = (
        ("limit_to", AutoCompleteFilter),
        "type",
        "active",
        "individual_filters_available",
        "household_filters_available",
        "recalculate_composition",
    )
    filter_horizontal = ("compatible_types", "limit_to")
    search_fields = (
        "label",
        "code",
    )
