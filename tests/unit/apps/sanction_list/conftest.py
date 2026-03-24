from pathlib import Path
from typing import Any, Generator

import pytest
from responses import RequestsMock

from hope.apps.core.celery import app
from hope.models import SanctionList


@pytest.fixture
def mocked_responses() -> Generator[RequestsMock, None, None]:
    with RequestsMock() as rsps:
        yield rsps


@pytest.fixture
def eu_file() -> str:
    return (Path(__file__).parent / "test_files" / "eu.xml").read_text()


@pytest.fixture
def always_eager() -> Generator[Any, None, None]:
    status = app.conf.task_always_eager
    app.conf.task_always_eager = False
    yield
    app.conf.task_always_eager = status


@pytest.fixture
def sanction_list(db: Any) -> SanctionList:
    sanction_list, _ = SanctionList.objects.get_or_create(
        pk=123,
        name="EU",
        strategy="hope.apps.sanction_list.strategies.eu.EUSanctionList",
        config={
            "url": "http://example.com/sl.xml",
        },
    )
    return sanction_list
