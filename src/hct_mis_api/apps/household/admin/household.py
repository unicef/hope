import logging
import re
from itertools import chain
from typing import Any, List, Optional
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

from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.core.utils import JSONBSet, decode_id_string_required
from hct_mis_api.apps.grievance.models import GrievanceTicket
from hct_mis_api.apps.household.admin.mixins import (
    CustomTargetPopulationMixin,
    HouseholdWithDrawnMixin,
)
from hct_mis_api.apps.household.celery_tasks import (
    enroll_households_to_program_task,
    mass_withdraw_households_from_list_task,
)
from hct_mis_api.apps.household.forms import MassEnrollForm
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
from hct_mis_api.apps.utils.admin import (
    BusinessAreaForHouseholdCollectionListFilter,
    HOPEModelAdminBase,
    IsOriginalAdminMixin,
    LastSyncDateResetMixin,
    LinkedObjectsManagerMixin,
    RdiMergeStatusAdminMixin,
    SoftDeletableAdminMixin,
)
from hct_mis_api.apps.utils.security import is_root

logger = logging.getLogger(__name__)


class HouseholdRepresentationInline(admin.TabularInline):
    model = Household
    extra = 0
    fields = ("unicef_id", "program", "is_original")
    readonly_fields = ("unicef_id", "program", "is_original")
    show_change_link = True
    can_delete = False
    verbose_name_plural = "Household representations"

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        return (
            Household.all_objects.all()
            .select_related("program")
            .only("unicef_id", "is_original", "copied_from", "program__name")
        )

    def has_add_permission(self, request: HttpRequest, obj: Optional[Household] = None) -> bool:
        return False  # Disable adding new individual representations inline


class HouseholdWithdrawFromListMixin:
    @staticmethod
    def get_program_from_encoded_id(program_id: str) -> Optional[Program]:
        try:
            decoded_program_id = decode_id_string_required(program_id)
            return Program.objects.filter(id=decoded_program_id).first()
        except Exception:
            return None

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
            user_fields=JSONBSet(F("user_fields"), Value("{withdrawn_tag}"), Value(f'"{tag}"')),
        )

    @staticmethod
    def split_list_of_ids(household_list: str) -> list:
        """
        Split input list of ids by literal 'new line' or any of the following characters: "," "|" "/" or white spaces
        """
        return [hh_id.strip() for hh_id in re.split(r"new line|[,\|/\s]+", household_list) if hh_id]

    @staticmethod
    def get_and_set_context_data(request: HttpRequest, context: dict) -> None:
        household_list = request.POST.get("household_list")
        tag = request.POST.get("tag")
        program_id = request.POST.get("program_id")
        context["household_list"] = household_list
        context["tag"] = tag
        context["program_id"] = program_id

    def withdraw_households_from_list(self, request: HttpRequest) -> Optional[HttpResponse]:
        context = self.get_common_context(request, title="Withdraw households from list")
        if request.method == "POST":
            step = request.POST.get("step")
            if step == "1":
                context["step"] = "2"
                self.get_and_set_context_data(request, context)
                return TemplateResponse(
                    request,
                    "admin/household/household/withdraw_households_from_list.html",
                    context,
                )
            elif step == "2":
                context["step"] = "2"
                self.get_and_set_context_data(request, context)
                household_id_list = self.split_list_of_ids(context["household_list"])
                program = self.get_program_from_encoded_id(context["program_id"])
                if not program:
                    self.message_user(
                        request,
                        f"Program with ID '{context['program_id']}' not found.",
                        level=messages.ERROR,
                    )
                    return HttpResponseRedirect(reverse("admin:household_household_changelist"))

                context["household_count"] = self.get_household_queryset_from_list(
                    household_id_list,
                    program,
                ).count()
                return TemplateResponse(
                    request,
                    "admin/household/household/withdraw_households_from_list.html",
                    context,
                )
            else:
                household_list = request.POST.get("household_list", "")
                tag = request.POST.get("tag", "")
                program_id = request.POST.get("program_id", "")

                program = self.get_program_from_encoded_id(program_id)
                household_id_list = self.split_list_of_ids(household_list)
                household_count = self.get_household_queryset_from_list(
                    household_id_list,
                    program,  # type: ignore
                ).count()

                mass_withdraw_households_from_list_task.delay(household_id_list, tag, program.id)  # type: ignore
                self.message_user(request, f"{household_count} Households are being withdrawn.")

                return HttpResponseRedirect(reverse("admin:household_household_changelist"))

        context["step"] = "1"
        return TemplateResponse(request, "admin/household/household/withdraw_households_from_list.html", context)


