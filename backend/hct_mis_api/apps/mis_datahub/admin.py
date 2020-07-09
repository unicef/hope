# Register your models here.
from django.contrib import admin

from mis_datahub.models import (
    Household,
    Individual,
    Session,
    TargetPopulation,
    Program, IndividualRoleInHousehold,
)


@admin.register(Household)
class HouseholdAdmin(admin.ModelAdmin):
    pass


@admin.register(Individual)
class IndividualAdmin(admin.ModelAdmin):
    pass


@admin.register(IndividualRoleInHousehold)
class IndividualRoleInHouseholdAdmin(admin.ModelAdmin):
    pass


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    pass


@admin.register(TargetPopulation)
class SessionAdmin(admin.ModelAdmin):
    pass


@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    pass
