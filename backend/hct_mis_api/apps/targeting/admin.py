from django.contrib import admin

# Register your models here.
from targeting.models import TargetPopulation, HouseholdSelection


@admin.register(TargetPopulation)
class TargetPopulationAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "status",
        "candidate_list_total_households",
        "candidate_list_total_individuals",
        "final_list_total_households",
        "final_list_total_individuals",
    )

@admin.register(HouseholdSelection)
class HouseholdSelectionAdmin(admin.ModelAdmin):
    list_display = (
        "household",
        "target_population",
        "vulnerability_score",
        "final",
    )
