from smart_admin.utils import MatchString, RegexString

from hope.config.env import env

SMART_ADMIN_SECTIONS = {
    "HOPE": [
        "program",
        MatchString("household.H*"),
        RegexString(r"household\.I.*"),
        "targeting",
        "payment",
    ],
    "RDI": [
        RegexString(r"registration_data\..*"),
    ],
    "Grievance": ["grievance"],
    "Configuration": [
        "core",
        "constance",
        "flags",
    ],
    "Rule Engine": [
        "steficon",
    ],
    "Security": ["account", "auth"],
    "Logs": [
        "admin.LogEntry",
        "activity_log",
    ],
    "Kobo": [
        "core.FlexibleAttributeChoice",
        "core.XLSXKoboTemplate",
        "core.FlexibleAttribute",
        "core.FlexibleAttributeGroup",
    ],
    "HUB (Kobo->Hope)": [
        "registration_datahub",
    ],
    "System": [
        "social_django",
        "constance",
        "sites",
    ],
}

SMART_ADMIN_BOOKMARKS = "hope.apps.administration.admin_site.get_bookmarks"

SMART_ADMIN_BOOKMARKS_PERMISSION = None
SMART_ADMIN_PROFILE_LINK = True
SMART_ADMIN_ISROOT = lambda r, *a: r.user.is_superuser and r.headers.get("x-root-token") == env("ROOT_TOKEN")
