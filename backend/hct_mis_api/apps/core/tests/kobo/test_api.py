from typing import Any

import pytest

from hct_mis_api.apps.core.kobo.api import CountryCodeNotProvided, KoboAPI
from hct_mis_api.apps.core.models import BusinessArea


class TestKoboAPI:
    @pytest.fixture(autouse=True)
    def use_kobo_master_token(self, settings: Any) -> None:
        settings.KOBO_MASTER_API_TOKEN = "token-from-env"
        settings.KOBO_KF_URL = "https://kf.hope.unicef.org"

    @pytest.mark.override_config(KOBO_ENABLE_SINGLE_USER_ACCESS=False)
    def test_kobo_token_provided_from_business_area(self) -> None:
        business_area = BusinessArea(kobo_token="token-from-business-area")
        service = KoboAPI(token=business_area.get_kobo_token())
        assert service._token == "token-from-business-area"

    @pytest.mark.override_config(KOBO_ENABLE_SINGLE_USER_ACCESS=True)
    def test_kobo_token_provided_from_settings(self) -> None:
        business_area = BusinessArea(kobo_token="token-from-business-area")
        service = KoboAPI(token=business_area.get_kobo_token())
        assert service._token == "token-from-env"

    def test_kobo_token_default_parameters(self) -> None:
        service = KoboAPI()
        assert service._token == "token-from-env"

    def test_get_all_projects_with_not_provided_country_code(self) -> None:
        service = KoboAPI()

        with pytest.raises(CountryCodeNotProvided):
            service.get_all_projects_data(None)  # type: ignore[arg-type]

    @pytest.mark.vcr()
    @pytest.mark.override_config(KOBO_ENABLE_SINGLE_USER_ACCESS=True)
    def test_get_all_projects_filter_by_country_code(self) -> None:
        service = KoboAPI()
        projects = service.get_all_projects_data("AFG")
        assert len(projects) == 117
        assert "AFG" in projects[0]["settings"]["country_codes"]

    @pytest.mark.vcr()
    @pytest.mark.override_config(KOBO_ENABLE_SINGLE_USER_ACCESS=True)
    def test_get_single_project_data(self) -> None:
        service = KoboAPI()
        project_data = service.get_single_project_data("aWnA2d5YBBDgQ5WZXpbaRe")
        assert project_data

    @pytest.mark.vcr()
    @pytest.mark.override_config(KOBO_ENABLE_SINGLE_USER_ACCESS=True)
    def test_get_project_submissions(self) -> None:
        service = KoboAPI()
        service.LIMIT = 10
        submissions = service.get_project_submissions("aWnA2d5YBBDgQ5WZXpbaRe", only_active_submissions=False)
        assert len(submissions) == 10

    @pytest.mark.vcr()
    @pytest.mark.override_config(KOBO_ENABLE_SINGLE_USER_ACCESS=True)
    def test_get_project_submissions_only_active_submissions(self) -> None:
        service = KoboAPI()
        service.LIMIT = 10
        submissions = service.get_project_submissions("aWnA2d5YBBDgQ5WZXpbaRe", only_active_submissions=True)
        assert len(submissions) == 0
