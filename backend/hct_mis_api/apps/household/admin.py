import logging
from itertools import chain
from typing import Iterable

from django.contrib import admin, messages
from django.contrib.admin import TabularInline
from django.contrib.admin.helpers import ACTION_CHECKBOX_NAME
from django.contrib.messages import DEFAULT_TAGS
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.db.models import JSONField, Q
from django.db.transaction import atomic
from django.forms import Form
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils import timezone

from admin_cursor_paginator import CursorPaginatorAdmin
from admin_extra_buttons.decorators import button
from adminfilters.autocomplete import AutoCompleteFilter
from adminfilters.depot.widget import DepotManager
from adminfilters.filters import (
    ChoicesFieldComboFilter,
    RelatedFieldComboFilter,
    ValueFilter,
)
from adminfilters.querystring import QueryStringFilter
from jsoneditor.forms import JSONEditor
from smart_admin.mixins import FieldsetMixin as SmartFieldsetMixin
from smart_admin.mixins import LinkedObjectsMixin

from hct_mis_api.apps.administration.widgets import JsonWidget
from hct_mis_api.apps.household.celery_tasks import (
    update_individuals_iban_from_xlsx_task,
)
from hct_mis_api.apps.household.forms import (
    MassWithdrawForm,
    RestoreForm,
    UpdateByXlsxStage1Form,
    UpdateByXlsxStage2Form,
    UpdateIndividualsIBANFromXlsxForm,
    WithdrawForm,
)
from hct_mis_api.apps.household.models import (
    HEAD,
    ROLE_ALTERNATE,
    ROLE_PRIMARY,
    Agency,
    BankAccountInfo,
    Document,
    DocumentType,
    EntitlementCard,
    Household,
    Individual,
    IndividualIdentity,
    IndividualRoleInHousehold,
    XlsxUpdateFile,
)
from hct_mis_api.apps.household.services.household_withdraw import HouseholdWithdraw
from hct_mis_api.apps.household.services.individual_xlsx_update import (
    IndividualXlsxUpdate,
    InvalidColumnsError,
)
from hct_mis_api.apps.power_query.mixin import PowerQueryMixin
from hct_mis_api.apps.utils.admin import (
    HOPEModelAdminBase,
    LastSyncDateResetMixin,
    SoftDeletableAdminMixin,
)
from hct_mis_api.apps.utils.security import is_root

logger = logging.getLogger(__name__)


@admin.register(Agency)
class AgencyAdmin(HOPEModelAdminBase):
    search_fields = ("label", "country")
    list_display = ("label", "type", "country")
    list_filter = (
        "type",
        ("country", ValueFilter.factory(label="Country ISO CODE 2")),
    )
    autocomplete_fields = ("country",)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("country")


@admin.register(Document)
class DocumentAdmin(SoftDeletableAdminMixin, HOPEModelAdminBase):
    search_fields = ("document_number", "country")
    list_display = ("document_number", "type", "country", "status", "individual")
    raw_id_fields = ("individual",)
    list_filter = (
        ("type", RelatedFieldComboFilter),
        ("individual", AutoCompleteFilter),
    )
    autocomplete_fields = ["type"]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("individual", "type", "type__country")


@admin.register(DocumentType)
class DocumentTypeAdmin(HOPEModelAdminBase):
    search_fields = ("label",)
    list_display = ("label", "type")
    list_filter = (
        "type",
        "label",
    )

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related(
                "country",
            )
        )


