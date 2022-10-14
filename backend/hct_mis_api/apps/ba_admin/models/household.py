from adminactions.mass_update import mass_update
from adminfilters.combo import RelatedFieldComboFilter

from hct_mis_api.apps.ba_admin.options import BAModelAdmin
from hct_mis_api.apps.household.models import Household


class BusinessAreaAreas(RelatedFieldComboFilter):
    def field_choices(self, field, request, model_admin):
        ba = model_admin.admin_site.selected_business_area(request)
        return field.get_choices(
            include_blank=False, ordering=("name",), limit_choices_to={"area_type__country__in": ba.countries.all()}
        )


class HouseholdAdmin(BAModelAdmin):
    model = Household
    target_field = "business_area__slug"
    search_fields = ("name",)
    list_display = ["unicef_id", "admin_area", "head_of_household"]
    writeable_fields = []
    list_select_related = ("admin_area", "head_of_household")
    list_filter = (
        "withdrawn",
        ("admin_area", BusinessAreaAreas),
    )
    actions = [
        mass_update,
    ]

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        field = super().formfield_for_foreignkey(db_field, request, **kwargs)
        if db_field.name == "admin_area":
            ba = self.admin_site.selected_business_area(request)
            field.queryset = field.queryset.filter(area_type__country__in=ba.countries)

        return field
