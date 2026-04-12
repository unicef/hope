from django.templatetags.static import static
from django.urls import reverse_lazy
from django.utils.functional import lazy
from django.utils.translation import gettext_lazy as _

static_lazy = lazy(static, str)

UNFOLD = {
    "SITE_TITLE": "HOPE ADMIN",
    "SITE_HEADER": "HOPE Administration",
    "SITE_URL": "/",
    "SITE_FAVICONS": [
        {
            "rel": "icon",
            "type": "image/png",
            "href": static_lazy("administration/favicon-admin.png"),
        },
    ],
    "DASHBOARD_CALLBACK": "hope.apps.administration.admin_site.dashboard_callback",
    "SHOW_HISTORY": True,
    "SHOW_VIEW_ON_SITE": True,
    "ENVIRONMENT": "hope.config.fragments.unfold.environment_callback",
    "SITE_DROPDOWN": "hope.apps.administration.admin_site.site_dropdown_callback",
    "STYLES": [
        lambda request: static("admin/css/hope_admin.css"),
    ],
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": True,
        "navigation": [
            {
                "title": _("HOPE"),
                "items": [
                    {
                        "title": _("Programs"),
                        "link": reverse_lazy("admin:program_program_changelist"),
                        "icon": "folder",
                    },
                    {
                        "title": _("Households"),
                        "link": reverse_lazy("admin:household_household_changelist"),
                        "icon": "group",
                    },
                    {
                        "title": _("Individuals"),
                        "link": reverse_lazy("admin:household_individual_changelist"),
                        "icon": "person",
                    },
                    {
                        "title": _("Payment"),
                        "link": reverse_lazy("admin:app_list", args=["payment"]),
                        "icon": "payments",
                    },
                ],
            },
            {
                "title": _("RDI"),
                "items": [
                    {
                        "title": _("Registration Data"),
                        "link": reverse_lazy(
                            "admin:app_list", args=["registration_data"]
                        ),
                        "icon": "upload_file",
                    },
                ],
            },
            {
                "title": _("Grievance"),
                "items": [
                    {
                        "title": _("Grievances"),
                        "link": reverse_lazy("admin:app_list", args=["grievance"]),
                        "icon": "report_problem",
                    },
                ],
            },
            {
                "title": _("Configuration"),
                "items": [
                    {
                        "title": _("Core"),
                        "link": reverse_lazy("admin:app_list", args=["core"]),
                        "icon": "settings",
                    },
                    {
                        "title": _("Constance"),
                        "link": reverse_lazy("admin:app_list", args=["constance"]),
                        "icon": "tune",
                    },
                    {
                        "title": _("Feature Flags"),
                        "link": reverse_lazy("admin:app_list", args=["flags"]),
                        "icon": "flag",
                    },
                ],
            },
            {
                "title": _("Rule Engine"),
                "items": [
                    {
                        "title": _("Steficon"),
                        "link": reverse_lazy("admin:app_list", args=["steficon"]),
                        "icon": "code",
                    },
                ],
            },
            {
                "title": _("Security"),
                "items": [
                    {
                        "title": _("Accounts"),
                        "link": reverse_lazy("admin:app_list", args=["account"]),
                        "icon": "manage_accounts",
                    },
                    {
                        "title": _("Auth"),
                        "link": reverse_lazy("admin:app_list", args=["auth"]),
                        "icon": "lock",
                    },
                ],
            },
            {
                "title": _("Logs"),
                "items": [
                    {
                        "title": _("Log Entries"),
                        "link": reverse_lazy("admin:admin_logentry_changelist"),
                        "icon": "history",
                    },
                    {
                        "title": _("Activity Log"),
                        "link": reverse_lazy("admin:app_list", args=["activity_log"]),
                        "icon": "timeline",
                    },
                ],
            },
            {
                "title": _("Kobo"),
                "items": [
                    {
                        "title": _("Flexible Attributes"),
                        "link": reverse_lazy("admin:core_flexibleattribute_changelist"),
                        "icon": "edit_note",
                    },
                    {
                        "title": _("Flexible Attribute Groups"),
                        "link": reverse_lazy(
                            "admin:core_flexibleattributegroup_changelist"
                        ),
                        "icon": "folder_open",
                    },
                    {
                        "title": _("XLSX Kobo Templates"),
                        "link": reverse_lazy("admin:core_xlsxkobotemplate_changelist"),
                        "icon": "description",
                    },
                ],
            },
            {
                "title": _("System"),
                "items": [
                    {
                        "title": _("Social Auth"),
                        "link": reverse_lazy("admin:app_list", args=["social_django"]),
                        "icon": "share",
                    },
                    {
                        "title": _("Sites"),
                        "link": reverse_lazy("admin:app_list", args=["sites"]),
                        "icon": "language",
                    },
                ],
            },
            {
                "title": _("Console"),
                "items": [
                    {
                        "title": _("Clear Cache"),
                        "link": reverse_lazy("admin:clear_cache"),
                        "icon": "delete_sweep",
                    },
                    {
                        "title": _("Migrations"),
                        "link": reverse_lazy("admin:panel_migrations"),
                        "icon": "storage",
                    },
                    {
                        "title": _("System Info"),
                        "link": reverse_lazy("admin:panel_sysinfo"),
                        "icon": "info",
                    },
                    {
                        "title": _("Test Email"),
                        "link": reverse_lazy("admin:panel_email"),
                        "icon": "email",
                    },
                    {
                        "title": _("Sentry"),
                        "link": reverse_lazy("admin:panel_sentry"),
                        "icon": "bug_report",
                    },
                    {
                        "title": _("Error Pages"),
                        "link": reverse_lazy("admin:panel_error_page"),
                        "icon": "error",
                    },
                    {
                        "title": _("Redis CLI"),
                        "link": reverse_lazy("admin:panel_redis"),
                        "icon": "terminal",
                    },
                    {
                        "title": _("Elasticsearch"),
                        "link": reverse_lazy("admin:panel_elasticsearch"),
                        "icon": "search",
                    },
                ],
            },
        ],
    },
    "COLORS": {
        "primary": {
            "50": "#e3f2fd",
            "100": "#bbdefb",
            "200": "#90caf9",
            "300": "#64b5f6",
            "400": "#42a5f5",
            "500": "#00ADEF",
            "600": "#1e88e5",
            "700": "#1976d2",
            "800": "#1565c0",
            "900": "#0d47a1",
            "950": "#0a3a7e",
        },
    },
}


def environment_callback(request):
    """Return environment name and color for the admin header banner."""
    host = request.get_host()
    url = request.build_absolute_uri()

    color_map = {
        "localhost": ("Local", "#FF6600"),
        "trn": ("Training", "#BF360C"),
        "stg": ("Staging", "#673AB7"),
        "dev": ("Development", "#00796B"),
        "eph": ("Ephemeral", "#CC00EF"),
        "tst": ("Test", "#EF00A7"),
    }

    if "localhost" in host:
        return color_map["localhost"]

    for env_key, (label, color) in color_map.items():
        if env_key in url:
            return label, color

    return "Production", "#00ADEF"
