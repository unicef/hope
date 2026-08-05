"""Tests for the es_reindex management command (blue-green dark-index build + alias swap).

All ES traffic is mocked - the tests assert the SEQUENCE (dark create without alias, populate to
the suffixed target, pre-swap delta, verify gate, one atomic 4-action swap, post-swap deltas) and
the guard rails (alias prerequisite, verify abort, lock, dry-run/status read-only).
"""

from io import StringIO
from unittest.mock import MagicMock, patch

from constance.test import override_config
from django.core.management import call_command
from django.core.management.base import CommandError
from elasticsearch import BadRequestError
import pytest

from extras.test_utils.factories import ProgramFactory
from hope.apps.household.documents import get_household_doc, get_individual_doc
from hope.apps.household.management.commands.es_reindex import Command
from hope.models import Program

pytestmark = pytest.mark.django_db

CMD = "es_reindex"
_MOD = "hope.apps.household.management.commands.es_reindex"
GET_CONN = "elasticsearch.dsl.connections.get_connection"
DELTA_CALL = f"{_MOD}.call_command"
POPULATE = f"{_MOD}.populate_index"


@pytest.fixture
def program() -> Program:
    return ProgramFactory(status=Program.ACTIVE)


@pytest.fixture
def programs_same_code() -> list[Program]:
    return [ProgramFactory(status=Program.ACTIVE, code="SAME"), ProgramFactory(status=Program.ACTIVE, code="SAME")]


@pytest.fixture
def index_names(program: Program) -> list[str]:
    return [
        get_individual_doc(str(program.id))._index._name,
        get_household_doc(str(program.id))._index._name,
    ]


def _make_es(*, aliased: bool = True, alias_version: str = "v1", swap_flips_to: str = "v2") -> MagicMock:
    """Mock ES: every name aliased to ``alias_version``, flipping to ``swap_flips_to`` after the swap."""
    es = MagicMock()
    state = {"swapped": False}
    es.indices.exists_alias.return_value = aliased
    es.indices.exists.return_value = False  # no dark leftovers by default -> fresh create path

    def update_aliases(**kw: dict) -> MagicMock:
        state["swapped"] = True
        return MagicMock()

    es.indices.update_aliases.side_effect = update_aliases
    es.indices.get_alias.side_effect = lambda **kw: {
        f"{kw['name']}_{swap_flips_to if state['swapped'] else alias_version}": {"aliases": {}}
    }
    es.indices.get.side_effect = lambda **kw: {kw["index"].replace("_v*", f"_{alias_version}"): {}}
    es.indices.get_settings.side_effect = lambda **kw: {
        kw["index"]: {"settings": {"index": {"creation_date": "1700000000000"}}}
    }
    es.count.return_value = {"count": 0}
    return es


@pytest.fixture
def es_aliased() -> MagicMock:
    return _make_es()


@pytest.fixture
def es_not_aliased() -> MagicMock:
    return _make_es(aliased=False)


@pytest.fixture
def es_count_mismatch() -> MagicMock:
    es = _make_es()
    es.count.return_value = {"count": 5}
    return es


@pytest.fixture
def es_count_recovers() -> MagicMock:
    es = _make_es()
    es.count.side_effect = [{"count": 5}, {"count": 5}, {"count": 0}, {"count": 0}]
    return es


@pytest.fixture
def es_swap_does_not_flip() -> MagicMock:
    return _make_es(swap_flips_to="v1")


@pytest.fixture
def es_diverged_versions(index_names: list[str]) -> MagicMock:
    """Individuals index already on _v2, households still on _v1."""
    ind_name, hh_name = index_names
    es = _make_es()
    es.indices.get.side_effect = lambda **kw: (
        {f"{ind_name}_v1": {}, f"{ind_name}_v2": {}} if kw["index"].startswith(ind_name) else {f"{hh_name}_v1": {}}
    )
    es.indices.get_alias.side_effect = lambda **kw: {
        (f"{kw['name']}_v2" if kw["name"] == ind_name else f"{kw['name']}_v1"): {"aliases": {}}
    }
    return es


