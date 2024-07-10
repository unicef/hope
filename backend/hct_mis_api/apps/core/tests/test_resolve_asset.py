import datetime
from typing import Any

import pytest
from dateutil.tz import tzlocal

from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.schema import resolve_asset

pytestmark = pytest.mark.django_db(transaction=True)


class TestResolveAsset:
    @pytest.fixture(autouse=True)
    def use_kobo_master_token(self, settings: Any) -> None:
        settings.KOBO_MASTER_API_TOKEN = "token-from-env"
        settings.KOBO_KF_URL = "https://kf.hope.unicef.org"
        settings.KOBO_PROJECT_VIEWS_ID = "pvEsUUfAgYyyV7jpR6i3FvM"

    @pytest.mark.vcr()
    def test_resolve_asset(self) -> None:
        create_afghanistan()

        result = resolve_asset("afghanistan", "aWnA2d5YBBDgQ5WZXpbaRe")
        assert result == {
            "asset_type": "survey",
            "country": "Afghanistan",
            "date_modified": datetime.datetime(2023, 10, 4, 10, 38, 23, 610534, tzinfo=tzlocal()),
            "deployment_active": True,
            "has_deployment": True,
            "id": "aWnA2d5YBBDgQ5WZXpbaRe",
            "name": "PMU-REG-Cash_for Education-Nooristan-ACTED-Dec-2022",
            "sector": "Humanitarian - Coordination / Information Management",
            "xls_link": "https://kf.hope.unicef.org/api/v2/assets/aWnA2d5YBBDgQ5WZXpbaRe/?format=json.xls",
        }
