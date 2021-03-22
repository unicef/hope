from django.contrib import admin, messages
from django.contrib.messages import DEFAULT_TAGS
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import reverse

from admin_extra_urls.decorators import button
from admin_extra_urls.mixins import ExtraUrlMixin
from adminfilters.filters import (
    ChoicesFieldComboFilter,
    MaxMinFilter,
    RelatedFieldComboFilter,
    TextFieldFilter,
)
from smart_admin.mixins import FieldsetMixin as SmartFieldsetMixin

from hct_mis_api.apps.household.models import (
    HEAD,
    ROLE_ALTERNATE,
    ROLE_PRIMARY,
    Agency,
    Document,
    DocumentType,
    Household,
    Individual,
    IndividualIdentity,
    IndividualRoleInHousehold,
)
from hct_mis_api.apps.utils.admin import HOPEModelAdminBase


@admin.register(Agency)
class AgencyTypeAdmin(HOPEModelAdminBase):
    list_display = ("label", "type", "country")


@admin.register(Document)
class DocumentAdmin(HOPEModelAdminBase):
    list_display = ("document_number", "type", "status", "individual")
    raw_id_fields = ("individual",)
    list_filter = (("type", RelatedFieldComboFilter),)


@admin.register(DocumentType)
class DocumentTypeAdmin(HOPEModelAdminBase):
    list_display = ("label", "country", "type")


@admin.register(Household)
class HouseholdAdmin(SmartFieldsetMixin, ExtraUrlMixin, HOPEModelAdminBase):
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
        ("business_area", RelatedFieldComboFilter),
        ("size", MaxMinFilter),
        "org_enumerator",
        "last_registration_date",
    )
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
                    "last_sync_at",
                    "created_at",
                    "updated_at",
                    "removed_date",
                    "withdrawn_date",
                ),
            },
        ),
        ("Others", {"classes": ("collapse",), "fields": ("__all__",)}),
    ]

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


@admin.register(Individual)
class IndividualAdmin(SmartFieldsetMixin, ExtraUrlMixin, HOPEModelAdminBase):
    list_display = (
        "unicef_id",
        "given_name",
        "family_name",
        "household",
        "sex",
        "relationship",
        "birth_date",
    )
    search_fields = ("family_name",)
    list_filter = (
        TextFieldFilter.factory("unicef_id__iexact", "UNICEF ID"),
        TextFieldFilter.factory("household__unicef_id__iexact", "Household ID"),
        ("deduplication_golden_record_status", ChoicesFieldComboFilter),
        ("deduplication_batch_status", ChoicesFieldComboFilter),
        ("business_area", RelatedFieldComboFilter),
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
                    "last_sync_at",
                    "created_at",
                    "updated_at",
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
        ("Others", {"classes": ("collapse",), "fields": ("__all__",)}),
    ]

    @button()
    def household_members(self, request, pk):
        obj = Individual.objects.get(pk=pk)
        url = reverse("admin:household_individual_changelist")
        return HttpResponseRedirect(f"{url}?household|unicef_id|iexact={obj.household.unicef_id}")


@admin.register(IndividualRoleInHousehold)
class IndividualRoleInHouseholdAdmin(HOPEModelAdminBase):
    list_display = ("individual_id", "household_id", "role")
    list_filter = ("role",)
    raw_id_fields = (
        "individual",
        "household",
    )


@admin.register(IndividualIdentity)
class IndividualIdentityAdmin(HOPEModelAdminBase):
    pass