@admin.register(Household)
class HouseholdAdmin(
    SoftDeletableAdminMixin,
    LastSyncDateResetMixin,
    LinkedObjectsManagerMixin,
    SmartFieldsetMixin,
    CursorPaginatorAdmin,
    HouseholdWithDrawnMixin,
    CustomTargetPopulationMixin,
    HOPEModelAdminBase,
    IsOriginalAdminMixin,
    HouseholdWithdrawFromListMixin,
    RdiMergeStatusAdminMixin,
):
    list_display = (
        "unicef_id",
        "business_area",
        "country",
        "head_of_household",
        "size",
        "withdrawn",
        "program",
        "rdi_merge_status",
    )
    list_filter = (
        DepotManager,
        ("business_area", LinkedAutoCompleteFilter.factory(parent=None)),
        ("program", LinkedAutoCompleteFilter.factory(parent="business_area")),
        ("registration_data_import", LinkedAutoCompleteFilter.factory(parent="program")),
        QueryStringFilter,
        "withdrawn",
    )
    search_fields = ("head_of_household__family_name", "unicef_id")
    readonly_fields = ("created_at", "updated_at")
    filter_horizontal = ("representatives", "programs")
    raw_id_fields = (
        "admin_area",
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
            "head_of_household", "country", "country_origin", "admin_area", "admin1", "admin2", "admin3", "admin4"
        )
        ordering = self.get_ordering(request)
        if ordering:
            qs = qs.order_by(*ordering)
        return qs

    def formfield_for_foreignkey(self, db_field: Any, request: HttpRequest, **kwargs: Any) -> Any:
        if db_field.name == "head_of_household":
            kwargs["queryset"] = Individual.all_objects.all()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_ignored_linked_objects(self, request: HttpRequest) -> List:
        return []

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False

    def has_delete_permission(self, request: HttpRequest, obj: Optional[Any] = None) -> bool:
        return False

    @button()
    def tickets(self, request: HttpRequest, pk: UUID) -> TemplateResponse:
        context = self.get_common_context(request, pk, title="Tickets")
        obj = context["original"]
        tickets = []
        for entry in chain(obj.sensitive_ticket_details.all(), obj.complaint_ticket_details.all()):
            tickets.append(entry.ticket)
        context["tickets"] = tickets
        return TemplateResponse(request, "admin/household/household/tickets.html", context)

    @button()
    def members(self, request: HttpRequest, pk: UUID) -> HttpResponseRedirect:
        obj = Household.all_merge_status_objects.get(pk=pk)
        url = reverse("admin:household_individual_changelist")
        flt = f"&qs=household_id={obj.id}"
        return HttpResponseRedirect(f"{url}?{flt}")

    @button()
    def sanity_check(self, request: HttpRequest, pk: UUID) -> TemplateResponse:
        # NOTE: this code is should be optimized in the future and it is not
        # intended to be used in bulk
        hh = self.get_object(request, str(pk))
        warnings: List[List] = []
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
        all_individuals = hh.individuals(manager="all_objects").all()
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

    def mass_enroll_to_another_program(self, request: HttpRequest, qs: QuerySet) -> Optional[HttpResponse]:
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
        permission=is_root,
    )
    def withdraw_households_from_list_button(self, request: HttpRequest) -> Optional[HttpResponse]:
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

    def number_of_representations(self, obj: HouseholdCollection) -> int:
        return obj.households(manager="all_objects").count()

    def business_area(self, obj: HouseholdCollection) -> Optional[BusinessArea]:
        return obj.business_area
