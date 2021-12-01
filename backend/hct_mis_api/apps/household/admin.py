import logging
from functools import wraps
from inspect import isclass
from itertools import chain

from django.contrib import admin, messages
from django.contrib.admin import TabularInline
from django.contrib.admin.models import LogEntry
from django.contrib.messages import DEFAULT_TAGS
from django.contrib.postgres.fields import JSONField
from django.db.models import Count, Q
from django.db.transaction import atomic
from django.http import HttpResponse, HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils import timezone
from django.utils.safestring import mark_safe

from admin_extra_urls.decorators import button, href
from admin_extra_urls.mixins import ExtraUrlMixin
from adminfilters.autocomplete import AutoCompleteFilter
from adminfilters.filters import (
    AllValuesComboFilter,
    ChoicesFieldComboFilter,
    MaxMinFilter,
    RelatedFieldComboFilter,
    TextFieldFilter,
)
from advanced_filters.admin import AdminAdvancedFiltersMixin
from jsoneditor.forms import JSONEditor
from smart_admin.mixins import FieldsetMixin as SmartFieldsetMixin
from smart_admin.mixins import LinkedObjectsMixin

from hct_mis_api.apps.administration.widgets import JsonWidget
from hct_mis_api.apps.grievance.models import (
    TicketNeedsAdjudicationDetails,
    TicketSystemFlaggingDetails,
)
from hct_mis_api.apps.household.forms import UpdateByXlsxStage1Form, UpdateByXlsxStage2Form
from hct_mis_api.apps.household.individual_xlsx_update import IndividualXlsxUpdate
from hct_mis_api.apps.household.models import (
    HEAD,
    ROLE_ALTERNATE,
    ROLE_PRIMARY,
    Agency,
    Document,
    DocumentType,
    EntitlementCard,
    Household,
    Individual,
    IndividualIdentity,
    IndividualRoleInHousehold,
    XlsxUpdateFile,
)
from hct_mis_api.apps.utils.admin import (
    HOPEModelAdminBase,
    LastSyncDateResetMixin,
    SoftDeletableAdminMixin,
)
from hct_mis_api.apps.utils.security import is_root

logger = logging.getLogger(__name__)


@admin.register(Agency)
class AgencyTypeAdmin(HOPEModelAdminBase):
    list_display = ("label", "type", "country")


@admin.register(Document)
class DocumentAdmin(SoftDeletableAdminMixin, HOPEModelAdminBase):
    list_display = ("document_number", "type", "status", "individual")
    raw_id_fields = ("individual",)
    list_filter = (("type", RelatedFieldComboFilter),)


@admin.register(DocumentType)
class DocumentTypeAdmin(HOPEModelAdminBase):
    list_display = ("label", "country", "type")


