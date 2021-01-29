from django.contrib import admin
from adminfilters.filters import TextFieldFilter, RelatedFieldComboFilter, AllValuesComboFilter, \
    ChoicesFieldComboFilter, MaxMinFilter
from hct_mis_api.apps.household.models import (
    Household,
    Individual,
    DocumentType,
    Document,
    Agency,
    IndividualRoleInHousehold,
    IndividualIdentity,
)
from hct_mis_api.apps.utils.admin import HOPEModelAdminBase


@admin.register(Agency)
class AgencyTypeAdmin(HOPEModelAdminBase):
    list_display = ("label", "type", "country")


@admin.register(Document)
class DocumentAdmin(HOPEModelAdminBase):
    list_display = ("document_number", "type", "individual")
    raw_id_fields = ("individual",)
    list_filter = ("type",)


@admin.register(DocumentType)
class DocumentTypeAdmin(HOPEModelAdminBase):
    list_display = ("label", "country", "type")


@admin.register(Household)
class HouseholdAdmin(HOPEModelAdminBase):
    list_display = ("unicef_id", "country", "head_of_household", "size", )
    list_filter = (TextFieldFilter.factory("unicef_id", "UNICEF ID"),
                   TextFieldFilter.factory("unhcr_id", "UNHCR ID"),
                   TextFieldFilter.factory("id", "MIS ID"),
                   # ("country", ChoicesFieldComboFilter),
                   ("business_area", RelatedFieldComboFilter),
                   ("size", MaxMinFilter),
                   "org_enumerator",
                   "last_registration_date",
                   )
    filter_horizontal = ("representatives", "programs")
    raw_id_fields = (
        "registration_data_import",
        "admin_area",
        "head_of_household",
        "business_area"
    )


@admin.register(Individual)
class IndividualAdmin(HOPEModelAdminBase):
    list_display = ("unicef_id", "given_name", "family_name", "household", "sex", "relationship", "birth_date", )
    search_fields = ('family_name',)
    list_filter = (TextFieldFilter.factory("unicef_id__iexact", "UNICEF ID"),
                   TextFieldFilter.factory("household__unicef_id__iexact", "Household ID"),
                   ("deduplication_golden_record_status", ChoicesFieldComboFilter),
                   ("deduplication_batch_status", ChoicesFieldComboFilter),

                   ("business_area", RelatedFieldComboFilter),
                   )
    raw_id_fields = ("household", "registration_data_import", "business_area")


@admin.register(IndividualRoleInHousehold)
class IndividualRoleInHouseholdAdmin(HOPEModelAdminBase):
    list_display = ("individual_id", "household_id", "role")
    list_filter = ("role", )
    raw_id_fields = ("individual", "household",)

@admin.register(IndividualIdentity)
class IndividualIdentityAdmin(HOPEModelAdminBase):
    pass
