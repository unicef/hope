from django.conf import settings
from django.test import override_settings
from elasticsearch import Elasticsearch
import pytest

from extras.test_utils.factories import HouseholdFactory, IndividualFactory, ProgramFactory
from hope.apps.household.documents import get_household_doc, get_individual_doc
from hope.models import IDP, REFUGEE, Program

pytestmark = [pytest.mark.usefixtures("django_elasticsearch_setup", "enable_es_autosync"), pytest.mark.elasticsearch]


@pytest.fixture
def enable_es_autosync():
    with override_settings(ELASTICSEARCH_DSL_AUTOSYNC=True):
        yield


def _es_count(index_name: str) -> int:
    es = Elasticsearch(settings.ELASTICSEARCH_HOST)
    if not es.indices.exists(index=index_name):
        return -1
    es.indices.refresh(index=index_name)
    return es.count(index=index_name)["count"]


def _index_exists(index_name: str) -> bool:
    return Elasticsearch(settings.ELASTICSEARCH_HOST).indices.exists(index=index_name)


def _ind_index(program):
    return get_individual_doc(str(program.id))._index._name


def _hh_index(program):
    return get_household_doc(str(program.id))._index._name


def _create_and_activate_program():
    program = ProgramFactory(status=Program.DRAFT)
    program.status = Program.ACTIVE
    program.save()
    return program


def test_program_created_as_draft_does_not_create_indexes():
    program = ProgramFactory(status=Program.DRAFT)
    assert not _index_exists(_ind_index(program))
    assert not _index_exists(_hh_index(program))


def test_program_status_change_to_active_creates_indexes():
    program = ProgramFactory(status=Program.DRAFT)
    assert not _index_exists(_ind_index(program))
    assert not _index_exists(_hh_index(program))
    program.status = Program.ACTIVE
    program.save()
    assert _index_exists(_ind_index(program))
    assert _index_exists(_hh_index(program))


def test_program_status_no_change_keeps_indexes():
    program = _create_and_activate_program()
    ind_index = _ind_index(program)
    assert _index_exists(ind_index)
    program.name = "Updated Name"
    program.save()
    assert _index_exists(ind_index)


def test_sync_individual_new_ind():
    program = _create_and_activate_program()
    IndividualFactory(program=program)
    index_name = _ind_index(program)
    assert _es_count(index_name) == 1
    IndividualFactory(program=program)
    assert _es_count(index_name) == 2


def test_sync_individual_soft_delete():
    program = _create_and_activate_program()
    index_name = _ind_index(program)
    individual = IndividualFactory(program=program)
    assert _es_count(index_name) == 1
    individual.delete()
    assert _es_count(index_name) == 0


def test_sync_individual_soft_delete_twice_does_not_error():
    program = _create_and_activate_program()
    index_name = _ind_index(program)
    individual = IndividualFactory(program=program)
    individual.delete()
    assert _es_count(index_name) == 0
    individual.save()
    assert _es_count(index_name) == 0


def test_sync_individual_hard_delete():
    program = _create_and_activate_program()
    index_name = _ind_index(program)
    individual = IndividualFactory(program=program)
    assert _es_count(index_name) == 1
    individual.delete(soft=False)
    assert _es_count(index_name) == 0


def test_individual_update_reflects_in_document():
    program = _create_and_activate_program()
    index_name = _ind_index(program)
    individual = IndividualFactory(program=program, given_name="OldName")
    es = Elasticsearch(settings.ELASTICSEARCH_HOST)
    es.indices.refresh(index=index_name)
    doc = es.get(index=index_name, id=str(individual.id))
    assert doc["_source"]["given_name"] == "OldName"

    individual.given_name = "NewName"
    individual.save()
    es.indices.refresh(index=index_name)
    doc = es.get(index=index_name, id=str(individual.id))
    assert doc["_source"]["given_name"] == "NewName"


def test_sync_individual_skipped_when_program_not_active():
    program = ProgramFactory(status=Program.DRAFT)
    ind = IndividualFactory(program=program)
    assert not _index_exists(_ind_index(program))
    ind.first_name = "Test"
    ind.save()
    assert not _index_exists(_ind_index(program))


def test_sync_household_new_hh(create_program_es_index):
    program = _create_and_activate_program()
    HouseholdFactory(program=program)
    index_name = _hh_index(program)
    assert _es_count(index_name) == 1
    HouseholdFactory(program=program)
    assert _es_count(index_name) == 2


def test_sync_household_soft_delete():
    program = _create_and_activate_program()
    index_name = _hh_index(program)
    household = HouseholdFactory(program=program)
    assert _es_count(index_name) == 1
    household.delete()
    assert _es_count(index_name) == 0


def test_sync_household_soft_delete_twice_does_not_error():
    program = _create_and_activate_program()
    index_name = _hh_index(program)
    household = HouseholdFactory(program=program)
    household.delete()
    assert _es_count(index_name) == 0
    household.save()
    assert _es_count(index_name) == 0


def test_sync_household_hard_delete():
    program = _create_and_activate_program()
    index_name = _hh_index(program)
    household = HouseholdFactory(program=program)
    assert _es_count(index_name) == 1
    household.delete(soft=False)
    assert _es_count(index_name) == 0


def test_household_update_reflects_in_document():
    program = _create_and_activate_program()
    index_name = _hh_index(program)
    household = HouseholdFactory(program=program, residence_status=REFUGEE)
    es = Elasticsearch(settings.ELASTICSEARCH_HOST)
    es.indices.refresh(index=index_name)
    doc = es.get(index=index_name, id=str(household.id))
    assert doc["_source"]["residence_status"] == REFUGEE

    household.residence_status = IDP
    household.save()
    es.indices.refresh(index=index_name)
    doc = es.get(index=index_name, id=str(household.id))
    assert doc["_source"]["residence_status"] == IDP


def test_sync_household_skipped_when_program_not_active():
    program = ProgramFactory(status=Program.DRAFT)
    hh = HouseholdFactory(program=program)
    assert not _index_exists(_hh_index(program))
    hh.residence_status = REFUGEE
    hh.save()
    assert not _index_exists(_ind_index(program))
