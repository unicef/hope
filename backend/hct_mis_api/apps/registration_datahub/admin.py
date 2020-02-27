from django.contrib import admin

from registration_datahub.models import (
    RegistrationDataImportDatahub,
    ImportedIndividual,
    ImportedHousehold,
)


@admin.register(RegistrationDataImportDatahub)
class RegistrationDataImportDatahubAdmin(admin.ModelAdmin):
    pass


@admin.register(ImportedIndividual)
class ImportedIndividualAdmin(admin.ModelAdmin):
    pass


@admin.register(ImportedHousehold)
class ImportedHouseholdAdmin(admin.ModelAdmin):
    pass