@admin.register(Household)
class HouseholdAdmin(
    SoftDeletableAdminMixin,
    LastSyncDateResetMixin,
    LinkedObjectsMixin,
    AdminAdvancedFiltersMixin,
    SmartFieldsetMixin,
    HOPEModelAdminBase,
):
    advanced_filter_fields = (
        "name",
        "country",
        "size",
        "admin_area",
        "last_registration_date",
        "registration_data_import",
        ("business_area__name", "business area"),
    )

    list_display = (
        "unicef_id",
        "country",
        "head_of_household",
        "size",
    )
    list_filter = (
        TextFieldFilter.factory("unicef_id", "UNICEF ID"),
        TextFieldFilter.factory("unhcr_id", "UNHCR ID"),
        TextFieldFilter.factory("id", "MIS ID"),
        # ("country", ChoicesFieldComboFilter),
        ("business_area", AutoCompleteFilter),
        ("size", MaxMinFilter),
        "org_enumerator",
        "last_registration_date",
    )
    readonly_fields = ("created_at", "updated_at")
    filter_horizontal = ("representatives", "programs")
    raw_id_fields = ("registration_data_import", "admin_area", "head_of_household", "business_area")
    fieldsets = [
        (None, {"fields": (("unicef_id", "head_of_household"),)}),
        (
            "Registration",
            {
                "classes": ("collapse",),
                "fields": (
                    "registration_data_import",
                    "registration_method",
                    "first_registration_date",
                    "last_registration_date",
                    "org_enumerator",
                    "org_name_enumerator",
                    "name_enumerator",
                ),
            },
        ),
        (
            "Dates",
            {
                "classes": ("collapse",),
                "fields": (
                    ("created_at", "updated_at"),
                    "last_sync_at",
                    "removed_date",
                    "withdrawn_date",
                ),
            },
        ),
        ("Others", {"classes": ("collapse",), "fields": ("__others__",)}),
    ]

    def get_ignored_linked_objects(self):
        return []

    @button(permission="can_withdrawn")
    def withdrawn(self, request, pk):
        from hct_mis_api.apps.grievance.models import GrievanceTicket

        context = self.get_common_context(request, pk, title="Withdrawn")
        obj = context["original"]
        new_withdrawn_status = "" if obj.withdrawn else "checked"
        context["status"] = new_withdrawn_status
        tickets = GrievanceTicket.objects.belong_household(obj)
        if obj.withdrawn:
            tickets = filter(lambda t: t.ticket.extras.get("status_before_withdrawn", False), tickets)
        else:
            tickets = filter(lambda t: t.ticket.status != GrievanceTicket.STATUS_CLOSED, tickets)

        context["tickets"] = tickets
        if request.method == "POST":
            try:
                with atomic():
                    withdrawn = not obj.withdrawn
                    if withdrawn:
                        obj.withdrawn_date = timezone.now()
                        message = "{} has been withdrawn"
                    else:
                        obj.withdrawn_date = None
                        message = "{} has been restored"
                    obj.withdrawn = withdrawn
                    withdrawns = list(obj.individuals.values_list("id", flat=True))
                    for ind in Individual.objects.filter(id__in=withdrawns, duplicate=False):
                        ind.withdrawn = withdrawn
                        ind.save()
                        self.log_change(request, ind, message.format("Individual"))
                    for tkt in context["tickets"]:
                        if withdrawn:
                            tkt.ticket.extras["status_before_withdrawn"] = tkt.ticket.status
                            tkt.ticket.status = GrievanceTicket.STATUS_CLOSED
                            self.log_change(request, tkt.ticket, "Ticket closed due to Household withdrawn")
                        else:
                            if tkt.ticket.extras.get("status_before_withdrawn"):
                                tkt.ticket.status = tkt.ticket.extras["status_before_withdrawn"]
                                tkt.ticket.extras["status_before_withdrawn"] = ""
                            self.log_change(request, tkt.ticket, "Ticket reopened due to Household restore")
                        tkt.ticket.save()

                    obj.save()
                    self.log_change(request, obj, message.format("Household"))
                    return HttpResponseRedirect(request.path)
            except Exception as e:
                self.message_user(request, str(e), messages.ERROR)

        return TemplateResponse(request, "admin/household/household/withdrawn.html", context)

    @button()
    def tickets(self, request, pk):
        context = self.get_common_context(request, pk, title="Tickets")
        obj = context["original"]
        tickets = []
        for entry in chain(obj.sensitive_ticket_details.all(), obj.complaint_ticket_details.all()):
            tickets.append(entry.ticket)
        context["tickets"] = tickets
        return TemplateResponse(request, "admin/household/household/tickets.html", context)

    @button()
    def members(self, request, pk):
        obj = Household.objects.get(pk=pk)
        url = reverse("admin:household_individual_changelist")
        return HttpResponseRedirect(f"{url}?household|unicef_id|iexact={obj.unicef_id}")

    @button()
    def sanity_check(self, request, pk):
        # NOTE: this code is not should be optimized in the future and it is not
        # intended to be used in bulk
        hh = self.get_object(request, pk)
        warnings = []
        primary = None
        head = None
        try:
            primary = IndividualRoleInHousehold.objects.get(household=hh, role=ROLE_PRIMARY)
        except IndividualRoleInHousehold.DoesNotExist:
            warnings.append([messages.ERROR, "Head of househould not found"])

        alternate = IndividualRoleInHousehold.objects.filter(household=hh, role=ROLE_ALTERNATE).first()
        try:
            head = hh.individuals.get(relationship=HEAD)
        except IndividualRoleInHousehold.DoesNotExist:
            warnings.append([messages.ERROR, "Head of househould not found"])

        total_in_ranges = 0
        for gender in ["male", "female"]:
            for num_range in ["0_5", "6_11", "12_17", "18_59", "60"]:
                field = f"{gender}_age_group_{num_range}_count"
                total_in_ranges += getattr(hh, field, 0) or 0

        active_individuals = hh.individuals.exclude(Q(duplicate=True) | Q(withdrawn=True))
        ghosts_individuals = hh.individuals.filter(Q(duplicate=True) | Q(withdrawn=True))
        all_individuals = hh.individuals.all()
        if hh.collect_individual_data:
            if active_individuals.count() != hh.size:
                warnings.append([messages.WARNING, "HH size does not match"])

        else:
            if all_individuals.count() > 1:
                warnings.append([messages.ERROR, "Individual data not collected but members found"])

        if hh.size != total_in_ranges:
            warnings.append(
                [messages.ERROR, f"HH size ({hh.size}) and ranges population ({total_in_ranges}) does not match"]
            )

        aaaa = active_individuals.values_list("unicef_id", flat=True)
        bbb = Household.objects.filter(unicef_id__in=aaaa)
        if bbb.count() > len(aaaa):
            warnings.append([messages.ERROR, "Unmarked duplicates found"])

        context = {
            "active_individuals": active_individuals,
            "ghosts_individuals": ghosts_individuals,
            "opts": Household._meta,
            "app_label": Household._meta.app_label,
            "original": hh,
            "head": head,
            "primary": primary,
            "alternate": alternate,
            "warnings": [(DEFAULT_TAGS[w[0]], w[1]) for w in warnings],
        }
        return TemplateResponse(request, "admin/household/household/sanity_check.html", context)


