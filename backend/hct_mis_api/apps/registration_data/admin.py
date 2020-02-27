from django.contrib import admin

from registration_data.models import RegistrationDataImport


@admin.register(RegistrationDataImport)
class RegistrationDataImportAdmin(admin.ModelAdmin):
    pass
