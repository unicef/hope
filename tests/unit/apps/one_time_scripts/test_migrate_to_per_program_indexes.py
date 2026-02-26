from django.conf import settings
from elasticsearch import Elasticsearch
import pytest

from extras.test_utils.factories import HouseholdFactory, IndividualFactory, ProgramFactory
from hope.apps.household.documents import get_household_doc, get_individual_doc
from hope.models import Program
from hope.one_time_scripts.migrate_to_per_program_indexes import _delete_old_indexes, migrate_to_per_program_indexes

pytestmark = pytest.mark.django_db

REBUILD = "hope.one_time_scripts.migrate_to_per_program_indexes.rebuild_program_indexes"
DELETE_OLD = "hope.one_time_scripts.migrate_to_per_program_indexes._delete_old_indexes"

MOCK_OLD_INDEXES = ["old_individuals_afghanistan", "old_households"]
MOCK_OLD_INDEXES_FULL = [f"{settings.ELASTICSEARCH_INDEX_PREFIX}{name}" for name in MOCK_OLD_INDEXES]


def _es():
    return Elasticsearch(settings.ELASTICSEARCH_HOST)


def _create_index(name):
    es = _es()
    if not es.indices.exists(index=name):
        es.indices.create(index=name)


def _index_exists(name):
    return _es().indices.exists(index=name)


@pytest.mark.usefixtures("django_elasticsearch_setup")
def test_delete_old_indexes_deletes_existing(mocker):
    keep_indexes = ["test_individuals_program_abc123", "test_households_program_abc123", "test_grievance_tickets"]
    for name in MOCK_OLD_INDEXES_FULL:
        _create_index(name)
    for name in keep_indexes:
        _create_index(name)
    assert all(_index_exists(n) for n in MOCK_OLD_INDEXES_FULL)
    assert all(_index_exists(n) for n in keep_indexes)

    mocker.patch("hope.one_time_scripts.migrate_to_per_program_indexes.OLD_INDEXES", MOCK_OLD_INDEXES)

    _delete_old_indexes()

    assert all(not _index_exists(n) for n in MOCK_OLD_INDEXES_FULL)
    assert all(_index_exists(n) for n in keep_indexes)


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


def test_migrate_continues_on_failure(mocker):
    mocker.patch(DELETE_OLD)
    rebuild_mock = mocker.patch(REBUILD, side_effect=[(False, "error"), (True, "ok")])

    ProgramFactory(status=Program.ACTIVE)
    ProgramFactory(status=Program.ACTIVE)

    migrate_to_per_program_indexes()

    assert rebuild_mock.call_count == 2


def test_migrate_no_active_programs(mocker):
    mocker.patch(DELETE_OLD)
    rebuild_mock = mocker.patch(REBUILD)

    ProgramFactory(status=Program.DRAFT)

    migrate_to_per_program_indexes()

    rebuild_mock.assert_not_called()


@pytest.mark.usefixtures("django_elasticsearch_setup")
@pytest.mark.elasticsearch
def test_migrate_creates_new_indexes_and_deletes_old(mocker):
    for name in MOCK_OLD_INDEXES_FULL:
        _create_index(name)

    mocker.patch(
        "hope.one_time_scripts.migrate_to_per_program_indexes.OLD_INDEXES",
        MOCK_OLD_INDEXES,
    )

    program = ProgramFactory(status=Program.ACTIVE)
    individual = IndividualFactory(program=program)
    household = HouseholdFactory(program=program)

    ind_index = get_individual_doc(str(program.id))._index._name
    hh_index = get_household_doc(str(program.id))._index._name

    assert all(_index_exists(n) for n in MOCK_OLD_INDEXES_FULL)
    assert not _index_exists(ind_index)
    assert not _index_exists(hh_index)

    migrate_to_per_program_indexes()

    assert all(not _index_exists(n) for n in MOCK_OLD_INDEXES_FULL)
    assert _index_exists(ind_index)
    assert _index_exists(hh_index)
    es = _es()
    es.indices.refresh(index=ind_index)
    es.indices.refresh(index=hh_index)
    assert es.count(index=ind_index)["count"] == 2  # created ind + hoh
    assert es.count(index=hh_index)["count"] == 1
    assert bool(es.exists(index=ind_index, id=str(individual.id)))
    assert bool(es.exists(index=hh_index, id=str(household.id)))
