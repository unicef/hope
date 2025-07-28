import logging
import re
from itertools import chain
from typing import Any
from uuid import UUID

from django.contrib import admin, messages
from django.contrib.messages import DEFAULT_TAGS
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.db.models import F, Q, QuerySet, Value
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils import timezone
from django.utils.safestring import mark_safe

from admin_cursor_paginator import CursorPaginatorAdmin
from admin_extra_buttons.decorators import button
from admin_extra_buttons.mixins import confirm_action
from adminfilters.autocomplete import LinkedAutoCompleteFilter
from adminfilters.depot.widget import DepotManager
from adminfilters.querystring import QueryStringFilter
from smart_admin.mixins import FieldsetMixin as SmartFieldsetMixin

from hct_mis_api.admin.household_admin.mixins import HouseholdWithDrawnMixin
from hct_mis_api.admin.utils_admin import (
    BusinessAreaForHouseholdCollectionListFilter,
    HOPEModelAdminBase,
    LastSyncDateResetMixin,
    LinkedObjectsManagerMixin,
    RdiMergeStatusAdminMixin,
    SoftDeletableAdminMixin,
)
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.core.utils import JSONBSet
from hct_mis_api.apps.grievance.models import GrievanceTicket
from hct_mis_api.apps.household.celery_tasks import (
    enroll_households_to_program_task,
    mass_withdraw_households_from_list_task,
)
from hct_mis_api.apps.household.forms import MassEnrollForm, WithdrawHouseholdsForm
from hct_mis_api.apps.household.models import (
    HEAD,
    ROLE_ALTERNATE,
    ROLE_PRIMARY,
    Document,
    Household,
    HouseholdCollection,
    Individual,
    IndividualRoleInHousehold,
)
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.utils.security import is_root

logger = logging.getLogger(__name__)


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


class HouseholdWithdrawFromListMixin:
    @staticmethod
    def get_household_queryset_from_list(household_id_list: list, program: Program) -> QuerySet:
        return Household.objects.filter(
            unicef_id__in=household_id_list,
            withdrawn=False,
            program=program,
        )

    @transaction.atomic
    def mass_withdraw_households_from_list_bulk(self, household_id_list: list, tag: str, program: Program) -> None:
        households = self.get_household_queryset_from_list(household_id_list, program)
        individuals = Individual.objects.filter(household__in=households, withdrawn=False, duplicate=False)

        tickets = GrievanceTicket.objects.belong_households_individuals(households, individuals)
        ticket_ids = [t.ticket.id for t in tickets]
        for status, _ in GrievanceTicket.STATUS_CHOICES:
            if status == GrievanceTicket.STATUS_CLOSED:
                continue
            GrievanceTicket.objects.filter(id__in=ticket_ids, status=status).update(
                extras=JSONBSet(F("extras"), Value("{status_before_withdrawn}"), Value(f'"{status}"')),
                status=GrievanceTicket.STATUS_CLOSED,
            )

        Document.objects.filter(individual__in=individuals).update(status=Document.STATUS_INVALID)

        individuals.update(
            withdrawn=True,
            withdrawn_date=timezone.now(),
        )
        households.update(
            withdrawn=True,
            withdrawn_date=timezone.now(),
            internal_data=JSONBSet(F("internal_data"), Value("{withdrawn_tag}"), Value(f'"{tag}"')),
        )

    @staticmethod
    def split_list_of_ids(household_list: str) -> list:
        """
        Split input list of ids by literal 'new line' or any of the following characters: "," "|" "/" or white spaces
        """
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
            return TemplateResponse(request, "admin/household/household/withdraw_households_from_list.html", context)

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
            return TemplateResponse(request, "admin/household/household/withdraw_households_from_list.html", context)

        business_area = request.session.get("business_area")
        form = WithdrawHouseholdsForm(request.POST, business_area=business_area)
        context["form"] = form

        if form.is_valid():
            household_id_list = [hh_id.strip() for hh_id in form.cleaned_data["household_list"].split(",")]
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
                    request, "admin/household/household/withdraw_households_from_list.html", context
                )

            if step == "3":
                mass_withdraw_households_from_list_task.delay(household_id_list, tag, str(program.id))
                self.message_user(request, f"{len(household_id_list)} Households are being withdrawn.")
                return HttpResponseRedirect(reverse("admin:household_household_changelist"))
        return TemplateResponse(request, "admin/household/household/withdraw_households_from_list.html", context)


