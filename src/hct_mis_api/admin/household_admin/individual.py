import logging
from typing import Any, Iterable, Optional, Tuple
from uuid import UUID

from django.contrib import admin, messages
from django.db.models import JSONField, QuerySet
from django.http import HttpRequest, HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from admin_cursor_paginator import CursorPaginatorAdmin
from admin_extra_buttons.decorators import button
from adminfilters.autocomplete import AutoCompleteFilter, LinkedAutoCompleteFilter
from adminfilters.combo import ChoicesFieldComboFilter
from adminfilters.depot.widget import DepotManager
from adminfilters.querystring import QueryStringFilter
from adminfilters.value import ValueFilter
from jsoneditor.forms import JSONEditor
from smart_admin.mixins import FieldsetMixin as SmartFieldsetMixin

from hct_mis_api.apps.administration.widgets import JsonWidget
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.household.celery_tasks import revalidate_phone_number_task
from hct_mis_api.apps.household.models import (
    Household,
    Individual,
    IndividualCollection,
    IndividualIdentity,
    IndividualRoleInHousehold,
)
from hct_mis_api.apps.payment.models import Account
from hct_mis_api.admin.utils_admin import (
    BusinessAreaForIndividualCollectionListFilter,
    HOPEModelAdminBase,
    LastSyncDateResetMixin,
    LinkedObjectsManagerMixin,
    RdiMergeStatusAdminMixin,
    SoftDeletableAdminMixin,
)
from hct_mis_api.apps.utils.security import is_root

logger = logging.getLogger(__name__)


class IndividualAccountInline(admin.TabularInline):
    model = Account
    extra = 0
    fields = ("account_type", "number", "data", "view_link")

    readonly_fields = ("view_link",)

    def view_link(self, obj: Any) -> str:
        if obj.pk:
            url = reverse("admin:payment_account_change", args=[obj.pk])
            return format_html('<a href="{}" target="_blank">View</a>', url)
        return ""

    view_link.short_description = "View"


@admin.register(Individual)
class IndividualAdmin(
    SoftDeletableAdminMixin,
    LastSyncDateResetMixin,
    LinkedObjectsManagerMixin,
    SmartFieldsetMixin,
    CursorPaginatorAdmin,
    HOPEModelAdminBase,
    RdiMergeStatusAdminMixin,
):
    # Custom template to merge AdminAdvancedFiltersMixin and ExtraButtonsMixin
    advanced_change_list_template = "admin/household/advanced_filters_extra_buttons_change_list.html"
    cursor_ordering_field = "unicef_id"

    list_display = (
        "unicef_id",
        "given_name",
        "family_name",
        "sex",
        "relationship",
        "birth_date",
        "marital_status",
        "duplicate",
        "withdrawn",
        "household",
        "business_area",
        "program",
        "registration_data_import",
        "rdi_merge_status",
    )
    advanced_filter_fields = (
        "updated_at",
        "last_sync_at",
        "deduplication_golden_record_status",
        "deduplication_batch_status",
        "duplicate",
        ("business_area__name", "business area"),
    )

    search_fields = ("family_name", "unicef_id", "household__unicef_id", "given_name", "family_name", "full_name")
    readonly_fields = ("created_at", "updated_at", "registration_data_import")
    exclude = ("created_at", "updated_at")
    list_filter = (
        DepotManager,
        QueryStringFilter,
        ("deduplication_golden_record_status", ChoicesFieldComboFilter),
        ("deduplication_batch_status", ChoicesFieldComboFilter),
        ("business_area", LinkedAutoCompleteFilter.factory(parent=None)),
        ("program", LinkedAutoCompleteFilter.factory(parent="business_area")),
        ("registration_data_import", LinkedAutoCompleteFilter.factory(parent="program")),
        "sex",
        "relationship",
        "marital_status",
        "duplicate",
        "withdrawn",
        "updated_at",
        "last_sync_at",
    )
    raw_id_fields = (
        "household",
        "registration_data_import",
        "business_area",
        "copied_from",
        "program",
        "individual_collection",
    )
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
    actions = ["count_queryset", "revalidate_phone_number_sync", "revalidate_phone_number_async"]
    inlines = [IndividualAccountInline]

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        return (
            super()
            .get_queryset(request)
            .select_related(
                "household", "registration_data_import", "individual_collection", "program", "business_area"
            )
        )

    def formfield_for_foreignkey(self, db_field: Any, request: HttpRequest, **kwargs: Any) -> Any:
        if db_field.name == "household":
            kwargs["queryset"] = Household.all_objects.all()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def formfield_for_dbfield(self, db_field: Any, request: HttpRequest, **kwargs: Any) -> Any:
        if isinstance(db_field, JSONField):
            if is_root(request):
                kwargs = {"widget": JSONEditor}
            else:
                kwargs = {"widget": JsonWidget}
            return db_field.formfield(**kwargs)
        return super().formfield_for_dbfield(db_field, request, **kwargs)

    @button(permission="household.view_individual")
    def household_members(self, request: HttpRequest, pk: UUID) -> HttpResponseRedirect:
        obj = Individual.all_merge_status_objects.get(pk=pk)
        url = reverse("admin:household_individual_changelist")
        flt = f"&qs=household_id={obj.household.id}&qs__negate=false"
        return HttpResponseRedirect(f"{url}?{flt}")

    @button(html_attrs={"class": "aeb-green"}, permission=is_root)
    def sanity_check(self, request: HttpRequest, pk: UUID) -> TemplateResponse:
        context = self.get_common_context(request, pk, title="Sanity Check")
        obj = context["original"]
        context["roles"] = obj.households_and_roles(manager="all_objects").all()
        context["duplicates"] = Individual.all_objects.filter(unicef_id=obj.unicef_id)

        return TemplateResponse(request, "admin/household/individual/sanity_check.html", context)

    def revalidate_phone_number_sync(self, request: HttpRequest, queryset: QuerySet) -> None:
        try:
            ids = queryset.values_list("id", flat=True)
            revalidate_phone_number_task(ids)
            self.message_user(request, f"Updated {len(ids)} records", messages.SUCCESS)
        except Exception as e:
            self.message_user(request, str(e), messages.ERROR)

    revalidate_phone_number_sync.short_description = "Re-validate phone number (sync)"

    def revalidate_phone_number_async(self, request: HttpRequest, queryset: QuerySet) -> None:
        ids = list(queryset.values_list("id", flat=True))
        revalidate_phone_number_task.delay(ids)
        self.message_user(request, "Updating in progress", messages.SUCCESS)

    revalidate_phone_number_async.short_description = "Re-validate phone number (async)"