@pytest.fixture
def es_dark_wreck(index_names: list[str]) -> MagicMock:
    """Alias on _v1; a dark _v2 wreck lingers. Its mapping stamp is WRONG (older deployment)."""
    es = _make_es()
    physical = {name: {f"{name}_v1": {"aliases": {name: {}}}, f"{name}_v2": {"aliases": {}}} for name in index_names}

    def get_indices(**kw: dict) -> dict:
        name = kw["index"].removesuffix("_v*")
        return dict(physical.get(name, {}))

    def delete_index(**kw: dict) -> None:
        for indices in physical.values():
            indices.pop(kw["index"], None)

    es.indices.get.side_effect = get_indices
    es.indices.delete.side_effect = delete_index
    es.indices.exists.side_effect = lambda **kw: any(kw["index"] in indices for indices in physical.values())
    es.indices.get_mapping.side_effect = lambda **kw: {
        kw["index"]: {"mappings": {"_meta": {"hope_mapping_hash": "stale-deployment-hash"}}}
    }
    return es


@pytest.fixture
def es_resumable(program: Program, index_names: list[str]) -> MagicMock:
    """Alias on _v1; a dark _v2 leftover whose mapping stamp MATCHES the current code mapping."""
    from hope.apps.household.services.index_management import mapping_content_hash

    docs = [get_individual_doc(str(program.id)), get_household_doc(str(program.id))]
    hashes = {f"{doc._index._name}_v2": mapping_content_hash(doc._index.to_dict().get("mappings")) for doc in docs}
    es = _make_es()
    es.indices.exists.side_effect = lambda **kw: kw["index"] in hashes
    es.indices.get_mapping.side_effect = lambda **kw: {
        kw["index"]: {"mappings": {"_meta": {"hope_mapping_hash": hashes[kw["index"]]}}}
    }
    return es


@pytest.fixture
def es_sanity_window(index_names: list[str]) -> MagicMock:
    """Alias already on _v2; the old _v1 lingers unaliased as the rollback safety net."""
    es = _make_es(alias_version="v2", swap_flips_to="v3")
    es.indices.get.side_effect = lambda **kw: {
        kw["index"].replace("_v*", "_v1"): {"aliases": {}},
        kw["index"].replace("_v*", "_v2"): {"aliases": {kw["index"].removesuffix("_v*"): {}}},
    }
    return es


@pytest.fixture
def es_locked() -> MagicMock:
    es = _make_es()
    es.indices.create.side_effect = BadRequestError("resource_already_exists_exception", MagicMock(), None)
    return es


def _dark_creates(es: MagicMock) -> list[dict]:
    return [kw for _, kw in es.indices.create.call_args_list if "aliases" in kw]


def test_requires_exactly_one_scope() -> None:
    with pytest.raises(CommandError, match="exactly one scope"):
        call_command(CMD)


def test_disabled_elasticsearch_aborts(program: Program) -> None:
    with pytest.raises(CommandError, match="IS_ELASTICSEARCH_ENABLED"):
        call_command(CMD, program=str(program.id), stdout=StringIO())


@override_config(IS_ELASTICSEARCH_ENABLED=True)
def test_reindex_creates_dark_pair_without_alias(
    program: Program, index_names: list[str], es_aliased: MagicMock
) -> None:
    with patch(GET_CONN, return_value=es_aliased), patch(DELTA_CALL), patch(POPULATE):
        call_command(CMD, program=str(program.id), stdout=StringIO())

    created = _dark_creates(es_aliased)
    assert sorted(kw["index"] for kw in created) == sorted(f"{n}_v2" for n in index_names)
    assert all(kw["aliases"] is None for kw in created)


