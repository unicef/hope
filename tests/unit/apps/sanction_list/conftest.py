from pathlib import Path
from typing import TYPE_CHECKING, Any, Generator

import pytest
from responses import RequestsMock

from hope.apps.core.celery import app

if TYPE_CHECKING:
    from hope.models.sanction_list import SanctionList


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
def sanction_list(db: Any) -> "SanctionList":
    from test_utils.factories.sanction_list import SanctionListFactory

    return SanctionListFactory(
        name="EU",
        strategy="hope.apps.sanction_list.strategies.eu.EUSanctionList",
        config={
            "url": "http://example.com/sl.xml",
        },
    )
