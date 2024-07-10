import datetime
from typing import Any

import pytest
from dateutil.tz import tzlocal
from graphql import GraphQLError

from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.schema import resolve_assets_list
from hct_mis_api.apps.geo.fixtures import CountryFactory

pytestmark = pytest.mark.django_db(transaction=True)


class TestResolveAssetsList:
    @pytest.fixture(autouse=True)
    def use_kobo_master_token(self, settings: Any) -> None:
        settings.KOBO_MASTER_API_TOKEN = "test-token"
        settings.KOBO_KF_URL = "https://kf.hope.unicef.org"
        settings.KOBO_PROJECT_VIEWS_ID = "pvEsUUfAgYyyV7jpR6i3FvM"

    def test_resolve_assets_list_wrong_business_area(self) -> None:
        with pytest.raises(GraphQLError):
            resolve_assets_list("wrong_business_area")

    def test_resolve_assets_list_without_country_code(self) -> None:
        create_afghanistan()
        with pytest.raises(GraphQLError):
            resolve_assets_list("afghanistan")

    @pytest.mark.vcr()
    def test_resolve_assets_list(self) -> None:
        business_area = create_afghanistan()
        country = CountryFactory()
        business_area.countries.add(country)

        result = resolve_assets_list("afghanistan")
        assert len(result) == 68
        assert result[0] == {
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
