"""Tests for the es_bootstrap_aliases management command (clone-first blue-green bootstrap).

All ES traffic is mocked - the tests assert the SEQUENCE the command drives (write-block, clone,
count sanity, atomic remove_index+add, unblock) and its state machine (skip on alias, create-v1 on
missing, resume after crash, lock, dry-run). DB is used only for the Program the doc factories need.
"""

from io import StringIO
from unittest.mock import MagicMock, patch

from django.core.management import call_command
from django.core.management.base import CommandError
from elasticsearch import BadRequestError
import pytest

from extras.test_utils.factories import ProgramFactory
from hope.apps.household.documents import get_household_doc, get_individual_doc
from hope.apps.household.management.commands.es_bootstrap_aliases import Command
from hope.apps.household.services.index_management import create_program_indexes
from hope.models import Program

pytestmark = pytest.mark.django_db

CMD = "es_bootstrap_aliases"
_MOD = "hope.apps.household.management.commands.es_bootstrap_aliases"
GET_CONN = "elasticsearch.dsl.connections.get_connection"
DELTA_CALL = f"{_MOD}.call_command"


@pytest.fixture
def program() -> Program:
    return ProgramFactory(status=Program.ACTIVE)


@pytest.fixture
def index_names(program: Program) -> list[str]:
    return [
        get_individual_doc(str(program.id))._index._name,
        get_household_doc(str(program.id))._index._name,
    ]


def _make_es(*, alias_exists: bool = False, index_exists: bool = True, target_exists: bool = False) -> MagicMock:
    """Mock ES for one uniform pre-bootstrap state across all index names."""
    es = MagicMock()
    es.indices.exists_alias.return_value = alias_exists
    es.indices.exists.side_effect = lambda **kw: target_exists if kw["index"].endswith("_v1") else index_exists
    es.cluster.health.return_value = {"status": "green"}
    es.count.return_value = {"count": 5}
    es.indices.get_settings.side_effect = lambda **kw: {
        kw["index"]: {"settings": {"index": {"number_of_replicas": "0"}}}
    }
    es.indices.get_alias.side_effect = lambda **kw: {f"{kw['name']}_v1": {"aliases": {kw["name"]: {}}}}
    return es


@pytest.fixture
def es_bare() -> MagicMock:
    return _make_es()


@pytest.fixture
def es_aliased() -> MagicMock:
    return _make_es(alias_exists=True)


@pytest.fixture
def es_missing() -> MagicMock:
    return _make_es(index_exists=False)


@pytest.fixture
def es_resume() -> MagicMock:
    return _make_es(target_exists=True)


@pytest.fixture
def es_count_mismatch() -> MagicMock:
    es = _make_es()
    es.count.side_effect = lambda **kw: {"count": 3 if kw["index"].endswith("_v1") else 5}
    return es


@pytest.fixture
def es_yellow() -> MagicMock:
    es = _make_es()
    es.cluster.health.return_value = {"status": "yellow"}
    return es


@pytest.fixture
def es_locked() -> MagicMock:
    es = _make_es()
    es.indices.create.side_effect = BadRequestError("resource_already_exists_exception", MagicMock(), None)
    return es


def test_requires_exactly_one_scope() -> None:
    with pytest.raises(CommandError, match="exactly one scope"):
        call_command(CMD)


def test_bootstrap_runs_full_sequence_per_index(program: Program, index_names: list[str], es_bare: MagicMock) -> None:
    with patch(GET_CONN, return_value=es_bare), patch(DELTA_CALL) as delta:
        call_command(CMD, program=str(program.id), stdout=StringIO())

    cloned = [kw["index"] for _, kw in es_bare.indices.clone.call_args_list]
    assert sorted(cloned) == sorted(index_names)
    actions = [kw["actions"] for _, kw in es_bare.indices.update_aliases.call_args_list]
    assert all("remove_index" in a[0] and "add" in a[1] for a in actions)
    assert delta.call_count == 1


def test_bootstrap_write_blocks_source_before_clone(program: Program, es_bare: MagicMock) -> None:
    with patch(GET_CONN, return_value=es_bare), patch(DELTA_CALL):
        call_command(CMD, program=str(program.id), stdout=StringIO())

    first_block = [kw for _, kw in es_bare.indices.put_settings.call_args_list][0]
    assert first_block["settings"] == {"index.blocks.write": True}


def test_bootstrap_unblocks_and_restores_replicas_on_target(program: Program, es_bare: MagicMock) -> None:
    with patch(GET_CONN, return_value=es_bare), patch(DELTA_CALL):
        call_command(CMD, program=str(program.id), stdout=StringIO())

    final = [kw for _, kw in es_bare.indices.put_settings.call_args_list][-1]
    assert final["index"].endswith("_v1")
    assert final["settings"] == {"index.blocks.write": None, "index.number_of_replicas": "0"}