@admin.register(Household)
class HouseholdAdmin(
    SoftDeletableAdminMixin,
    LastSyncDateResetMixin,
    LinkedObjectsManagerMixin,
    SmartFieldsetMixin,
    CursorPaginatorAdmin,
    HouseholdWithDrawnMixin,
    HOPEModelAdminBase,
    HouseholdWithdrawFromListMixin,
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
        ("business_area", LinkedAutoCompleteFilter.factory(parent=None)),
        ("program", LinkedAutoCompleteFilter.factory(parent="business_area")),
        ("registration_data_import", LinkedAutoCompleteFilter.factory(parent="program")),
        "registration_method",
        "residence_status",
        "collect_type",
        "withdrawn",
        "consent",
        "consent_sharing",
    )
    search_fields = ("head_of_household__family_name", "unicef_id")
    readonly_fields = ("created_at", "updated_at")
    filter_horizontal = ("representatives",)
    raw_id_fields = (
        "admin1",
        "admin2",
        "admin3",
        "admin4",
        "program",
        "copied_from",
        "business_area",
        "country",
        "country_origin",
        "head_of_household",
        "registration_data_import",
        "household_collection",
        "storage_obj",
        "copied_from",
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
    actions = [
        "mass_withdraw",
        "mass_unwithdraw",
        "count_queryset",
        "create_target_population",
        "add_to_target_population",
        "mass_enroll_to_another_program",
    ]
    cursor_ordering_field = "unicef_id"
    inlines = [HouseholdRepresentationInline]

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
        tickets = []
        for entry in chain(obj.sensitive_ticket_details.all(), obj.complaint_ticket_details.all()):
            tickets.append(entry.ticket)
        context["tickets"] = tickets
        return TemplateResponse(request, "admin/household/household/tickets.html", context)

    @button(permission="household.view_household")
    def members(self, request: HttpRequest, pk: UUID) -> HttpResponseRedirect:
        obj = Household.all_merge_status_objects.get(pk=pk)
        url = reverse("admin:household_individual_changelist")
        flt = f"&qs=household_id={obj.id}"
        return HttpResponseRedirect(f"{url}?{flt}")

    @button(permission=is_root)
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

    @button(permission=lambda request, obj, handler: is_root(request, obj, handler) and obj.can_be_erase())
    def gdpr_remove(self, request: HttpRequest, pk: UUID) -> HttpResponseRedirect:
        household: Household = self.get_queryset(request).get(pk=pk)
        if request.method == "POST":
            try:
                with transaction.atomic():
                    household.erase()
                self.message_user(request, f"Household {household.unicef_id} erased.", messages.SUCCESS)
            except Exception as e:
                self.message_user(request, str(e), messages.ERROR)
            return HttpResponseRedirect(reverse("admin:household_household_change", args=[pk]))
        return confirm_action(
            self,
            request,
            self.gdpr_remove,
            mark_safe(
                """<h1>Household erase</h1>
                <p>After this operation household will be erased, all sensitive data will be overwritten.</p>
                <p>This operation cannot be undo.</p>
                """
            ),
            "Successfully executed",
        )

    @button(permission=lambda request, household, *args, **kwargs: is_root(request) and not household.is_removed)
    def logical_delete(self, request: HttpRequest, pk: UUID) -> HttpResponseRedirect:
        household: Household = self.get_queryset(request).get(pk=pk)
        if request.method == "POST":
            try:
                household.delete()
                self.message_user(request, f"Household {household.unicef_id} was soft removed.", messages.SUCCESS)
            except Exception as e:
                self.message_user(request, str(e), messages.ERROR)
            return HttpResponseRedirect(reverse("admin:household_household_change", args=[pk]))
        return confirm_action(
            self,
            request,
            self.logical_delete,
            mark_safe(
                """<h1>Household logical delete</h1>
                <p>After this operation household will be marked as logical deleted and will be hidden in the application.</p>
                """
            ),
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
                enroll_households_to_program_task.delay(
                    households_ids=households_ids,
                    program_for_enroll_id=str(program_for_enroll.id),
                    user_id=str(request.user.id),
                )
                self.message_user(
                    request,
                    f"Enrolling households to program: {program_for_enroll}",
                    level=messages.SUCCESS,
                )
                return None
        else:
            # Check if all selected objects have the same business_area
            if not all(obj.business_area_id == business_area_id for obj in qs):
                self.message_user(
                    request,
                    "Selected households need to belong to the same business area",
                    level=messages.ERROR,
                )
                return None
        form = MassEnrollForm(request.POST, business_area_id=business_area_id, households=qs)
        context["form"] = form
        context["action"] = "mass_enroll_to_another_program"
        return TemplateResponse(request, "admin/household/household/enroll_households_to_program.html", context)

    mass_enroll_to_another_program.short_description = "Mass enroll households to another program"

    @button(
        label="Withdraw households from list",
        permission="household.can_withdrawn",
    )
    def withdraw_households_from_list_button(self, request: HttpRequest) -> HttpResponse | None:
        return self.withdraw_households_from_list(request)


@admin.register(HouseholdCollection)
class HouseholdCollectionAdmin(admin.ModelAdmin):
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
