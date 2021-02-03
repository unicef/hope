from adminfilters.filters import ChoicesFieldComboFilter, RelatedFieldComboFilter
from django.contrib import admin

# Register your models here.
from hct_mis_api.apps.targeting.models import TargetPopulation, HouseholdSelection
from hct_mis_api.apps.utils.admin import HOPEModelAdminBase


@admin.register(TargetPopulation)
class TargetPopulationAdmin(HOPEModelAdminBase):
    list_display = (
        "name",
        "status",
        "candidate_list_total_households",
        "candidate_list_total_individuals",
        "final_list_total_households",
        "final_list_total_individuals",
    )
    search_fields = ('name',)
    list_filter = (('status', ChoicesFieldComboFilter),
                   ('business_area', RelatedFieldComboFilter),
                   'is_removed',
                   )
    raw_id_fields = ('created_by', 'approved_by', 'finalized_by',
                     'business_area', 'program')


@admin.register(HouseholdSelection)
class HouseholdSelectionAdmin(HOPEModelAdminBase):
    list_display = (
        "household",
        "target_population",
        "vulnerability_score",
        "final",
    )
