from django.contrib.admin.models import LogEntry

from adminfilters.combo import RelatedFieldComboFilter

from hct_mis_api.apps.ba_admin.options import BAModelAdmin


class LogEntryAdmin(BAModelAdmin):
    model = LogEntry
    target_field = "user__user_roles__business_area__slug"
    list_display = ("action_time", "user", "content_type", "object_repr", "action_flag")
    date_hierarchy = "action_time"
    list_filter = (
        "action_flag",
        ("content_type", RelatedFieldComboFilter),
    )
