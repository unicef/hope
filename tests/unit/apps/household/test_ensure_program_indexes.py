"""Tests for ensure_program_indexes and the defused automatic ES entrypoints.

Automatic paths (program-activation signal, rebuild_search_index) must never delete a live index —
they route through ensure_program_indexes: create missing ``_v1``+alias indexes and upsert-populate.
ES is mocked; the assertions are about which ES operations are (not) driven.
"""

from unittest.mock import MagicMock, patch

from constance.test import override_config
import pytest

from extras.test_utils.factories import ProgramFactory
from hope.apps.household.services.index_management import ensure_program_indexes
from hope.models import Program

pytestmark = pytest.mark.django_db

_IM = "hope.apps.household.services.index_management"
GET_CONN = "elasticsearch.dsl.connections.get_connection"


@pytest.fixture
def program() -> Program:
    return ProgramFactory(status=Program.ACTIVE)


@pytest.fixture
def draft_program() -> Program:
    return ProgramFactory(status=Program.DRAFT)


@pytest.fixture
def es_no_indexes() -> MagicMock:
    es = MagicMock()
    es.indices.exists.return_value = False
    return es


@pytest.fixture
def es_with_indexes() -> MagicMock:
    es = MagicMock()
    es.indices.exists.return_value = True
    return es


def test_ensure_creates_versioned_indexes_when_missing(program: Program, es_no_indexes: MagicMock) -> None:
    with patch(GET_CONN, return_value=es_no_indexes):
        ok, msg = ensure_program_indexes(str(program.id))

    assert ok, msg
    created = [kw for _, kw in es_no_indexes.indices.create.call_args_list]
    assert all(kw["index"].endswith("_v1") and kw["aliases"] for kw in created)
    assert len(created) == 2


def test_ensure_never_deletes(program: Program, es_with_indexes: MagicMock) -> None:
    with patch(GET_CONN, return_value=es_with_indexes):
        ok, _ = ensure_program_indexes(str(program.id))

    assert ok
    es_with_indexes.indices.delete.assert_not_called()
    es_with_indexes.options.return_value.indices.delete.assert_not_called()


def test_ensure_skips_create_when_index_exists(program: Program, es_with_indexes: MagicMock) -> None:
    with patch(GET_CONN, return_value=es_with_indexes):
        ok, _ = ensure_program_indexes(str(program.id))

    assert ok
    es_with_indexes.indices.create.assert_not_called()


def test_ensure_reports_create_failure(program: Program) -> None:
    with patch(f"{_IM}.create_program_indexes", return_value=(False, "boom")):
        ok, msg = ensure_program_indexes(str(program.id))

    assert not ok
    assert msg == "Create failed: boom"


def test_ensure_reports_populate_failure(program: Program) -> None:
    with (
        patch(f"{_IM}.create_program_indexes", return_value=(True, "")),
        patch(f"{_IM}.populate_program_indexes", return_value=(False, "boom")),
    ):
        ok, msg = ensure_program_indexes(str(program.id))

    assert not ok
    assert msg == "Populate failed: boom"


@override_config(IS_ELASTICSEARCH_ENABLED=True)
def test_program_activation_signal_uses_ensure_not_rebuild(draft_program: Program) -> None:
    with (
        patch(f"{_IM}.ensure_program_indexes") as ensure,
        patch(f"{_IM}.rebuild_program_indexes") as rebuild,
    ):
        draft_program.status = Program.ACTIVE
        draft_program.save()

    ensure.assert_called_once_with(str(draft_program.pk))
    rebuild.assert_not_called()