@override_config(IS_ELASTICSEARCH_ENABLED=True)
def test_reindex_populates_the_suffixed_targets(
    program: Program, index_names: list[str], es_aliased: MagicMock
) -> None:
    with patch(GET_CONN, return_value=es_aliased), patch(DELTA_CALL), patch(POPULATE) as populate:
        call_command(CMD, program=str(program.id), stdout=StringIO())

    populated = [call.args[1]._index._name for call in populate.call_args_list]
    assert sorted(populated) == sorted(f"{n}_v2" for n in index_names)


@override_config(IS_ELASTICSEARCH_ENABLED=True)
def test_reindex_delta_passes_pre_and_post_swap(program: Program, es_aliased: MagicMock) -> None:
    with patch(GET_CONN, return_value=es_aliased), patch(DELTA_CALL) as delta, patch(POPULATE):
        call_command(CMD, program=str(program.id), stdout=StringIO())

    assert delta.call_count == 3
    assert delta.call_args_list[0].kwargs["target_suffix"] == "v2"
    assert all("target_suffix" not in c.kwargs for c in delta.call_args_list[1:])
    assert all(c.kwargs["program"] == str(program.id) for c in delta.call_args_list)


@override_config(IS_ELASTICSEARCH_ENABLED=True)
def test_swap_is_one_atomic_call_for_the_pair(program: Program, index_names: list[str], es_aliased: MagicMock) -> None:
    with patch(GET_CONN, return_value=es_aliased), patch(DELTA_CALL), patch(POPULATE):
        call_command(CMD, program=str(program.id), stdout=StringIO())

    assert es_aliased.indices.update_aliases.call_count == 1
    actions = es_aliased.indices.update_aliases.call_args.kwargs["actions"]
    removes = [a["remove"] for a in actions if "remove" in a]
    adds = [a["add"] for a in actions if "add" in a]
    assert sorted(r["index"] for r in removes) == sorted(f"{n}_v1" for n in index_names)
    assert all(r["must_exist"] is True for r in removes)
    assert sorted(a["index"] for a in adds) == sorted(f"{n}_v2" for n in index_names)


@override_config(IS_ELASTICSEARCH_ENABLED=True)
def test_refuses_index_that_is_not_an_alias(program: Program, es_not_aliased: MagicMock) -> None:
    with (
        patch(GET_CONN, return_value=es_not_aliased),
        patch(DELTA_CALL) as delta,
        patch(POPULATE) as populate,
        pytest.raises(CommandError, match="failed"),
    ):
        call_command(CMD, program=str(program.id), stdout=StringIO())

    assert _dark_creates(es_not_aliased) == []
    es_not_aliased.indices.update_aliases.assert_not_called()
    populate.assert_not_called()
    assert delta.call_count == 0


@override_config(IS_ELASTICSEARCH_ENABLED=True)
def test_verify_mismatch_aborts_before_swap_after_one_retry(program: Program, es_count_mismatch: MagicMock) -> None:
    with (
        patch(GET_CONN, return_value=es_count_mismatch),
        patch(DELTA_CALL) as delta,
        patch(POPULATE),
        pytest.raises(CommandError, match="failed"),
    ):
        call_command(CMD, program=str(program.id), stdout=StringIO())

    es_count_mismatch.indices.update_aliases.assert_not_called()
    assert delta.call_count == 2
    assert all(c.kwargs["target_suffix"] == "v2" for c in delta.call_args_list)


@override_config(IS_ELASTICSEARCH_ENABLED=True)
def test_verify_mismatch_recovers_after_extra_delta(program: Program, es_count_recovers: MagicMock) -> None:
    with patch(GET_CONN, return_value=es_count_recovers), patch(DELTA_CALL) as delta, patch(POPULATE):
        call_command(CMD, program=str(program.id), stdout=StringIO())

    assert es_count_recovers.indices.update_aliases.call_count == 1
    assert delta.call_count == 4