@admin.register(Household)
class HouseholdAdmin(
    SoftDeletableAdminMixin,
    LastSyncDateResetMixin,
    LinkedObjectsMixin,
    PowerQueryMixin,
    SmartFieldsetMixin,
    CursorPaginatorAdmin,
    HOPEModelAdminBase,
):
    list_display = (
        "unicef_id",
        "country",
        "head_of_household",
        "size",
        "withdrawn",
    )
    list_filter = (
        DepotManager,
        ("business_area", AutoCompleteFilter),
        QueryStringFilter,
        "withdrawn",
    )
    search_fields = ("head_of_household__family_name", "unicef_id")
    readonly_fields = ("created_at", "updated_at")
    filter_horizontal = ("representatives", "programs")
    raw_id_fields = (
        "admin_area",
        "business_area",
        "country",
        "country_origin",
        "currency",
        "head_of_household",
        "registration_data_import",
    )
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
    actions = ["mass_withdraw", "mass_unwithdraw", "count_queryset"]
    cursor_ordering_field = "unicef_id"

    def get_queryset(self, request):
        qs = self.model.all_objects.get_queryset().select_related(
            "head_of_household", "country", "country_origin", "admin_area"
        )
        ordering = self.get_ordering(request)
        if ordering:
            qs = qs.order_by(*ordering)
        return qs

    def get_ignored_linked_objects(self, request):
        return []

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def _toggle_withdraw_status(self, request, hh: Household, tickets: Iterable = None, comment=None, tag=None):
        from hct_mis_api.apps.grievance.models import GrievanceTicket

        if tickets is None:
            tickets = GrievanceTicket.objects.belong_household(hh)
            if hh.withdrawn:
                tickets = filter(lambda t: t.ticket.extras.get("status_before_withdrawn", False), tickets)
            else:
                tickets = filter(lambda t: t.ticket.status != GrievanceTicket.STATUS_CLOSED, tickets)
        service = HouseholdWithdraw(hh)
        service.change_tickets_status(tickets)
        if hh.withdrawn:
            hh.unwithdraw()
            message = "{target} has been restored by {user}. {comment}"
            ticket_message = "Ticket reopened due to Household restore"
        else:
            hh.withdraw(tag=tag)
            message = "{target} has been withdrawn by {user}. {comment}"
            ticket_message = "Ticket closed due to Household withdrawn"

        for individual in service.individuals:
            self.log_change(
                request, individual, message.format(target="Individual", user=request.user.username, comment=comment)
            )

        for ticket in tickets:
            self.log_change(request, ticket.ticket, ticket_message)
        self.log_change(request, hh, message.format(target="Household", user=request.user.username, comment=comment))

        return service

    def has_withdrawn_permission(self, request):
        return request.user.has_perm("household.can_withdrawn")

    def mass_withdraw(self, request, qs):
        context = self.get_common_context(request, title="Withdrawn")
        context["op"] = "withdraw"
        context["action"] = "mass_withdraw"
        context["ticket_operation"] = "close any ticket related to the household or his members"
        results = 0
        if "apply" in request.POST:
            form = MassWithdrawForm(request.POST)
            if form.is_valid():
                with atomic():
                    for hh in qs.filter(withdrawn=False):
                        service = self._toggle_withdraw_status(
                            request, hh, tag=form.cleaned_data["tag"], comment=form.cleaned_data["reason"]
                        )
                        if service.household.withdraw:
                            results += 1
                self.message_user(request, f"Changed {results} Households.")
            else:
                context["form"] = form
                return TemplateResponse(request, "admin/household/household/mass_withdrawn.html", context)
        else:
            context["form"] = MassWithdrawForm(
                initial={"_selected_action": request.POST.getlist(ACTION_CHECKBOX_NAME), "reason": "", "tag": ""}
            )
            return TemplateResponse(request, "admin/household/household/mass_withdrawn.html", context)

    mass_withdraw.allowed_permissions = ["household.can_withdrawn"]

    def mass_unwithdraw(self, request, qs):
        context = self.get_common_context(request, title="Restore")
        context["action"] = "mass_unwithdraw"
        context["op"] = "restore"
        context["ticket_operation"] = "reopen any previously closed tickets relating to the household or its members"
        context["queryset"] = qs
        results = 0
        if "apply" in request.POST:
            form = RestoreForm(request.POST)
            if form.is_valid():
                with atomic():
                    if form.cleaned_data["reopen_tickets"]:
                        tickets = None
                    else:
                        tickets = []
                    for hh in qs.filter(withdrawn=True):
                        service = self._toggle_withdraw_status(
                            request, hh, tickets=tickets, comment=form.cleaned_data["reason"]
                        )
                        if not service.household.withdraw:
                            results += 1
                self.message_user(request, f"Changed {results} Households.")
            else:
                context["form"] = form
                return TemplateResponse(request, "admin/household/household/mass_withdrawn.html", context)
        else:
            context["form"] = RestoreForm(
                initial={"reopen_tickets": True, "_selected_action": request.POST.getlist(ACTION_CHECKBOX_NAME)}
            )
            return TemplateResponse(request, "admin/household/household/mass_withdrawn.html", context)

    mass_withdraw.allowed_permissions = ["withdrawn"]

    @button(permission="household.can_withdrawn")
    def withdraw(self, request, pk):
        from hct_mis_api.apps.grievance.models import GrievanceTicket

        context = self.get_common_context(request, pk)

        obj: Household = context["original"]
        context["status"] = "" if obj.withdrawn else "checked"

        tickets = GrievanceTicket.objects.belong_household(obj)
        if obj.withdrawn:
            msg = "Household successfully restored"
            context["title"] = "Restore"
            tickets = filter(lambda t: t.ticket.extras.get("status_before_withdrawn", False), tickets)
        else:
            context["title"] = "Withdrawn"
            msg = "Household successfully withdrawn"
            tickets = filter(lambda t: t.ticket.status != GrievanceTicket.STATUS_CLOSED, tickets)

        if request.method == "POST":
            form = WithdrawForm(request.POST)
            if form.is_valid():
                try:
                    with atomic():
                        self._toggle_withdraw_status(request, obj, tickets, tag=form.cleaned_data["tag"])
                        self.message_user(request, msg, messages.SUCCESS)
                        return HttpResponseRedirect(request.path)
                except Exception as e:
                    self.message_user(request, str(e), messages.ERROR)
        else:
            if obj.withdrawn:
                form = Form()
            else:
                form = WithdrawForm(initial={"tag": timezone.now().strftime("%Y%m%d%H%M%S")})

        context["form"] = form
        context["tickets"] = tickets
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
        return HttpResponseRedirect(f"{url}?qs=unicef_id={obj.unicef_id}")

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
        except ObjectDoesNotExist:
            warnings.append([messages.ERROR, "Head of househould not found"])

        alternate = IndividualRoleInHousehold.objects.filter(household=hh, role=ROLE_ALTERNATE).first()
        try:
            head = hh.individuals.get(relationship=HEAD)
        except ObjectDoesNotExist:
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
                [
                    messages.ERROR,
                    f"HH size ({hh.size}) and ranges population ({total_in_ranges}) does not match",
                ]
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


