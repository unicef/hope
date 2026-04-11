"""Section grouping used by the HOPE smart-index admin view.

Ported from ``SMART_ADMIN_SECTIONS`` on ``develop`` when the
``django-smart-admin`` dependency was removed.
"""

from hope.apps.administration.section_utils import MatchString, RegexString

HOPE_ADMIN_SECTIONS = {
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