class IndividualRoleInHouseholdInline(TabularInline):
    model = IndividualRoleInHousehold
    extra = 0
    readonly_fields = ("household", "role")
    fields = ("household", "role")

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Individual)
class IndividualAdmin(
    SoftDeletableAdminMixin,
    LastSyncDateResetMixin,
    LinkedObjectsMixin,
    SmartFieldsetMixin,
    AdminAdvancedFiltersMixin,
    HOPEModelAdminBase,
):
    list_display = (
        "unicef_id",
        "given_name",
        "family_name",
        "household",
        "sex",
        "relationship",
        "birth_date",
    )
    advanced_filter_fields = (
        "updated_at",
        "last_sync_at",
        "deduplication_golden_record_status",
        "deduplication_batch_status",
        "duplicate",
        ("business_area__name", "business area"),
    )

    search_fields = ("family_name",)
    readonly_fields = ("created_at", "updated_at")
    exclude = ("created_at", "updated_at")
    inlines = [IndividualRoleInHouseholdInline]
    list_filter = (
        TextFieldFilter.factory("unicef_id__iexact", "UNICEF ID"),
        TextFieldFilter.factory("household__unicef_id__iexact", "Household ID"),
        ("deduplication_golden_record_status", ChoicesFieldComboFilter),
        ("deduplication_batch_status", ChoicesFieldComboFilter),
        ("business_area", AutoCompleteFilter),
        "updated_at",
        "last_sync_at",
    )
    raw_id_fields = ("household", "registration_data_import", "business_area")
    fieldsets = [
        (
            None,
            {
                "fields": (
                    (
                        "full_name",
                        "withdrawn",
                        "duplicate",
                        "is_removed",
                    ),
                    ("sex", "birth_date", "marital_status"),
                    ("unicef_id",),
                    ("household", "relationship"),
                )
            },
        ),
        (
            "Dates",
            {
                "classes": ("collapse",),
                "fields": (
                    ("created_at", "updated_at"),
                    "last_sync_at",
                    "removed_date",
                    "withdrawn_date",
                    "duplicate_date",
                ),
            },
        ),
        (
            "Registration",
            {
                "classes": ("collapse",),
                "fields": (
                    "registration_data_import",
                    "first_registration_date",
                    "last_registration_date",
                ),
            },
        ),
        ("Others", {"classes": ("collapse",), "fields": ("__others__",)}),
    ]

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if isinstance(db_field, JSONField):
            if is_root(request):
                kwargs = {"widget": JSONEditor}
            else:
                kwargs = {"widget": JsonWidget}
            return db_field.formfield(**kwargs)
        return super().formfield_for_dbfield(db_field, request, **kwargs)

    @button()
    def household_members(self, request, pk):
        obj = Individual.objects.get(pk=pk)
        url = reverse("admin:household_individual_changelist")
        return HttpResponseRedirect(f"{url}?household|unicef_id|iexact={obj.household.unicef_id}")

    @button()
    def sanity_check(self, request, pk):
        context = self.get_common_context(request, pk, title="Sanity Check")
        obj = context["original"]
        context["roles"] = obj.households_and_roles.all()
        context["duplicates"] = Individual.objects.filter(unicef_id=obj.unicef_id)

        return TemplateResponse(request, "admin/household/individual/sanity_check.html", context)

    def xlsx_update_stage2(self, request, old_form):
        xlsx_update_file = XlsxUpdateFile(
            file=old_form.cleaned_data["file"],
            business_area=old_form.cleaned_data["business_area"],
            rdi=old_form.cleaned_data["registration_data_import"],
        )
        xlsx_update_file.save()
        updater = IndividualXlsxUpdate(xlsx_update_file)
        context = self.get_common_context(
            request,
            title="Update Individual by xlsx",
            form=UpdateByXlsxStage2Form(
                xlsx_columns=updater.columns_names, initial={"xlsx_update_file": xlsx_update_file}
            ),
        )
        return TemplateResponse(request, "admin/household/individual/xlsx_update_stage2.html", context)

    def xlsx_update_stage3(self, request, old_form):
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
        )
        return TemplateResponse(request, "admin/household/individual/xlsx_update_stage3.html", context)

    @button()
    def xlsx_update(self, request):
        if request.method == "GET":
            context = self.get_common_context(request, title="Update Individual by xlsx", form=UpdateByXlsxStage1Form())
        if request.POST.get("stage") == "2":
            form = UpdateByXlsxStage1Form(request.POST, request.FILES)
            context = self.get_common_context(request, title="Update Individual by xlsx", form=form)
            if not form.is_valid():
                return TemplateResponse(request, "admin/household/individual/xlsx_update.html", context)
            return self.xlsx_update_stage2(request, form)
        if request.POST.get("stage") == "3":
            xlsx_update_file = XlsxUpdateFile.objects.get(pk=request.POST["xlsx_update_file"])
            updater = IndividualXlsxUpdate(xlsx_update_file)
            form = UpdateByXlsxStage2Form(request.POST, request.FILES, xlsx_columns=updater.columns_names)
            context = self.get_common_context(request, title="Update Individual by xlsx", form=form)
            if not form.is_valid():
                return TemplateResponse(request, "admin/household/individual/xlsx_update_stage2.html", context)
            return self.xlsx_update_stage3(request, form)
        return TemplateResponse(request, "admin/household/individual/xlsx_update.html", context)


@admin.register(IndividualRoleInHousehold)
class IndividualRoleInHouseholdAdmin(LastSyncDateResetMixin, HOPEModelAdminBase):
    list_display = ("individual_id", "household_id", "role")
    list_filter = ("role",)
    raw_id_fields = (
        "individual",
        "household",
    )


@admin.register(IndividualIdentity)
class IndividualIdentityAdmin(HOPEModelAdminBase):
    pass


@admin.register(EntitlementCard)
class EntitlementCardAdmin(ExtraUrlMixin, HOPEModelAdminBase):
    list_display = ("id", "card_number", "status", "card_type", "service_provider")
    search_fields = ("card_number",)
    date_hierarchy = "created_at"
    raw_id_fields = ("household",)
    list_filter = (
        "status",
        TextFieldFilter.factory("card_type"),
        TextFieldFilter.factory("service_provider"),
    )
