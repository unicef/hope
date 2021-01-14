from django.contrib import admin

from hct_mis_api.apps.registration_data.models import RegistrationDataImport


@admin.register(RegistrationDataImport)
class RegistrationDataImportAdmin(admin.ModelAdmin):
    pass