class InputFilter(admin.SimpleListFilter):
    template: str = "admin/household/individual/business_area_slug_input_filter.html"

    def lookups(self, request: HttpRequest, model_admin: Any) -> Optional[Iterable[Tuple[Any, str]]]:
        return [(None, "")]


class BusinessAreaSlugFilter(InputFilter):
    parameter_name: str = "individual__business_area_slug"
    title: str = _("Business Area Slug")

    def queryset(self, request: HttpRequest, queryset: QuerySet) -> QuerySet:
        if self.value() is not None:
            return queryset.filter(individual__business_area__slug=self.value())
        return queryset


@admin.register(IndividualRoleInHousehold)
class IndividualRoleInHouseholdAdmin(
    SoftDeletableAdminMixin, LastSyncDateResetMixin, HOPEModelAdminBase, RdiMergeStatusAdminMixin
):
    search_fields = ("individual__unicef_id", "household__unicef_id")
    list_display = ("individual", "household", "role", "copied_from", "is_removed")
    list_filter = (
        DepotManager,
        QueryStringFilter,
        BusinessAreaSlugFilter,
        "role",
    )
    raw_id_fields = ("individual", "household", "copied_from")

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        return (
            super()
            .get_queryset(request)
            .select_related(
                "individual",
                "household",
            )
        )

    def formfield_for_foreignkey(self, db_field: Any, request: HttpRequest, **kwargs: Any) -> Any:
        if db_field.name == "individual":
            kwargs["queryset"] = Individual.all_objects.all()
        if db_field.name == "household":
            kwargs["queryset"] = Household.all_objects.all()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(IndividualIdentity)
class IndividualIdentityAdmin(HOPEModelAdminBase, RdiMergeStatusAdminMixin):
    list_display = (
        "number",
        "partner",
        "individual",
    )
    list_filter = (
        ("individual__unicef_id", ValueFilter.factory(label="Individual's UNICEF Id")),
        ("partner", AutoCompleteFilter),
    )
    raw_id_fields = ("individual", "partner", "copied_from", "country")
    search_fields = ("number", "individual__unicef_id")

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        return super().get_queryset(request).select_related("individual", "partner", "copied_from", "country")

    def formfield_for_foreignkey(self, db_field: Any, request: HttpRequest, **kwargs: Any) -> Any:
        if db_field.name == "individual":
            kwargs["queryset"] = Individual.all_objects.all()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class IndividualRepresentationInline(admin.TabularInline):
    model = Individual
    extra = 0
    fields = ("unicef_id", "program")
    readonly_fields = ("unicef_id", "program")
    show_change_link = True
    can_delete = False
    verbose_name_plural = "Individual representations"

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        return (
            Individual.all_objects.select_related("program").all().only("unicef_id", "copied_from", "program__name")
        )  # pragma: no cover

    def has_add_permission(self, request: HttpRequest, obj: Optional[Individual] = None) -> bool:
        return False  # Disable adding new individual representations inline


@admin.register(IndividualCollection)
class IndividualCollectionAdmin(admin.ModelAdmin):
    list_display = (
        "unicef_id",
        "business_area",
        "number_of_representations",
    )
    search_fields = ("unicef_id",)
    list_filter = [BusinessAreaForIndividualCollectionListFilter]
    inlines = [IndividualRepresentationInline]

    def get_queryset(self, request: HttpRequest) -> "QuerySet":
        return (
            super()
            .get_queryset(request)
            .prefetch_related(
                "individuals",
            )
        )

    def number_of_representations(self, obj: IndividualCollection) -> int:
        return obj.individuals(manager="all_objects").count()

    def business_area(self, obj: IndividualCollection) -> Optional[BusinessArea]:
        return obj.business_area