class BankAccountInfoStackedInline(admin.StackedInline):
    model = BankAccountInfo

    exclude = ("debit_card_number",)
    extra = 0


@admin.register(Individual)
class IndividualAdmin(
    SoftDeletableAdminMixin,
    LastSyncDateResetMixin,
    LinkedObjectsMixin,
    SmartFieldsetMixin,
    CursorPaginatorAdmin,
    HOPEModelAdminBase,
):
    # Custom template to merge AdminAdvancedFiltersMixin and ExtraButtonsMixin
    advanced_change_list_template = "admin/household/advanced_filters_extra_buttons_change_list.html"
    cursor_ordering_field = "unicef_id"

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

    search_fields = ("family_name", "unicef_id")
    readonly_fields = ("created_at", "updated_at", "registration_data_import")
    exclude = ("created_at", "updated_at")
    list_filter = (
        DepotManager,
        QueryStringFilter,
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
    actions = ["count_queryset"]

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related(
                "household",
                "registration_data_import",
            )
        )

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
        flt = f"&qs=household_id={obj.household.id}&qs__negate=false"
        return HttpResponseRedirect(f"{url}?{flt}")

    @button(html_attrs={"class": "aeb-green"})
    def sanity_check(self, request, pk):
        context = self.get_common_context(request, pk, title="Sanity Check")
        obj = context["original"]
        context["roles"] = obj.households_and_roles.all()
        context["duplicates"] = Individual.objects.filter(unicef_id=obj.unicef_id)

        return TemplateResponse(request, "admin/household/individual/sanity_check.html", context)

    @button(label="Add/Update Individual IBAN by xlsx")
    def add_update_individual_iban_from_xlsx(self, request):
        if request.method == "GET":
            form = UpdateIndividualsIBANFromXlsxForm()
            context = self.get_common_context(request, title="Add/Update Individual IBAN by xlsx", form=form)
            return TemplateResponse(request, "admin/household/individual/individuals_iban_xlsx_update.html", context)
        else:
            form = UpdateIndividualsIBANFromXlsxForm(request.POST, request.FILES)
            if form.is_valid():
                try:
                    with transaction.atomic():
                        xlsx_update_file = XlsxUpdateFile(
                            file=form.cleaned_data["file"],
                            business_area=form.cleaned_data["business_area"],
                            uploaded_by=request.user,
                        )
                        xlsx_update_file.save()

                        transaction.on_commit(
                            lambda: update_individuals_iban_from_xlsx_task.delay(xlsx_update_file.id, request.user.id)
                        )

                        self.message_user(
                            request,
                            f"Started IBAN update for {form.cleaned_data['business_area']}, results will be send to {request.user.email}",
                            messages.SUCCESS,
                        )
                        return redirect(reverse("admin:household_individual_changelist"))

                except Exception as e:
                    self.message_user(request, f"{e.__class__.__name__}: {str(e)}", messages.ERROR)

            else:
                context = self.get_common_context(request, title="Add/Update Individual IBAN by xlsx", form=form)
                return TemplateResponse(
                    request, "admin/household/individual/individuals_iban_xlsx_update.html", context
                )


