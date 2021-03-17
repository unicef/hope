from adminfilters.filters import ChoicesFieldComboFilter, TextFieldFilter
from django.contrib import admin

from hct_mis_api.apps.registration_datahub.models import (
    RegistrationDataImportDatahub,
    ImportedIndividual,
    ImportedHousehold,
    ImportedDocumentType,
    ImportedDocument,
    ImportData,
    ImportedIndividualRoleInHousehold,
    ImportedIndividualIdentity,
)
from hct_mis_api.apps.utils.admin import HOPEModelAdminBase


@admin.register(RegistrationDataImportDatahub)
class RegistrationDataImportDatahubAdmin(HOPEModelAdminBase):
    pass


@admin.register(ImportedIndividual)
class ImportedIndividualAdmin(HOPEModelAdminBase):
    list_display = (
        "registration_data_import",
        "full_name",
        "sex",
    )
    list_filter = (TextFieldFilter.factory("registration_data_import__name__istartswith"),)
    date_hierarchy = "updated_at"
    raw_id_fields = ("household", "registration_data_import")


@admin.register(ImportedIndividualIdentity)
class ImportedIndividualIdentityAdmin(HOPEModelAdminBase):
    pass


@admin.register(ImportedHousehold)
class ImportedHouseholdAdmin(HOPEModelAdminBase):
    pass


@admin.register(ImportData)
class ImportDataAdmin(HOPEModelAdminBase):
    pass


@admin.register(ImportedDocument)
class ImportedDocumentAdmin(HOPEModelAdminBase):
    list_display = ("document_number", "type", "individual")


@admin.register(ImportedDocumentType)
class ImportedDocumentTypeAdmin(HOPEModelAdminBase):
    list_display = ("label", "country")


@admin.register(ImportedIndividualRoleInHousehold)
class ImportedIndividualRoleInHouseholdAdmin(HOPEModelAdminBase):
    pass
