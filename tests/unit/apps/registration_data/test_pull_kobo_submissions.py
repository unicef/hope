import json
from pathlib import Path
from typing import Any
from unittest import mock

import pytest

from extras.test_utils.factories import BusinessAreaFactory, KoboImportDataFactory, ProgramFactory
from hope.apps.registration_data.tasks.pull_kobo_submissions import PullKoboSubmissions
from hope.models import KoboImportData

pytestmark = pytest.mark.django_db

FILES_DIR = Path(__file__).resolve().parent / "test_file"


@pytest.fixture
def kobo_settings(settings: Any) -> None:
    settings.KOBO_MASTER_API_TOKEN = "token-from-env"
    settings.KOBO_URL = "https://kf.hope.unicef.org"


@pytest.fixture
def kobo_context(kobo_settings: None) -> dict:
    business_area = BusinessAreaFactory(slug="afghanistan", name="Afghanistan")
    program = ProgramFactory(business_area=business_area)
    kobo_import_data = KoboImportDataFactory(
        status=KoboImportData.STATUS_PENDING,
        business_area_slug="afghanistan",
        data_type=KoboImportData.JSON,
        kobo_asset_id="aWnA2d5YBBDgQ5WZXpbaRe",
        only_active_submissions=False,
    )
    return {"business_area": business_area, "program": program, "kobo_import_data": kobo_import_data}


def test_pull_kobo_submissions(kobo_context: dict) -> None:
    content = (FILES_DIR / "kobo_submissions_collectors.json").read_text()
    submissions = json.loads(content)
    with mock.patch(
        "hope.apps.registration_data.tasks.pull_kobo_submissions.KoboAPI.get_project_submissions",
        return_value=submissions,
    ):
        service = PullKoboSubmissions()
        result = service.execute(kobo_context["kobo_import_data"], kobo_context["program"])

    kobo_context["kobo_import_data"].refresh_from_db()
    assert kobo_context["kobo_import_data"].id == result["kobo_import_data_id"]
