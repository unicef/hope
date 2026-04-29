from itertools import chain
import logging
import re
from typing import Any, cast
from uuid import UUID

from admin_cursor_paginator import CursorPaginatorAdmin
from admin_extra_buttons.decorators import button
from admin_extra_buttons.mixins import confirm_action
from adminfilters.autocomplete import LinkedAutoCompleteFilter
from adminfilters.depot.widget import DepotManager
from adminfilters.querystring import QueryStringFilter
from django.contrib import admin, messages
from django.contrib.admin import SimpleListFilter
from django.contrib.admin.helpers import ACTION_CHECKBOX_NAME
from django.contrib.messages import DEFAULT_TAGS
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.db.models import Q, QuerySet
from django.db.transaction import atomic
from django.forms import Form
from django.http import HttpRequest, HttpResponse, HttpResponseBase, HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils import timezone
from smart_admin.mixins import FieldsetMixin as SmartFieldsetMixin

from hope.admin.utils import (
    AutocompleteForeignKeyMixin,
    BusinessAreaForHouseholdCollectionListFilter,
    HOPEModelAdminBase,
    LastSyncDateResetMixin,
    LinkedObjectsManagerMixin,
    RdiMergeStatusAdminMixin,
    SoftDeletableAdminMixin,
)
from hope.apps.household.celery_tasks import (
    enroll_households_to_program_async_task,
    mass_unwithdraw_households_async_task,
    mass_withdraw_households_async_task,
)
from hope.apps.household.forms import (
    MassEnrollForm,
    MassRestoreForm,
    MassWithdrawForm,
    WithdrawForm,
    WithdrawHouseholdsForm,
)
from hope.apps.utils.security import is_root
from hope.models import (
    HEAD,
    ROLE_ALTERNATE,
    ROLE_PRIMARY,
    BusinessArea,
    Document,
    Household,
    HouseholdCollection,
    Individual,
    IndividualRoleInHousehold,
    Program,
)

logger = logging.getLogger(__name__)


class MessageRecipientFilter(SimpleListFilter):
    title = "message"
    parameter_name = "message_id"

    def lookups(self, request: HttpRequest, model_admin: Any) -> list:
        return []

    def has_output(self) -> bool:
        return bool(self.value())

    def queryset(self, request: HttpRequest, queryset: QuerySet) -> QuerySet:
        if self.value():
            return queryset.filter(messages__id=self.value())
        return queryset