@admin.register(IndividualRoleInHousehold)
class IndividualRoleInHouseholdAdmin(LastSyncDateResetMixin, HOPEModelAdminBase):
    list_display = ("individual", "household", "role")
    list_filter = (
        DepotManager,
        QueryStringFilter,
        "role",
    )
    raw_id_fields = (
        "individual",
        "household",
    )

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related(
                "individual",
                "household",
            )
        )


@admin.register(IndividualIdentity)
class IndividualIdentityAdmin(HOPEModelAdminBase):
    list_display = ("agency", "individual", "number")
    list_filter = (("individual__unicef_id", ValueFilter.factory(label="Individual's UNICEF Id")),)
    # autocomplete_fields = ["agency", "individual"]
    raw_id_fields = (
        "individual",
        "agency",
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("individual", "agency")


@admin.register(EntitlementCard)
class EntitlementCardAdmin(HOPEModelAdminBase):
    list_display = ("id", "card_number", "status", "card_type", "service_provider")
    search_fields = ("card_number",)
    date_hierarchy = "created_at"
    raw_id_fields = ("household",)
    list_filter = ("status", ("card_type", ValueFilter), ("service_provider", ValueFilter))


@admin.register(XlsxUpdateFile)
class XlsxUpdateFileAdmin(HOPEModelAdminBase):
    readonly_fields = ("file", "business_area", "rdi", "xlsx_match_columns", "uploaded_by")
    list_filter = (
        ("business_area", AutoCompleteFilter),
        ("uploaded_by", AutoCompleteFilter),
    )

    def xlsx_update_stage2(self, request, old_form):
        xlsx_update_file = XlsxUpdateFile(
            file=old_form.cleaned_data["file"],
            business_area=old_form.cleaned_data["business_area"],
            rdi=old_form.cleaned_data["registration_data_import"],
            uploaded_by=request.user,
        )
        xlsx_update_file.save()
        try:
            updater = IndividualXlsxUpdate(xlsx_update_file)
        except InvalidColumnsError as e:
            self.message_user(request, str(e), messages.ERROR)
            context = self.get_common_context(request, title="Update Individual by xlsx", form=UpdateByXlsxStage1Form())
            return TemplateResponse(request, "admin/household/individual/xlsx_update.html", context)

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
            xlsx_update_file=xlsx_update_file.id,
        )
        return TemplateResponse(request, "admin/household/individual/xlsx_update_stage3.html", context)

    def add_view(self, request, form_url="", extra_context=None):
        return self.xlsx_update(request)

    def xlsx_update(self, request):
        if request.method == "GET":
            form = UpdateByXlsxStage1Form()
            # form.fields["registration_data_import"].widget = AutocompleteWidget(RegistrationDataImport, self.admin_site)
            # form.fields["business_area"].widget = AutocompleteWidget(BusinessArea, self.admin_site)
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
                return TemplateResponse(request, "admin/household/individual/xlsx_update_stage3.html", context)

        return TemplateResponse(request, "admin/household/individual/xlsx_update.html", context)
