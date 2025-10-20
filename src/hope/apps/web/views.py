import json
import logging
from pathlib import Path

from django.conf import settings
from django.contrib.staticfiles.storage import staticfiles_storage
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.templatetags.static import static
from django.views.decorators.cache import never_cache
import requests

logger = logging.getLogger(__name__)


def get_manifest() -> dict[str, dict[str, str]]:
    manifest_path = settings.MANIFEST_FILE
    manifest_url = staticfiles_storage.url(manifest_path)

    if manifest_url.startswith("http"):
        response = requests.get(manifest_url, timeout=60)
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            logger.error("Failed to fetch manifest: %s", e)
            return {}
        return response.json()

    # Safe local path resolution
    path = Path(settings.PROJECT_ROOT) / "apps/web/static" / manifest_path
    if not path.exists():
        logger.error("Manifest file does not exist at %s", path)
        return {}

    with path.open() as f:
        return json.load(f)


@never_cache
def react_main(request: HttpRequest) -> HttpResponse:
    manifest = get_manifest()
    context = {
        "assets": {
            "file": static(f"web/{manifest['src/main.tsx']['file']}"),
            "css": (static(f"web/{css}") for css in manifest["src/main.tsx"]["css"]),
        },
        "settings": settings,
    }
    return render(request, "web/index.html", context)
