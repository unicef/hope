import json
import logging

import requests
from django.conf import settings
from django.contrib.staticfiles.storage import staticfiles_storage
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.templatetags.static import static
from django.views.decorators.cache import never_cache

logger = logging.getLogger(__name__)


def get_manifest() -> dict[str, dict[str, str]]:
    manifest_path = settings.MANIFEST_FILE
    manifest_url = staticfiles_storage.url(manifest_path)

    if manifest_url.startswith("http"):
        response = requests.get(manifest_url, timeout=60)
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            logger.warning(e)
            raise
        return response.json()

    path = f"{settings.PROJECT_ROOT}/apps/web/static/{manifest_path}"
    with open(path) as f:
        return json.loads(f.read())


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