class HouseholdWithDrawnMixin:
    def has_withdrawn_permission(self, request: HttpRequest) -> bool:
        return request.user.has_perm("household.withdrawn")

    def mass_withdraw(self, request: HttpRequest, qs: QuerySet) -> TemplateResponse | None:
        context = self.get_common_context(request, title="Withdrawn")
        context["op"] = "withdraw"
        context["action"] = "mass_withdraw"
        context["ticket_operation"] = "close any ticket related to the household or his members"
        if "apply" in request.POST:
            form = MassWithdrawForm(request.POST)
            if form.is_valid():
                programs_households: dict[str, list[str]] = {}
                for pk, program_id in qs.values_list("pk", "program_id"):
                    programs_households.setdefault(str(program_id), []).append(str(pk))
                for program_id, household_ids in programs_households.items():
                    mass_withdraw_households_async_task(household_ids, form.cleaned_data["tag"], program_id)
                self.message_user(request, f"{qs.count()} Households are being withdrawn.")
                return None
            context["form"] = form
            return TemplateResponse(request, "admin/household/household/mass_withdrawn.html", context)
        context["form"] = MassWithdrawForm(
            initial={
                "_selected_action": request.POST.getlist(ACTION_CHECKBOX_NAME),
                "reason": "",
                "tag": "",
            }
        )
        return TemplateResponse(request, "admin/household/household/mass_withdrawn.html", context)

    mass_withdraw.allowed_permissions = ["withdrawn"]

    def mass_unwithdraw(self, request: HttpRequest, qs: QuerySet) -> TemplateResponse | None:
        context = self.get_common_context(request, title="Restore")
        context["action"] = "mass_unwithdraw"
        context["op"] = "restore"
        context["ticket_operation"] = "reopen any previously closed tickets relating to the household or its members"
        context["queryset"] = qs
        if "apply" in request.POST:
            form = MassRestoreForm(request.POST)
            if form.is_valid():
                programs_households: dict[str, list[str]] = {}
                for pk, program_id in qs.values_list("pk", "program_id"):
                    programs_households.setdefault(str(program_id), []).append(str(pk))
                for program_id, household_ids in programs_households.items():
                    mass_unwithdraw_households_async_task(
                        household_ids, program_id, reopen_tickets=form.cleaned_data["reopen_tickets"]
                    )
                self.message_user(request, f"{qs.count()} Households are being restored.")
                return None
            context["form"] = form
            return TemplateResponse(request, "admin/household/household/mass_withdrawn.html", context)
        context["form"] = MassRestoreForm(
            initial={
                "reopen_tickets": True,
                "_selected_action": request.POST.getlist(ACTION_CHECKBOX_NAME),
            }
        )
        return TemplateResponse(request, "admin/household/household/mass_withdrawn.html", context)

    mass_unwithdraw.allowed_permissions = ["withdrawn"]

    @button(permission="household.withdrawn")
    def withdraw(self, request: HttpRequest, pk: UUID) -> HttpResponseRedirect | TemplateResponse:
        from hope.apps.grievance.models import GrievanceTicket
        from hope.apps.household.services.bulk_withdraw import HouseholdBulkWithdrawService

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
        form: Form | WithdrawForm
        if request.method == "POST":
            form = WithdrawForm(request.POST)
            if form.is_valid():
                try:
                    with atomic():
                        qs = Household.objects.filter(pk=obj.pk)
                        if obj.withdrawn:
                            HouseholdBulkWithdrawService(obj.program).unwithdraw(qs)
                            log_message = "{target} has been restored by {user}."
                        else:
                            HouseholdBulkWithdrawService(obj.program).withdraw(qs, form.cleaned_data["tag"])
                            log_message = "{target} has been withdrawn by {user}."
                        for individual in Individual.objects.filter(household=obj, duplicate=False).order_by("pk"):
                            self.log_change(
                                request,
                                individual,
                                log_message.format(target="Individual", user=request.user.username),
                            )
                        self.log_change(
                            request,
                            obj,
                            log_message.format(target="Household", user=request.user.username),
                        )
                        self.message_user(request, msg, messages.SUCCESS)
                        return HttpResponseRedirect(request.path)
                except (ValueError, ObjectDoesNotExist) as e:
                    self.message_user(request, str(e), messages.ERROR)
        else:
            context["form"] = (
                Form() if obj.withdrawn else WithdrawForm(initial={"tag": timezone.now().strftime("%Y%m%d%H%M%S")})
            )

        context["tickets"] = tickets
        return TemplateResponse(request, "admin/household/household/withdrawn.html", context)

    @staticmethod
    def get_household_queryset_from_list(household_id_list: list[str], program: Program) -> QuerySet:
        return Household.objects.filter(
            unicef_id__in=household_id_list,
            withdrawn=False,
            program=program,
        )

    @staticmethod
    def split_list_of_ids(household_list: str) -> list:
        """Split input list of ids by literal 'new line' or any of "," "|" "/" or white spaces."""
        return [hh_id.strip() for hh_id in re.split(r"new line|[,\|/\s]+", household_list) if hh_id]

    @staticmethod
    def get_and_set_context_data(request: HttpRequest, context: dict) -> None:
        context["household_list"] = request.POST.get("household_list")
        context["tag"] = request.POST.get("tag")
        context["program"] = request.POST.get("program")
        context["business_area"] = request.POST.get("business_area")

    def withdraw_households_from_list(self, request: HttpRequest) -> HttpResponse | None:
        step = request.POST.get("step", "0")
        context = self.get_common_context(request, title="Withdraw households from list")

        if step == "0":
            context["form"] = WithdrawHouseholdsForm()
            context["step"] = "0"
            return TemplateResponse(
                request,
                "admin/household/household/withdraw_households_from_list.html",
                context,
            )

        if step == "1":
            business_area = request.POST.get("business_area")
            request.session["business_area"] = business_area
            context.update(
                {
                    "form": WithdrawHouseholdsForm(request.POST, business_area=business_area),
                    "business_area": business_area,
                    "step": "1",
                }
            )
            return TemplateResponse(
                request,
                "admin/household/household/withdraw_households_from_list.html",
                context,
            )

        business_area = request.session.get("business_area")
        form = WithdrawHouseholdsForm(request.POST, business_area=business_area)
        context["form"] = form

        if form.is_valid():
            household_id_list = self.split_list_of_ids(form.cleaned_data["household_list"])
            program = form.cleaned_data["program"]
            tag = form.cleaned_data["tag"]

            if step == "2":
                context.update(
                    {
                        "step": "2",
                        "household_count": self.get_household_queryset_from_list(household_id_list, program).count(),
                    }
                )
                self.get_and_set_context_data(request, context)
                return TemplateResponse(
                    request,
                    "admin/household/household/withdraw_households_from_list.html",
                    context,
                )

            if step == "3":
                household_ids = list(
                    self.get_household_queryset_from_list(household_id_list, program).values_list("pk", flat=True)
                )
                mass_withdraw_households_async_task(
                    [str(pk) for pk in household_ids], tag, str(program.id)
                )
                self.message_user(request, f"{len(household_ids)} Households are being withdrawn.")
                return HttpResponseRedirect(reverse("admin:household_household_changelist"))
        return TemplateResponse(
            request,
            "admin/household/household/withdraw_households_from_list.html",
            context,
        )

    @button(
        label="Withdraw households from list",
        permission="household.withdrawn",
    )
    def withdraw_households_from_list_button(self, request: HttpRequest) -> HttpResponse | None:
        return self.withdraw_households_from_list(request)


