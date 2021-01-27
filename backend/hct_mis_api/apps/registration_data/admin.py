from adminfilters.filters import RelatedFieldComboFilter
from django.contrib import admin
from django.contrib.admin import SimpleListFilter

from hct_mis_api.apps.registration_data.models import RegistrationDataImport


class Errored(SimpleListFilter):
    title = 'Errored'
    parameter_name = 'errored'

    def lookups(self, request, model_admin):
        return (('fail', 'Fail'), ('success', 'Success'))

    def queryset(self, request, queryset):
        if not self.value():
            return queryset
        if self.value() == '-':
            return queryset
        elif self.value() == 'fail':
            return queryset.filter(error_message__isnull=True)
        else:
            return queryset.filter(error_message__isnull=False)


@admin.register(RegistrationDataImport)
class RegistrationDataImportAdmin(admin.ModelAdmin):
    list_display = ('name', 'status', 'import_date', 'imported_by', 'number_of_individuals')
    date_hierarchy = 'import_date'
    list_filter = ('status',
                   ('business_area', RelatedFieldComboFilter),
                   Errored
                   )
