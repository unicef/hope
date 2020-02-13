from django.contrib import admin

from household.models import Household


@admin.register(Household)
class HouseholdAdmin(admin.ModelAdmin):
    pass
