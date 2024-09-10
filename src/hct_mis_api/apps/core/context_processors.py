from typing import TypedDict

from django.conf import settings
from django.http import HttpRequest


class MatomoConfig(TypedDict):
    MATOMO_SITE_ID: str
    MATOMO_TRACKER_URL: str
    MATOMO_SCRIPT_URL: str


def matomo(request: HttpRequest) -> MatomoConfig:
    return {
        "MATOMO_SITE_ID": settings.MATOMO_SITE_ID,
        "MATOMO_TRACKER_URL": settings.MATOMO_TRACKER_URL,
        "MATOMO_SCRIPT_URL": settings.MATOMO_SCRIPT_URL,
    }