@override_config(IS_ELASTICSEARCH_ENABLED=True)
def test_postcondition_failure_skips_post_swap_deltas(program: Program, es_swap_does_not_flip: MagicMock) -> None:
    with (
        patch(GET_CONN, return_value=es_swap_does_not_flip),
        patch(DELTA_CALL) as delta,
        patch(POPULATE),
        pytest.raises(CommandError, match="failed"),
    ):
        call_command(CMD, program=str(program.id), stdout=StringIO())

    assert delta.call_count == 1


@override_config(IS_ELASTICSEARCH_ENABLED=True)
def test_lock_held_by_another_run_refuses(program: Program, es_locked: MagicMock) -> None:
    with patch(GET_CONN, return_value=es_locked), pytest.raises(CommandError, match="lock"):
        call_command(CMD, program=str(program.id), stdout=StringIO())


@override_config(IS_ELASTICSEARCH_ENABLED=True)
def test_lock_released_after_run(program: Program, es_aliased: MagicMock) -> None:
    with patch(GET_CONN, return_value=es_aliased), patch(DELTA_CALL), patch(POPULATE):
        call_command(CMD, program=str(program.id), stdout=StringIO())

    deleted = [kw["index"] for _, kw in es_aliased.options.return_value.indices.delete.call_args_list]
    assert Command.LOCK_INDEX in deleted


@override_config(IS_ELASTICSEARCH_ENABLED=True)
def test_dry_run_touches_nothing(program: Program, es_aliased: MagicMock) -> None:
    out = StringIO()
    with patch(GET_CONN, return_value=es_aliased), patch(DELTA_CALL) as delta, patch(POPULATE) as populate:
        call_command(CMD, program=str(program.id), dry_run=True, stdout=out)

    es_aliased.indices.create.assert_not_called()
    es_aliased.indices.update_aliases.assert_not_called()
    populate.assert_not_called()
    assert delta.call_count == 0
    assert "REINDEX" in out.getvalue()


@override_config(IS_ELASTICSEARCH_ENABLED=True)
def test_dry_run_survives_alias_outside_version_scheme(program: Program, es_aliased: MagicMock) -> None:
    es_aliased.indices.get_alias.side_effect = lambda **kw: {f"{kw['name']}-hand-mangled": {"aliases": {}}}
    out = StringIO()
    with patch(GET_CONN, return_value=es_aliased):
        call_command(CMD, program=str(program.id), dry_run=True, stdout=out)

    assert "SKIP" in out.getvalue()
    assert "outside the _vN scheme" in out.getvalue()


@override_config(IS_ELASTICSEARCH_ENABLED=True)
def test_dry_run_flags_non_aliased_program(program: Program, es_not_aliased: MagicMock) -> None:
    out = StringIO()
    with patch(GET_CONN, return_value=es_not_aliased):
        call_command(CMD, program=str(program.id), dry_run=True, stdout=out)

    assert "es_bootstrap_aliases" in out.getvalue()


@override_config(IS_ELASTICSEARCH_ENABLED=True)
def test_resume_reuses_matching_dark_pair_without_repopulating(
    program: Program, index_names: list[str], es_resumable: MagicMock
) -> None:
    out = StringIO()
    with patch(GET_CONN, return_value=es_resumable), patch(DELTA_CALL) as delta, patch(POPULATE) as populate:
        call_command(CMD, program=str(program.id), stdout=out)

    populate.assert_not_called()
    assert _dark_creates(es_resumable) == []
    es_resumable.indices.delete.assert_not_called()
    assert es_resumable.indices.update_aliases.call_count == 1
    assert delta.call_args_list[0].kwargs["target_suffix"] == "v2"
    assert "resuming into existing dark" in out.getvalue()


@override_config(IS_ELASTICSEARCH_ENABLED=True)
def test_resumed_verify_failure_hints_sweep_wrecks(program: Program, es_resumable: MagicMock) -> None:
    es_resumable.count.return_value = {"count": 5}
    with (
        patch(GET_CONN, return_value=es_resumable),
        patch(DELTA_CALL),
        patch(POPULATE),
        pytest.raises(CommandError, match="sweep-wrecks"),
    ):
        call_command(CMD, program=str(program.id), stdout=StringIO())

    es_resumable.indices.update_aliases.assert_not_called()


