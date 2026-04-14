from django.templatetags.static import static
from django.utils.functional import lazy

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
    "STYLES": [
        lambda request: static("admin/css/hope_admin.css"),
    ],
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": True,
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


def environment_callback(request: object) -> tuple[str, str]:
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
