"""Tests for es_drop_old_index_versions (sweep unaliased _vN leftovers, never touch aliased ones)."""

from io import StringIO
from unittest.mock import MagicMock, patch

from django.core.management import call_command
from django.core.management.base import CommandError
import pytest

from extras.test_utils.factories import ProgramFactory
from hope.apps.household.documents import get_household_doc, get_individual_doc
from hope.models import Program

pytestmark = pytest.mark.django_db

CMD = "es_drop_old_index_versions"
GET_CONN = "elasticsearch.dsl.connections.get_connection"


@pytest.fixture
def program() -> Program:
    return ProgramFactory(status=Program.ACTIVE)


@pytest.fixture
def index_names(program: Program) -> list[str]:
    return [
        get_individual_doc(str(program.id))._index._name,
        get_household_doc(str(program.id))._index._name,
    ]


def _make_es(*, aliased: bool = True) -> MagicMock:
    """Every name: alias on _v2; leftovers _v1 (unaliased), _v3 (aliased elsewhere) and
    _v2_backup (unaliased but NOT a strict _vN name - the wildcard still matches it)."""
    es = MagicMock()
    es.indices.exists_alias.return_value = aliased
    es.indices.get_alias.side_effect = lambda **kw: {f"{kw['name']}_v2": {"aliases": {kw["name"]: {}}}}
    es.indices.get.side_effect = lambda **kw: {
        kw["index"].replace("_v*", "_v1"): {"aliases": {}},
        kw["index"].replace("_v*", "_v2"): {"aliases": {kw["index"].removesuffix("_v*"): {}}},
        kw["index"].replace("_v*", "_v3"): {"aliases": {"someone-elses-alias": {}}},
        kw["index"].replace("_v*", "_v2_backup"): {"aliases": {}},
    }
    return es


@pytest.fixture
def es_aliased() -> MagicMock:
    return _make_es()


@pytest.fixture
def es_not_aliased() -> MagicMock:
    return _make_es(aliased=False)


def test_requires_exactly_one_scope() -> None:
    with pytest.raises(CommandError, match="exactly one scope"):
        call_command(CMD)


def test_without_confirm_lists_but_deletes_nothing(program: Program, es_aliased: MagicMock) -> None:
    out = StringIO()
    with patch(GET_CONN, return_value=es_aliased):
        call_command(CMD, program=str(program.id), stdout=out)

    es_aliased.indices.delete.assert_not_called()
    assert "Would drop 2" in out.getvalue()


def test_confirm_deletes_only_unaliased_old_versions(
    program: Program, index_names: list[str], es_aliased: MagicMock
) -> None:
    with patch(GET_CONN, return_value=es_aliased):
        call_command(CMD, program=str(program.id), confirm=True, stdout=StringIO())

    deleted = [kw["index"] for _, kw in es_aliased.indices.delete.call_args_list]
    assert sorted(deleted) == sorted(f"{n}_v1" for n in index_names)


def test_aliased_leftover_is_skipped_with_warning(program: Program, es_aliased: MagicMock) -> None:
    out = StringIO()
    with patch(GET_CONN, return_value=es_aliased):
        call_command(CMD, program=str(program.id), confirm=True, stdout=out)

    deleted = [kw["index"] for _, kw in es_aliased.indices.delete.call_args_list]
    assert not any(name.endswith("_v3") for name in deleted)
    assert "has aliases attached - skipped" in out.getvalue()


def test_non_strict_version_name_is_never_deleted(program: Program, es_aliased: MagicMock) -> None:
    # the _v* wildcard also matches names like <name>_v2_backup - unaliased, so it looks
    # exactly like a leftover, but it is not a strict _vN name and is not ours to delete
    with patch(GET_CONN, return_value=es_aliased):
        call_command(CMD, program=str(program.id), confirm=True, stdout=StringIO())

    deleted = [kw["index"] for _, kw in es_aliased.indices.delete.call_args_list]
    assert not any(name.endswith("_v2_backup") for name in deleted)


def test_non_alias_name_is_skipped(program: Program, es_not_aliased: MagicMock) -> None:
    out = StringIO()
    with patch(GET_CONN, return_value=es_not_aliased):
        call_command(CMD, program=str(program.id), confirm=True, stdout=out)

    es_not_aliased.indices.delete.assert_not_called()
    assert "not an alias - skipped" in out.getvalue()