@override_config(IS_ELASTICSEARCH_ENABLED=True)
def test_stale_mapping_wreck_is_rebuilt_under_same_number(
    program: Program, index_names: list[str], es_dark_wreck: MagicMock
) -> None:
    with patch(GET_CONN, return_value=es_dark_wreck), patch(DELTA_CALL), patch(POPULATE) as populate:
        call_command(CMD, program=str(program.id), stdout=StringIO())

    deleted = [kw["index"] for _, kw in es_dark_wreck.indices.delete.call_args_list if "index" in kw]
    assert sorted(d for d in deleted if d.endswith("_v2")) == sorted(f"{n}_v2" for n in index_names)
    created = _dark_creates(es_dark_wreck)
    assert sorted(kw["index"] for kw in created) == sorted(f"{n}_v2" for n in index_names)
    assert populate.call_count == 2


@override_config(IS_ELASTICSEARCH_ENABLED=True)
def test_sweep_wrecks_flag_deletes_leftovers_upfront(
    program: Program, index_names: list[str], es_dark_wreck: MagicMock
) -> None:
    with patch(GET_CONN, return_value=es_dark_wreck), patch(DELTA_CALL), patch(POPULATE):
        call_command(CMD, program=str(program.id), sweep_wrecks=True, stdout=StringIO())

    deleted = [kw["index"] for _, kw in es_dark_wreck.indices.delete.call_args_list if "index" in kw]
    assert sorted(d for d in deleted if d.endswith("_v2")) == sorted(f"{n}_v2" for n in index_names)
    created = _dark_creates(es_dark_wreck)
    assert sorted(kw["index"] for kw in created) == sorted(f"{n}_v2" for n in index_names)


@override_config(IS_ELASTICSEARCH_ENABLED=True)
def test_sanity_window_old_version_is_not_swept(
    program: Program, index_names: list[str], es_sanity_window: MagicMock
) -> None:
    with patch(GET_CONN, return_value=es_sanity_window), patch(DELTA_CALL), patch(POPULATE):
        call_command(CMD, program=str(program.id), stdout=StringIO())

    deleted = [kw["index"] for _, kw in es_sanity_window.indices.delete.call_args_list if "index" in kw]
    assert not any(d.endswith("_v1") for d in deleted)
    created = _dark_creates(es_sanity_window)
    assert sorted(kw["index"] for kw in created) == sorted(f"{n}_v3" for n in index_names)


@override_config(IS_ELASTICSEARCH_ENABLED=True)
def test_diverged_versions_advance_in_lockstep(program: Program, es_diverged_versions: MagicMock) -> None:
    out = StringIO()
    with patch(GET_CONN, return_value=es_diverged_versions):
        call_command(CMD, program=str(program.id), dry_run=True, stdout=out)

    assert "-> _v3" in out.getvalue()


@override_config(IS_ELASTICSEARCH_ENABLED=True)
def test_status_reports_alias_and_versions(program: Program, es_aliased: MagicMock) -> None:
    out = StringIO()
    with patch(GET_CONN, return_value=es_aliased):
        call_command(CMD, program=str(program.id), status=True, stdout=out)

    assert "ALIAS ->" in out.getvalue()
    assert "versions=[1]" in out.getvalue()
    es_aliased.indices.create.assert_not_called()


@override_config(IS_ELASTICSEARCH_ENABLED=True)
def test_ambiguous_program_code_is_rejected(programs_same_code: list[Program], es_aliased: MagicMock) -> None:
    with (
        patch(GET_CONN, return_value=es_aliased),
        pytest.raises(CommandError, match="unique per business area"),
    ):
        call_command(CMD, program="SAME", stdout=StringIO())

    es_aliased.indices.update_aliases.assert_not_called()
