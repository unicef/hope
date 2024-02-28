import json
import logging
from typing import Dict

import requests
from django.conf import settings
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.templatetags.static import static
from django.views.decorators.cache import never_cache

logger = logging.getLogger(__name__)


def get_manifest() -> Dict[str, Dict[str, str]]:
    manifest_file = settings.MANIFEST_FILE
    if settings.DEBUG:
        with open(manifest_file, "r") as f:
            return json.loads(f.read())
    response = requests.get(manifest_file)
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        logger.exception(e)
        raise
    return response.json()


@never_cache
def react_main(request: HttpRequest) -> HttpResponse:
    manifest = get_manifest()
    context = {
        "assets": {
            "file": static(f"web/{manifest['src/main.tsx']['file']}"),
            "css": map(lambda css: static(f"web/{css}"), manifest["src/main.tsx"]["css"]),
        },
        "settings": settings,
    }
    return render(request, "web/index.html", context)
