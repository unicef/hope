import threading

from constance.test import override_config
from django.conf import settings
from elasticsearch import BadRequestError, Elasticsearch
import pytest

from extras.test_utils.factories import HouseholdFactory, IndividualFactory, ProgramFactory
from hope.apps.household.documents import get_household_doc, get_individual_doc
from hope.apps.household.services.index_management import delete_es_index
from hope.models import Program
from hope.one_time_scripts.migrate_to_per_program_indexes import _delete_old_indexes, migrate_to_per_program_indexes

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.elasticsearch,
    pytest.mark.xdist_group(name="elasticsearch"),
    pytest.mark.usefixtures("django_elasticsearch_setup"),
]

REBUILD = "hope.one_time_scripts.migrate_to_per_program_indexes.rebuild_program_indexes"
DELETE_OLD = "hope.one_time_scripts.migrate_to_per_program_indexes._delete_old_indexes"

MOCK_OLD_INDEXES = ["old_individuals_afghanistan", "old_households"]


def _mock_old_indexes_full():
    return [f"{settings.ELASTICSEARCH_INDEX_PREFIX}{name}" for name in MOCK_OLD_INDEXES]


def _es():
    return Elasticsearch(settings.ELASTICSEARCH_HOST)


def _create_index(name):
    es = _es()
    if not es.indices.exists(index=name):
        es.indices.create(index=name)


def _create_alias_with_concrete_indexes(alias_name: str, concrete_names: list[str]) -> None:
    """Create multiple concrete indexes all pointing to the same alias.

    Simulates what happens on eph envs with large data where django-elasticsearch-dsl
    creates alias-backed indexes (e.g. individuals_afghanistan -> individuals_afghanistan-000001).
    The last concrete index is marked as is_write_index=True, as ES requires exactly
    one write index when multiple concrete indexes share an alias.
    """
    es = _es()
    for i, concrete in enumerate(concrete_names):
        is_write = i == len(concrete_names) - 1
        if not es.indices.exists(index=concrete):
            es.indices.create(
                index=concrete,
                body={"aliases": {alias_name: {"is_write_index": is_write}}},
            )


def _index_exists(name):
    return _es().indices.exists(index=name)


@override_config(IS_ELASTICSEARCH_ENABLED=True)
def test_delete_old_indexes_deletes_existing(mocker):
    keep_indexes = ["test_individuals_program_abc123", "test_households_program_abc123", "test_grievance_tickets"]
    for name in _mock_old_indexes_full():
        _create_index(name)
    for name in keep_indexes:
        _create_index(name)
    assert all(_index_exists(n) for n in _mock_old_indexes_full())
    assert all(_index_exists(n) for n in keep_indexes)

    mocker.patch("hope.one_time_scripts.migrate_to_per_program_indexes.OLD_INDEXES", MOCK_OLD_INDEXES)

    _delete_old_indexes()

    assert all(not _index_exists(n) for n in _mock_old_indexes_full())
    assert all(_index_exists(n) for n in keep_indexes)


@override_config(IS_ELASTICSEARCH_ENABLED=True)
def test_migrate_calls_rebuild_for_each_active_program(mocker):
    mocker.patch(DELETE_OLD)
    rebuild_mock = mocker.patch(REBUILD, return_value=(True, "ok"))

    active1 = ProgramFactory(status=Program.ACTIVE)
    active2 = ProgramFactory(status=Program.ACTIVE)
    ProgramFactory(status=Program.DRAFT)
    ProgramFactory(status=Program.FINISHED)

    migrate_to_per_program_indexes()

    assert rebuild_mock.call_count == 2
    called_ids = {c.args[0] for c in rebuild_mock.call_args_list}
    assert str(active1.id) in called_ids
    assert str(active2.id) in called_ids


@override_config(IS_ELASTICSEARCH_ENABLED=True)
def test_migrate_continues_on_failure(mocker):
    mocker.patch(DELETE_OLD)
    rebuild_mock = mocker.patch(REBUILD, side_effect=[(False, "error"), (True, "ok")])

    ProgramFactory(status=Program.ACTIVE)
    ProgramFactory(status=Program.ACTIVE)

    migrate_to_per_program_indexes()

    assert rebuild_mock.call_count == 2


