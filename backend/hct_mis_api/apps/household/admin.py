from django.contrib import admin

from household.models import Household, Individual


@admin.register(Household)
class HouseholdAdmin(admin.ModelAdmin):
    pass


@admin.register(Individual)
class ImportedIndividualAdmin(admin.ModelAdmin):
    pass
