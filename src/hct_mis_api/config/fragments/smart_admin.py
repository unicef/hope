from smart_admin.utils import match, regex

from hct_mis_api.config.env import env

SMART_ADMIN_SECTIONS = {
    "HOPE": [
        "program",
        match("household.H*"),
        regex(r"household\.I.*"),
        "targeting",
        "payment",
    ],
    "RDI": [
        regex(r"registration_data\..*"),
        # regex(r"registration_datahub\..*"),
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

SMART_ADMIN_BOOKMARKS = "hct_mis_api.apps.administration.site.get_bookmarks"

SMART_ADMIN_BOOKMARKS_PERMISSION = None
SMART_ADMIN_PROFILE_LINK = True
SMART_ADMIN_ISROOT = lambda r, *a: r.user.is_superuser and r.headers.get("x-root-token") == env("ROOT_TOKEN")