@override_config(IS_ELASTICSEARCH_ENABLED=True)
def test_migrate_no_active_programs(mocker):
    mocker.patch(DELETE_OLD)
    rebuild_mock = mocker.patch(REBUILD)

    ProgramFactory(status=Program.DRAFT)

    migrate_to_per_program_indexes()

    rebuild_mock.assert_not_called()


@pytest.mark.django_db(transaction=True)
@override_config(IS_ELASTICSEARCH_ENABLED=True)
def test_migrate_creates_new_indexes_and_deletes_old(mocker):
    for name in _mock_old_indexes_full():
        _create_index(name)

    mocker.patch(
        "hope.one_time_scripts.migrate_to_per_program_indexes.OLD_INDEXES",
        MOCK_OLD_INDEXES,
    )

    with override_config(IS_ELASTICSEARCH_ENABLED=False):
        program = ProgramFactory(status=Program.ACTIVE)
        individual = IndividualFactory(program=program)
        household = HouseholdFactory(program=program)

    ind_index = get_individual_doc(str(program.id))._index._name
    hh_index = get_household_doc(str(program.id))._index._name

    assert all(_index_exists(n) for n in _mock_old_indexes_full())
    assert not _index_exists(ind_index)
    assert not _index_exists(hh_index)

    migrate_to_per_program_indexes()

    assert all(not _index_exists(n) for n in _mock_old_indexes_full())
    assert _index_exists(ind_index)
    assert _index_exists(hh_index)
    es = _es()
    es.indices.refresh(index=ind_index)
    es.indices.refresh(index=hh_index)
    assert es.count(index=ind_index)["count"] == 2  # created ind + hoh
    assert es.count(index=hh_index)["count"] == 1
    assert bool(es.exists(index=ind_index, id=str(individual.id)))
    assert bool(es.exists(index=hh_index, id=str(household.id)))


@pytest.mark.django_db(transaction=True)
@override_config(IS_ELASTICSEARCH_ENABLED=True)
def test_migrate_parallel_multiple_programs_check_threading(mocker):
    mocker.patch(DELETE_OLD)
    used_threads = set()

    import hope.apps.household.services.index_management as im

    original_rebuild = im.rebuild_program_indexes

    def tracking_rebuild(program_id, batch_size=1000):
        used_threads.add(threading.current_thread().name)
        return original_rebuild(program_id, batch_size=batch_size)

    mocker.patch(REBUILD, side_effect=tracking_rebuild)

    es = _es()

    with override_config(IS_ELASTICSEARCH_ENABLED=False):
        programs = [ProgramFactory(status=Program.ACTIVE) for _ in range(5)]
        for program in programs:
            IndividualFactory(program=program)
            HouseholdFactory(program=program)

    for program in programs:
        ind_index = get_individual_doc(str(program.id))._index._name
        hh_index = get_household_doc(str(program.id))._index._name
        assert not _index_exists(ind_index)
        assert not _index_exists(hh_index)

    migrate_to_per_program_indexes(max_workers=2)

    assert len(used_threads) == 2

    for program in programs:
        ind_index = get_individual_doc(str(program.id))._index._name
        hh_index = get_household_doc(str(program.id))._index._name
        es.indices.refresh(index=ind_index)
        es.indices.refresh(index=hh_index)
        assert es.count(index=ind_index)["count"] == 2
        assert es.count(index=hh_index)["count"] == 1


@override_config(IS_ELASTICSEARCH_ENABLED=True)
def test_deleting_alias():
    prefix = settings.ELASTICSEARCH_INDEX_PREFIX
    alias = f"{prefix}old_individuals_afghanistan"
    concrete_1 = f"{alias}-000001"
    concrete_2 = f"{alias}-000002"

    _create_alias_with_concrete_indexes(alias, [concrete_1, concrete_2])

    assert _index_exists(alias)

    es = _es()
    with pytest.raises(BadRequestError) as exc_info:
        es.indices.delete(index=alias)

    assert "illegal_argument_exception" in str(exc_info.value)
    assert "matches an alias" in str(exc_info.value)

    assert _index_exists(alias)
    assert _index_exists(concrete_1)
    assert _index_exists(concrete_2)

    delete_es_index(es, alias)

    assert not _index_exists(alias)
    assert not _index_exists(concrete_1)
    assert not _index_exists(concrete_2)
