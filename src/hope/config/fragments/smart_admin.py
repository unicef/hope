from smart_admin.utils import MatchString, RegexString

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
    "System": [
        "social_django",
        "constance",
        "sites",
    ],
}

SMART_ADMIN_BOOKMARKS = "hope.apps.administration.admin_site.get_bookmarks"

SMART_ADMIN_PROFILE_LINK = True
