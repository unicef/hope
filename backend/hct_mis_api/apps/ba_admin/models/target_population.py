from hct_mis_api.apps.ba_admin.options import BAModelAdmin
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.targeting.models import TargetPopulation


class TargetPopulationAdmin(BAModelAdmin):
    model = TargetPopulation
    target_field = "business_area__slug"
    search_fields = ("name",)
    list_display = [
        "name",
        "status",
    ]
    writeable_fields = []
