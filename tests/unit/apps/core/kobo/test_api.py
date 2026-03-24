from typing import Any

import pytest

from hope.apps.core.kobo.api import CountryCodeNotProvidedError, KoboAPI

pytestmark = pytest.mark.django_db


@pytest.fixture
def kobo_settings(settings: Any) -> None:
    settings.KOBO_MASTER_API_TOKEN = "test-token"
    settings.KOBO_URL = "https://kf.hope.unicef.org"
    settings.KOBO_PROJECT_VIEWS_ID = "pvEsUUfAgYyyV7jpR6i3FvM"


def test_get_all_projects_raises_error_when_country_code_not_provided(
    kobo_settings: None,
) -> None:
    service = KoboAPI()

    with pytest.raises(CountryCodeNotProvidedError):
        service.get_all_projects_data(None)  # type: ignore[arg-type]


@pytest.mark.vcr
def test_get_all_projects_filters_by_country_code(
    kobo_settings: None,
) -> None:
    service = KoboAPI()
    projects = service.get_all_projects_data("AFG")
    assert len(projects) == 117
    assert "AFG" in projects[0]["settings"]["country_codes"]


@pytest.mark.vcr
def test_get_single_project_data_returns_project(
    kobo_settings: None,
) -> None:
    service = KoboAPI()
    project_data = service.get_single_project_data("aWnA2d5YBBDgQ5WZXpbaRe")
    assert project_data


@pytest.mark.vcr
def test_get_project_submissions_returns_limited_submissions(
    kobo_settings: None,
) -> None:
    service = KoboAPI()
    service.LIMIT = 10
    submissions = service.get_project_submissions("aWnA2d5YBBDgQ5WZXpbaRe", only_active_submissions=False)
    assert len(submissions) == 10


@pytest.mark.vcr
def test_get_project_submissions_returns_empty_for_active_only(
    kobo_settings: None,
) -> None:
    service = KoboAPI()
    service.LIMIT = 10
    submissions = service.get_project_submissions("aWnA2d5YBBDgQ5WZXpbaRe", only_active_submissions=True)
    assert len(submissions) == 0
