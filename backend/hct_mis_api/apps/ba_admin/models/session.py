from hct_mis_api.apps.ba_admin.options import BAModelAdmin
from hct_mis_api.apps.cash_assist_datahub.models import Session as CASessionModel
from hct_mis_api.apps.mis_datahub.models import Session as MISSessionModel


class CASessionAdmin(BAModelAdmin):
    model = CASessionModel
    target_field = "business_area"


class HOPESessionAdmin(BAModelAdmin):
    model = MISSessionModel
    target_field = "business_area"
