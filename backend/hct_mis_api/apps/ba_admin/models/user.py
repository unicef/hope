from adminfilters.combo import ChoicesFieldComboFilter

from hct_mis_api.apps.account.models import User
from hct_mis_api.apps.ba_admin.options import BAModelAdmin


class UserAdmin(BAModelAdmin):
    model = User
    target_field = "user_roles__business_area__slug"
    list_display = ["username", "email", "partner", "is_active"]
    # fields = ["username", "email", "active", "partner"]
    search_fields = ["username", "email"]
    list_filter = (("partner", ChoicesFieldComboFilter), "is_active")
