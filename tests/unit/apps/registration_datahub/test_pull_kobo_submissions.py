import json
from pathlib import Path
from typing import Any
from unittest import mock

from django.conf import settings
import pytest

from extras.test_utils.factories.core import create_afghanistan
from extras.test_utils.factories.program import ProgramFactory
from hope.models.kobo_import_data import KoboImportData
from hope.apps.registration_datahub.tasks.pull_kobo_submissions import (
    PullKoboSubmissions,
)

pytestmark = pytest.mark.django_db(databases=(("default",)), transaction=True)


class TestPullKoboSubmissions:
    @pytest.fixture(autouse=True)
    def use_kobo_master_token(self, settings: Any) -> None:
        settings.KOBO_MASTER_API_TOKEN = "token-from-env"
        settings.KOBO_URL = "https://kf.hope.unicef.org"

    def test_pull_kobo_submissions(self) -> None:
        create_afghanistan()
        kobo_import_data = KoboImportData(
            status=KoboImportData.STATUS_PENDING,
            business_area_slug="afghanistan",
            data_type=KoboImportData.JSON,
            kobo_asset_id="aWnA2d5YBBDgQ5WZXpbaRe",
            only_active_submissions=False,
        )
        kobo_import_data.save()
        program = ProgramFactory()

        content = Path(
            f"{settings.TESTS_ROOT}/apps/registration_datahub/test_file/kobo_submissions_collectors.json"
        ).read_text()
        content = json.loads(content)
        with mock.patch(
            "hope.apps.registration_datahub.tasks.pull_kobo_submissions.KoboAPI.get_project_submissions",
            return_value=content,
        ):
            service = PullKoboSubmissions()
            result = service.execute(kobo_import_data, program)

        kobo_import_data.refresh_from_db()
        assert kobo_import_data.id == result["kobo_import_data_id"]