def test_skip_when_alias_already_exists(program: Program, es_aliased: MagicMock) -> None:
    out = StringIO()
    with patch(GET_CONN, return_value=es_aliased), patch(DELTA_CALL):
        call_command(CMD, program=str(program.id), stdout=out)

    es_aliased.indices.clone.assert_not_called()
    es_aliased.indices.update_aliases.assert_not_called()
    assert "skip (already alias)" in out.getvalue()


def test_missing_index_creates_v1_with_alias(program: Program, index_names: list[str], es_missing: MagicMock) -> None:
    with patch(GET_CONN, return_value=es_missing), patch(DELTA_CALL):
        call_command(CMD, program=str(program.id), stdout=StringIO())

    es_missing.indices.clone.assert_not_called()
    versioned = [kw for _, kw in es_missing.indices.create.call_args_list if "aliases" in kw]
    assert sorted(kw["index"] for kw in versioned) == sorted(f"{n}_v1" for n in index_names)
    assert all(kw["aliases"] == {kw["index"].removesuffix("_v1"): {}} for kw in versioned)


def test_resume_after_crash_skips_clone_but_redoes_takeover(program: Program, es_resume: MagicMock) -> None:
    with patch(GET_CONN, return_value=es_resume), patch(DELTA_CALL):
        call_command(CMD, program=str(program.id), stdout=StringIO())

    es_resume.indices.clone.assert_not_called()
    assert es_resume.indices.update_aliases.call_count == 2


def test_count_mismatch_aborts_before_takeover_and_unblocks_source(
    program: Program, es_count_mismatch: MagicMock
) -> None:
    with (
        patch(GET_CONN, return_value=es_count_mismatch),
        patch(DELTA_CALL),
        pytest.raises(CommandError, match="failed"),
    ):
        call_command(CMD, program=str(program.id), stdout=StringIO())

    es_count_mismatch.indices.update_aliases.assert_not_called()
    unblocks = [
        kw
        for _, kw in es_count_mismatch.indices.put_settings.call_args_list
        if kw["settings"] == {"index.blocks.write": None}
    ]
    assert len(unblocks) == 2


def test_cluster_not_green_aborts(program: Program, es_yellow: MagicMock) -> None:
    with patch(GET_CONN, return_value=es_yellow), pytest.raises(CommandError, match="GREEN"):
        call_command(CMD, program=str(program.id), stdout=StringIO())


def test_lock_held_by_another_run_refuses(program: Program, es_locked: MagicMock) -> None:
    with patch(GET_CONN, return_value=es_locked), pytest.raises(CommandError, match="lock"):
        call_command(CMD, program=str(program.id), stdout=StringIO())


def test_lock_released_after_run(program: Program, es_bare: MagicMock) -> None:
    with patch(GET_CONN, return_value=es_bare), patch(DELTA_CALL):
        call_command(CMD, program=str(program.id), stdout=StringIO())

    deleted = [kw["index"] for _, kw in es_bare.options.return_value.indices.delete.call_args_list]
    assert Command.LOCK_INDEX in deleted


def test_dry_run_touches_nothing(program: Program, es_bare: MagicMock) -> None:
    out = StringIO()
    with patch(GET_CONN, return_value=es_bare), patch(DELTA_CALL) as delta:
        call_command(CMD, program=str(program.id), dry_run=True, stdout=out)

    es_bare.indices.clone.assert_not_called()
    es_bare.indices.update_aliases.assert_not_called()
    es_bare.indices.create.assert_not_called()
    assert delta.call_count == 0
    assert "BOOTSTRAP (clone-first)" in out.getvalue()


def test_status_reports_bare_state(program: Program, es_bare: MagicMock) -> None:
    out = StringIO()
    with patch(GET_CONN, return_value=es_bare):
        call_command(CMD, program=str(program.id), status=True, stdout=out)

    assert "BARE physical (pre-bootstrap)" in out.getvalue()
    es_bare.indices.clone.assert_not_called()


def test_skip_delta_skips_the_sweep(program: Program, es_bare: MagicMock) -> None:
    with patch(GET_CONN, return_value=es_bare), patch(DELTA_CALL) as delta:
        call_command(CMD, program=str(program.id), skip_delta=True, stdout=StringIO())

    assert delta.call_count == 0


def test_create_program_indexes_creates_v1_plus_alias(program: Program, index_names: list[str]) -> None:
    es = _make_es(index_exists=False)
    with patch(GET_CONN, return_value=es):
        ok, msg = create_program_indexes(str(program.id))

    assert ok, msg
    created = [kw for _, kw in es.indices.create.call_args_list]
    assert sorted(kw["index"] for kw in created) == sorted(f"{n}_v1" for n in index_names)
    assert all(kw["aliases"] == {kw["index"].removesuffix("_v1"): {}} for kw in created)
