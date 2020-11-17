from django.contrib import admin

from mis_datahub.models import (
    Household,
    Individual,
    Session,
    TargetPopulation,
    Program,
    IndividualRoleInHousehold,
    Document,
)


@admin.register(Household)
class HouseholdAdmin(admin.ModelAdmin):
    pass


@admin.register(Individual)
class IndividualAdmin(admin.ModelAdmin):
    list_display = ("unicef_id", "family_name", "given_name")


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


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ("type", "number")
