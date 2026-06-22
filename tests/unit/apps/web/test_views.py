import json
import logging
from typing import Any

from django.test import RequestFactory
import pytest

from hope.apps.web.views import get_manifest, react_main

pytestmark = pytest.mark.django_db


@pytest.fixture
def manifest_content() -> dict[str, dict[str, Any]]:
    return {
        "src/main.tsx": {
            "file": "assets/main-abc123.js",
            "css": ["assets/main-abc123.css", "assets/vendor-def456.css"],
        }
    }


@pytest.fixture
def manifest_on_disk(
    settings: Any, tmp_path: Any, manifest_content: dict[str, dict[str, Any]]
) -> dict[str, dict[str, Any]]:
    settings.PROJECT_ROOT = str(tmp_path)
    settings.MANIFEST_FILE = "manifest.json"
    static_dir = tmp_path / "apps" / "web" / "static"
    static_dir.mkdir(parents=True)
    (static_dir / "manifest.json").write_text(json.dumps(manifest_content))
    return manifest_content


def test_get_manifest_returns_parsed_json(manifest_on_disk: dict[str, dict[str, Any]]) -> None:
    assert get_manifest() == manifest_on_disk


def test_get_manifest_returns_empty_dict_and_logs_error_when_file_missing(
    settings: Any, tmp_path: Any, caplog: pytest.LogCaptureFixture
) -> None:
    settings.PROJECT_ROOT = str(tmp_path)
    settings.MANIFEST_FILE = "missing-manifest.json"

    with caplog.at_level(logging.ERROR, logger="hope.apps.web.views"):
        result = get_manifest()

    assert result == {}
    assert "Manifest file does not exist" in caplog.text


def test_react_main_renders_index_with_manifest_assets(manifest_on_disk: dict[str, dict[str, Any]]) -> None:
    request = RequestFactory().get("/")

    response = react_main(request)

    content = response.content.decode()
    assert response.status_code == 200
    assert '<script type="module" src="/api/static/web/assets/main-abc123.js"></script>' in content
    assert '<link rel="stylesheet" href="/api/static/web/assets/main-abc123.css" />' in content
    assert '<link rel="stylesheet" href="/api/static/web/assets/vendor-def456.css" />' in content


def test_react_main_response_is_never_cached(manifest_on_disk: dict[str, dict[str, Any]]) -> None:
    request = RequestFactory().get("/")

    response = react_main(request)

    assert "no-cache" in response["Cache-Control"]
