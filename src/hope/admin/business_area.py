import logging
from typing import TYPE_CHECKING, Any

from admin_extra_buttons.api import button
from admin_extra_buttons.mixins import confirm_action
from admin_sync.mixin import GetManyFromRemoteMixin
from adminfilters.mixin import AdminAutoCompleteSearchMixin
from django import forms
from django.contrib import admin, messages
from django.contrib.admin import SimpleListFilter, TabularInline
from django.contrib.admin.templatetags.admin_urls import add_preserved_filters
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.postgres.aggregates import ArrayAgg
from django.core.validators import RegexValidator
from django.db import transaction
from django.forms import inlineformset_factory
from django.http import HttpRequest, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.template.defaultfilters import slugify
from django.template.response import TemplateResponse
from django.urls import reverse
from jsoneditor.forms import JSONEditor

from hope.admin.utils import HOPEModelAdminBase, LastSyncDateResetMixin
from hope.apps.administration.widgets import JsonWidget
from hope.apps.core.services.rapid_pro.api import RapidProAPI
from hope.apps.payment.forms import AcceptanceProcessThresholdForm
from hope.apps.utils.security import is_root
from hope.models.acceptance_process_threshold import AcceptanceProcessThreshold
from hope.models.business_area import BusinessArea
from hope.models.document_type import DocumentType
from hope.models.partner import Partner
from hope.models.role_assignment import RoleAssignment

if TYPE_CHECKING:
    from uuid import UUID

    from django.contrib.admin.options import ModelAdmin
    from django.db.models import QuerySet

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

        for r1, r2 in zip(ranges, ranges[1:], strict=False):
            if not r1[1] or (r1[1] and r2[0] and r1[1] > r2[0]):  # [1, None) [10, 100) or [1, 10) [8, 20)
                raise forms.ValidationError(
                    f"Provided ranges overlap [{r1[0]}, {r1[1] or '∞'}) [{r2[0]}, {r2[1] or '∞'})"
                )

            if r1[1] != r2[0]:
                raise forms.ValidationError(
                    f"Whole range of [0 , ∞] is not covered, please cover range between [{r1[0]}, {r1[1] or '∞'})"
                    f" [{r2[0]}, {r2[1] or '∞'})"
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
    GetManyFromRemoteMixin,
    LastSyncDateResetMixin,
    AdminAutoCompleteSearchMixin,
    HOPEModelAdminBase,
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
        "postpone_deduplication",
        "is_split",
        "enable_email_notification",
        "is_accountability_applicable",
    )
    readonly_fields = ("parent", "is_split", "document_types_valid_for_deduplication")
    filter_horizontal = ("countries", "partners", "payment_countries")

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
                            f"You cannot remove {partner.name}"
                            f" because it has existing role assignments in this business area.",
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
            from hope.apps.registration_data.services.mark_submissions import (
                MarkSubmissions,
            )

            try:
                task = MarkSubmissions(business_area)
                result = task.execute()
                self.message_user(request, result["message"], messages.SUCCESS)
            except Exception as e:
                logger.warning(e)
                self.message_user(request, str(e), messages.ERROR)
            return HttpResponseRedirect(reverse("admin:core_businessarea_change", args=[business_area.id]))
        return confirm_action(
            self,
            request,
            self.mark_submissions,
            """<h1>DO NOT CONTINUE IF YOU ARE NOT SURE WHAT YOU ARE DOING</h1>
            <h3>All ImportedSubmission for not merged rdi will be marked.</h3>
            """,
            "Successfully executed",
        )