class HouseholdRepresentationInline(admin.TabularInline):
    model = Household
    extra = 0
    fields = ("unicef_id", "program")
    readonly_fields = ("unicef_id", "program")
    show_change_link = True
    can_delete = False
    verbose_name_plural = "Household representations"

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        return Household.all_objects.all().select_related("program").only("unicef_id", "copied_from", "program__name")

    def has_add_permission(self, request: HttpRequest, obj: Household | None = None) -> bool:
        return False  # Disable adding new individual representations inline


class RepresentativesInline(AutocompleteForeignKeyMixin, admin.TabularInline):
    model = IndividualRoleInHousehold
    extra = 1


@admin.register(Household)
class HouseholdAdmin(
    SoftDeletableAdminMixin,
    LastSyncDateResetMixin,
    LinkedObjectsManagerMixin,
    SmartFieldsetMixin,
    CursorPaginatorAdmin,
    HouseholdWithDrawnMixin,
    HOPEModelAdminBase,
    RdiMergeStatusAdminMixin,
):
    list_display = (
        "unicef_id",
        "business_area",
        "country",
        "program",
        "head_of_household",
        "rdi_merge_status",
        "registration_data_import",
        "registration_method",
        "residence_status",
        "collect_type",
        "withdrawn",
        "size",
        "consent",
        "consent_sharing",
    )
    list_filter = (
        DepotManager,
        QueryStringFilter,
        MessageRecipientFilter,
        ("business_area", LinkedAutoCompleteFilter.factory(parent=None)),
        ("program", LinkedAutoCompleteFilter.factory(parent="business_area")),
        ("facility__name", LinkedAutoCompleteFilter.factory(parent="business_area", title="Facility")),
        (
            "registration_data_import",
            LinkedAutoCompleteFilter.factory(parent="program"),
        ),
        "registration_method",
        "residence_status",
        "collect_type",
        "withdrawn",
        "consent",
        "consent_sharing",
    )
    search_fields = ("head_of_household__family_name", "unicef_id")
    readonly_fields = (
        "created_at",
        "updated_at",
        "extra_rdis",
        "detail_id",
        "originating_id",
        # property fields
        "geopoint",
    )
    fieldsets = [
        (
            None,
            {
                "fields": (
                    ("unicef_id", "head_of_household"),
                    ("program", "business_area"),
                    "withdrawn",
                ),
            },
        ),
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
                    "detail_id",
                    "originating_id",
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
        (
            "Location",
            {
                "classes": ("collapse",),
                "fields": (
                    ("country", "country_origin"),
                    ("admin1", "admin2"),
                    ("admin3", "admin4"),
                    "address",
                    "village",
                    "zip_code",
                    "geopoint",
                ),
            },
        ),
        (
            "Demographics",
            {
                "classes": ("collapse",),
                "fields": (
                    "male_children_count",
                    "female_children_count",
                    "children_disabled_count",
                    "pregnant_count",
                    "other_sex_group_count",
                    "female_age_group_0_5_count",
                    "female_age_group_6_11_count",
                    "female_age_group_12_17_count",
                    "female_age_group_18_59_count",
                    "female_age_group_60_count",
                    "male_age_group_0_5_count",
                    "male_age_group_6_11_count",
                    "male_age_group_12_17_count",
                    "male_age_group_18_59_count",
                    "male_age_group_60_count",
                    "female_age_group_0_5_disabled_count",
                    "female_age_group_6_11_disabled_count",
                    "female_age_group_12_17_disabled_count",
                    "female_age_group_18_59_disabled_count",
                    "female_age_group_60_disabled_count",
                    "male_age_group_0_5_disabled_count",
                    "male_age_group_6_11_disabled_count",
                    "male_age_group_12_17_disabled_count",
                    "male_age_group_18_59_disabled_count",
                    "male_age_group_60_disabled_count",
                ),
            },
        ),
        ("Others", {"classes": ("collapse",), "fields": ("__others__",)}),
    ]
    actions = [
        "mass_withdraw",
        "mass_unwithdraw",
        "count_queryset",
        "create_target_population",
        "add_to_target_population",
        "mass_enroll_to_another_program",
    ]
    cursor_ordering_field = "unicef_id"
    inlines = [HouseholdRepresentationInline, RepresentativesInline]
    show_full_result_count = False

    def geopoint(self, obj: Household) -> str | None:
        return obj.geopoint

    geopoint.short_description = "Geopoint (lat, lon)"

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        qs = self.model.all_objects.get_queryset().select_related(
            "business_area",
            "head_of_household",
            "country",
            "country_origin",
            "admin1",
            "admin2",
            "admin3",
            "admin4",
            "program",
            "registration_data_import",
            "facility",
        )
        ordering = self.get_ordering(request)
        if ordering:
            qs = qs.order_by(*ordering)
        return qs

    def formfield_for_foreignkey(self, db_field: Any, request: HttpRequest, **kwargs: Any) -> Any:
        if db_field.name == "head_of_household":
            kwargs["queryset"] = Individual.all_objects.all()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_ignored_linked_objects(self, request: HttpRequest) -> list:
        return []

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False

    def has_delete_permission(self, request: HttpRequest, obj: Any | None = None) -> bool:
        return False

    @button(permission="grievance.view_grievanceticket")
    def tickets(self, request: HttpRequest, pk: UUID) -> TemplateResponse:
        context = self.get_common_context(request, pk, title="Tickets")
        obj = context["original"]
        tickets = [
            entry.ticket for entry in chain(obj.sensitive_ticket_details.all(), obj.complaint_ticket_details.all())
        ]
        context["tickets"] = tickets
        return TemplateResponse(request, "admin/household/household/tickets.html", context)

    @button(permission="grievance.view_grievanceticket")
    def linked_grievances(self, request: HttpRequest, pk: UUID) -> HttpResponseRedirect:
        obj = Household.all_merge_status_objects.get(pk=pk)
        url = reverse("admin:grievance_grievanceticket_changelist")
        return HttpResponseRedirect(f"{url}?household_unicef_id={obj.unicef_id}")

    @button(permission="household.view_household")
    def members(self, request: HttpRequest, pk: UUID) -> HttpResponseRedirect:
        obj = Household.all_merge_status_objects.get(pk=pk)
        url = reverse("admin:household_individual_changelist")
        return HttpResponseRedirect(f"{url}?household__id__exact={obj.id}")

    @button(
        permission=lambda request, obj, handler: is_root(request) and request.user.has_perm("household.sanity_check")
    )
    def sanity_check(self, request: HttpRequest, pk: UUID) -> TemplateResponse:
        # NOTE: this code should be optimized in the future, and it is not intended to be used in bulk
        hh = self.get_object(request, str(pk))
        warnings: list[list] = []
        primary = None
        head = None
        try:
            primary = IndividualRoleInHousehold.all_objects.get(household=hh, role=ROLE_PRIMARY)
        except ObjectDoesNotExist:
            warnings.append([messages.ERROR, "Head of househould not found"])

        alternate = IndividualRoleInHousehold.all_objects.filter(household=hh, role=ROLE_ALTERNATE).first()
        try:
            head = hh.individuals(manager="all_objects").get(relationship=HEAD)
        except ObjectDoesNotExist:
            warnings.append([messages.ERROR, "Head of househould not found"])

        total_in_ranges = 0
        for gender in ["male", "female"]:
            for num_range in ["0_5", "6_11", "12_17", "18_59", "60"]:
                field = f"{gender}_age_group_{num_range}_count"
                total_in_ranges += getattr(hh, field, 0) or 0

        active_individuals = hh.individuals(manager="all_objects").exclude(Q(duplicate=True) | Q(withdrawn=True))
        ghosts_individuals = hh.individuals(manager="all_objects").filter(Q(duplicate=True) | Q(withdrawn=True))

        if hh.size != total_in_ranges:
            warnings.append(
                [
                    messages.ERROR,
                    f"HH size ({hh.size}) and ranges population ({total_in_ranges}) does not match",
                ]
            )

        aaaa = active_individuals.values_list("unicef_id", flat=True)
        bbb = Household.all_objects.filter(unicef_id__in=aaaa)
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

    @button(
        permission=lambda request, obj, handler: (
            is_root(request) and obj.can_be_erase() and request.user.has_perm("household.gdpr_remove")
        )
    )
    def gdpr_remove(self, request: HttpRequest, pk: UUID) -> HttpResponseBase | None:
        household: Household = cast("Household", self.get_queryset(request).get(pk=pk))
        if request.method == "POST":
            try:
                with transaction.atomic():
                    household.erase()
                self.message_user(
                    request,
                    f"Household {household.unicef_id} erased.",
                    messages.SUCCESS,
                )
            except ObjectDoesNotExist as e:
                self.message_user(request, str(e), messages.ERROR)
            return HttpResponseRedirect(reverse("admin:household_household_change", args=[pk]))
        return confirm_action(
            self,
            request,
            self.gdpr_remove,
            """<h1>Household erase</h1>
            <p>After this operation household will be erased, all sensitive data will be overwritten.</p>
            <p>This operation cannot be undo.</p>
            """,
            "Successfully executed",
        )

    @button(
        permission=lambda request, household, *args, **kwargs: (
            is_root(request) and request.user.has_perm("household.logical_delete") and not household.is_removed
        )
    )
    def logical_delete(self, request: HttpRequest, pk: UUID) -> HttpResponseBase | None:
        household: Household = cast("Household", self.get_queryset(request).get(pk=pk))
        if request.method == "POST":
            try:
                household.delete()
                self.message_user(
                    request,
                    f"Household {household.unicef_id} was soft removed.",
                    messages.SUCCESS,
                )
            except ObjectDoesNotExist as e:
                self.message_user(request, str(e), messages.ERROR)
            return HttpResponseRedirect(reverse("admin:household_household_change", args=[pk]))
        return confirm_action(
            self,
            request,
            self.logical_delete,
            """<h1>Household logical delete</h1>
                <p>After this operation household will be marked as logical deleted
                 and will be hidden in the application.</p>
                """,
            "Successfully executed",
        )

    def mass_enroll_to_another_program(self, request: HttpRequest, qs: QuerySet) -> HttpResponse | None:
        context = self.get_common_context(request, title="Mass enroll households to another program")
        business_area_id = qs.first().business_area_id
        if "apply" in request.POST or "acknowledge" in request.POST:
            form = MassEnrollForm(request.POST, business_area_id=business_area_id, households=qs)
            if form.is_valid():
                program_for_enroll = form.cleaned_data["program_for_enroll"]
                households_ids = list(qs.distinct("unicef_id").values_list("id", flat=True))
                enroll_households_to_program_async_task(
                    households_ids=households_ids,
                    program_for_enroll_id=program_for_enroll,
                    user_id=str(request.user.id),
                )
                self.message_user(
                    request,
                    f"Enrolling households to program: {program_for_enroll}",
                    level=messages.SUCCESS,
                )
                return None
        elif not all(obj.business_area_id == business_area_id for obj in qs):
            # Check if all selected objects have the same business_area
            self.message_user(
                request,
                "Selected households need to belong to the same business area",
                level=messages.ERROR,
            )
            return None
        form = MassEnrollForm(request.POST, business_area_id=business_area_id, households=qs)
        context["form"] = form
        context["action"] = "mass_enroll_to_another_program"
        return TemplateResponse(
            request,
            "admin/household/household/enroll_households_to_program_async_task.html",
            context,
        )

    mass_enroll_to_another_program.short_description = "Mass enroll households to another program"


@admin.register(HouseholdCollection)
class HouseholdCollectionAdmin(AutocompleteForeignKeyMixin, admin.ModelAdmin):
    list_display = (
        "unicef_id",
        "business_area",
        "number_of_representations",
    )
    search_fields = ("unicef_id",)
    list_filter = [BusinessAreaForHouseholdCollectionListFilter]
    inlines = [HouseholdRepresentationInline]

    def get_queryset(self, request: HttpRequest) -> "QuerySet":
        return (
            super()
            .get_queryset(request)
            .prefetch_related(
                "households",
            )
        )

    def number_of_representations(self, obj: HouseholdCollection) -> int:
        return obj.households(manager="all_objects").count()

    def business_area(self, obj: HouseholdCollection) -> BusinessArea | None:
        return obj.business_area
