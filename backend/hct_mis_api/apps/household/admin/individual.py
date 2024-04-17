import logging
from typing import Any, Iterable, Optional, Tuple
from uuid import UUID

from django.contrib import admin, messages
from django.db import transaction
from django.db.models import JSONField, QuerySet
from django.http import HttpRequest, HttpResponseRedirect
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from admin_cursor_paginator import CursorPaginatorAdmin
from admin_extra_buttons.decorators import button
from adminfilters.autocomplete import LinkedAutoCompleteFilter
from adminfilters.combo import ChoicesFieldComboFilter
from adminfilters.depot.widget import DepotManager
from adminfilters.querystring import QueryStringFilter
from adminfilters.value import ValueFilter
from jsoneditor.forms import JSONEditor
from smart_admin.mixins import FieldsetMixin as SmartFieldsetMixin
from smart_admin.mixins import LinkedObjectsMixin

from hct_mis_api.apps.administration.widgets import JsonWidget
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.household.celery_tasks import (
    revalidate_phone_number_task,
    update_individuals_iban_from_xlsx_task,
)
from hct_mis_api.apps.household.forms import UpdateIndividualsIBANFromXlsxForm
from hct_mis_api.apps.household.models import (
    Individual,
    IndividualCollection,
    IndividualIdentity,
    IndividualRoleInHousehold,
    XlsxUpdateFile,
)
from hct_mis_api.apps.utils.admin import (
    BusinessAreaForIndividualCollectionListFilter,
    HOPEModelAdminBase,
    IsOriginalAdminMixin,
    LastSyncDateResetMixin,
    SoftDeletableAdminMixin,
)
from hct_mis_api.apps.utils.security import is_root

logger = logging.getLogger(__name__)


@admin.register(Individual)
class IndividualAdmin(
    SoftDeletableAdminMixin,
    LastSyncDateResetMixin,
    LinkedObjectsMixin,
    SmartFieldsetMixin,
    CursorPaginatorAdmin,
    HOPEModelAdminBase,
    IsOriginalAdminMixin,
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
        "program",
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
        ("business_area", LinkedAutoCompleteFilter.factory(parent=None)),
        ("program", LinkedAutoCompleteFilter.factory(parent="business_area")),
        ("registration_data_import", LinkedAutoCompleteFilter.factory(parent="program")),
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

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        return (
            super()
            .get_queryset(request)
            .select_related(
                "household",
                "registration_data_import",
            )
        )

    def formfield_for_dbfield(self, db_field: Any, request: HttpRequest, **kwargs: Any) -> Any:
        if isinstance(db_field, JSONField):
            if is_root(request):
                kwargs = {"widget": JSONEditor}
            else:
                kwargs = {"widget": JsonWidget}
            return db_field.formfield(**kwargs)
        return super().formfield_for_dbfield(db_field, request, **kwargs)

    @button()
    def household_members(self, request: HttpRequest, pk: UUID) -> HttpResponseRedirect:
        obj = Individual.objects.get(pk=pk)
        url = reverse("admin:household_individual_changelist")
        flt = f"&qs=household_id={obj.household.id}&qs__negate=false"
        return HttpResponseRedirect(f"{url}?{flt}")

    @button(html_attrs={"class": "aeb-green"})
    def sanity_check(self, request: HttpRequest, pk: UUID) -> TemplateResponse:
        context = self.get_common_context(request, pk, title="Sanity Check")
        obj = context["original"]
        context["roles"] = obj.households_and_roles.all()
        context["duplicates"] = Individual.objects.filter(unicef_id=obj.unicef_id)

        return TemplateResponse(request, "admin/household/individual/sanity_check.html", context)

    @button(label="Add/Update Individual IBAN by xlsx")
    def add_update_individual_iban_from_xlsx(self, request: HttpRequest) -> Any:
        if request.method == "GET":
            form = UpdateIndividualsIBANFromXlsxForm()
            context = self.get_common_context(request, title="Add/Update Individual IBAN by xlsx", form=form)
            return TemplateResponse(
                request,
                "admin/household/individual/individuals_iban_xlsx_update.html",
                context,
            )
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
                    request,
                    "admin/household/individual/individuals_iban_xlsx_update.html",
                    context,
                )

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
class IndividualRoleInHouseholdAdmin(SoftDeletableAdminMixin, LastSyncDateResetMixin, HOPEModelAdminBase):
    list_display = ("individual", "household", "role")
    list_filter = (DepotManager, QueryStringFilter, "role", BusinessAreaSlugFilter)
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


@admin.register(IndividualIdentity)
class IndividualIdentityAdmin(SoftDeletableAdminMixin, HOPEModelAdminBase):
    list_display = ("partner", "individual", "number")
    list_filter = (("individual__unicef_id", ValueFilter.factory(label="Individual's UNICEF Id")),)
    raw_id_fields = ("individual", "partner", "copied_from")

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        return super().get_queryset(request).select_related("individual", "partner")


class IndividualRepresentationInline(admin.TabularInline):
    model = Individual
    extra = 0
    fields = ("unicef_id", "program", "is_original")
    readonly_fields = ("unicef_id", "program", "is_original")
    show_change_link = True
    can_delete = False
    verbose_name_plural = "Individual representations"

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        return (
            Individual.all_objects.select_related("program")
            .all()
            .only("unicef_id", "is_original", "copied_from", "program__name")
        )

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

    def number_of_representations(self, obj: IndividualCollection) -> int:
        return obj.individuals(manager="all_objects").count()

    def business_area(self, obj: IndividualCollection) -> Optional[BusinessArea]:
        return obj.business_area
