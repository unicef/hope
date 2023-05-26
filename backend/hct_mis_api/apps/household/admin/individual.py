import logging
from typing import Any
from uuid import UUID

from django.contrib import admin, messages
from django.db import transaction
from django.db.models import JSONField, QuerySet
from django.http import HttpRequest, HttpResponseRedirect
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import reverse

from admin_cursor_paginator import CursorPaginatorAdmin
from admin_extra_buttons.decorators import button
from adminfilters.autocomplete import AutoCompleteFilter
from adminfilters.combo import ChoicesFieldComboFilter
from adminfilters.depot.widget import DepotManager
from adminfilters.querystring import QueryStringFilter
from adminfilters.value import ValueFilter
from jsoneditor.forms import JSONEditor
from smart_admin.mixins import FieldsetMixin as SmartFieldsetMixin
from smart_admin.mixins import LinkedObjectsMixin

from hct_mis_api.apps.administration.widgets import JsonWidget
from hct_mis_api.apps.utils.admin import (
    HOPEModelAdminBase,
    LastSyncDateResetMixin,
    SoftDeletableAdminMixin,
)
from hct_mis_api.apps.utils.security import is_root

from hct_mis_api.apps.household.celery_tasks import (
    revalidate_phone_number_task,
    update_individuals_iban_from_xlsx_task,
)
from hct_mis_api.apps.household.forms import UpdateIndividualsIBANFromXlsxForm
from hct_mis_api.apps.household.models import (
    Individual,
    IndividualIdentity,
    IndividualRoleInHousehold,
    XlsxUpdateFile,
)

logger = logging.getLogger(__name__)


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
class IndividualIdentityAdmin(HOPEModelAdminBase):
    list_display = ("partner", "individual", "number")
    list_filter = (("individual__unicef_id", ValueFilter.factory(label="Individual's UNICEF Id")),)
    raw_id_fields = (
        "individual",
        "partner",
    )

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        return super().get_queryset(request).select_related("individual", "partner")
