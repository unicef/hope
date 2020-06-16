# Register your models here.
from django.contrib import admin

from mis_datahub.models import Household, Individual


@admin.register(Household)
class HouseholdAdmin(admin.ModelAdmin):
    pass


@admin.register(Individual)
class IndividualAdmin(admin.ModelAdmin):
    pass
