from hct_mis_api.apps.ba_admin.options import BAModelAdmin
from hct_mis_api.apps.program.models import CashPlan


class CashPlanAdmin(BAModelAdmin):
    model = CashPlan
    target_field = "business_area__slug"
