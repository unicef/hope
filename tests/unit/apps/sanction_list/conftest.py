from pathlib import Path
from typing import TYPE_CHECKING, Any, Generator

from django.core.management import call_command

import pytest
from responses import RequestsMock

import hct_mis_api
from hct_mis_api.apps.core.celery import app
from hct_mis_api.apps.geo.models import Country

if TYPE_CHECKING:
    from hct_mis_api.apps.sanction_list.models import SanctionList


@pytest.fixture
def mocked_responses() -> Generator[RequestsMock, None, None]:
    with RequestsMock() as rsps:
        yield rsps


@pytest.fixture
def eu_file() -> str:
    return (Path(__file__).parent / "test_files" / "eu.xml").read_text()


@pytest.fixture(autouse=True)
def countries(db: Any) -> None:
    Country.objects.create(**{
        "created_at": "2021-10-28 09:39:13.189-00:00",
        "updated_at": "2021-10-28 09:39:13.189-00:00",
        "original_id": None,
        "name": "Poland",
        "short_name": "Poland",
        "iso_code2": "PL",
        "iso_code3": "POL",
        "iso_num": "0616",
        "parent": None,
        "valid_from": "2021-10-28 09:39:13.189-00:00",
        "valid_until": None,
        "extras": {},
        "lft": 1,
        "rght": 2,
        "tree_id": 177,
        "level": 0
    })
    Country.objects.create(**{
        "created_at": "2021-10-28 09:39:12.804-00:00",
        "updated_at": "2021-10-28 09:39:12.804-00:00",
        "original_id": None,
        "name": "Iraq",
        "short_name": "Iraq",
        "iso_code2": "IQ",
        "iso_code3": "IRQ",
        "iso_num": "0368",
        "parent": None,
        "valid_from": "2021-10-28 09:39:12.804-00:00",
        "valid_until": None,
        "extras": {},
        "lft": 1,
        "rght": 2,
        "tree_id": 107,
        "level": 0
    })


@pytest.fixture()
def always_eager() -> Generator[Any, None, None]:
    status = app.conf.task_always_eager
    app.conf.task_always_eager = False
    yield
    app.conf.task_always_eager = status


@pytest.fixture()
def sanction_list(db: Any) -> "SanctionList":
    from test_utils.factories.sanction_list import SanctionListFactory

    sl = SanctionListFactory(
        name="EU",
        strategy="hct_mis_api.apps.sanction_list.strategies.eu.EUSanctionList",
        config={
            "url": "http://example.com/sl.xml",
        },
    )
    return sl
