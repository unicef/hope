"""Live-Elasticsearch tests for the blue-green bootstrap and reindex flows.

The mocked command tests assert the SEQUENCE of ES calls; a MagicMock happily accepts a
malformed clone or aliases action, so the parts that depend on the real API contract get one
end-to-end run each here: cloning under a write block, the atomic ``_aliases`` calls
(``remove_index`` + ``add`` in bootstrap, ``must_exist`` remove + add in the swap), and the
``_meta.hope_mapping_hash`` stamp surviving ``indices.create`` and coming back through
``get_mapping``.
"""

from io import StringIO
from typing import Any

from constance.test import override_config
from django.conf import settings
from django.core.management import call_command
from elasticsearch import Elasticsearch
import pytest

from extras.test_utils.factories import BusinessAreaFactory, IndividualFactory, ProgramFactory
from hope.apps.household.documents import get_household_doc, get_individual_doc
from hope.apps.household.services.index_management import mapping_content_hash
from hope.models import BusinessArea, Individual, Program

pytestmark = [
    pytest.mark.elasticsearch,
    pytest.mark.xdist_group(name="elasticsearch"),
    pytest.mark.usefixtures("django_elasticsearch_setup"),
]


@pytest.fixture
def program_with_individual() -> dict:
    with override_config(IS_ELASTICSEARCH_ENABLED=False):
        ba: BusinessArea = BusinessAreaFactory()
        program: Program = ProgramFactory(business_area=ba, status=Program.ACTIVE)
        individual: Individual = IndividualFactory(program=program, business_area=ba)
    return {"program": program, "individual": individual}


@pytest.mark.django_db
@override_config(IS_ELASTICSEARCH_ENABLED=True)
def test_bootstrap_clones_write_blocked_bare_index_into_the_alias(program_with_individual: dict) -> None:
    program: Program = program_with_individual["program"]
    ind_doc = get_individual_doc(str(program.id))
    ind_name = ind_doc._index._name
    hh_name = get_household_doc(str(program.id))._index._name
    es = Elasticsearch(settings.ELASTICSEARCH_HOST)
    # pre-blue-green state: the doc name is a BARE physical index holding data
    es.indices.create(index=ind_name, settings={"number_of_replicas": 0})
    es.indices.create(index=hh_name, settings={"number_of_replicas": 0})
    ind_doc().update([program_with_individual["individual"]])
    es.indices.refresh(index=ind_name)

    call_command("es_bootstrap_aliases", program=str(program.id), skip_delta=True, stdout=StringIO())

    # the name IS an alias now: proof the atomic remove_index + add call went through
    # (ES refuses an alias while an index of the same name exists)
    assert es.indices.exists_alias(name=ind_name)
    assert list(es.indices.get_alias(name=ind_name)) == [f"{ind_name}_v1"]
    es.indices.refresh(index=ind_name)
    assert es.count(index=ind_name)["count"] == 1  # the doc survived the write-blocked clone
    v1_settings = es.indices.get_settings(index=f"{ind_name}_v1")[f"{ind_name}_v1"]["settings"]["index"]
    assert v1_settings.get("blocks", {}).get("write") != "true"  # the clone was opened before takeover


@pytest.mark.django_db
@override_config(IS_ELASTICSEARCH_ENABLED=True)
def test_reindex_swaps_the_alias_and_stamps_the_mapping(
    program_with_individual: dict, create_program_es_index: Any
) -> None:
    program: Program = program_with_individual["program"]
    create_program_es_index(program)  # alias -> _v1, mapping from code
    ind_name = get_individual_doc(str(program.id))._index._name
    es = Elasticsearch(settings.ELASTICSEARCH_HOST)

    # force: _v1 was just created from the current code mapping, so its stamp matches and
    # the fleet-resume skip would (correctly) declare the program up-to-date
    call_command("es_reindex", program=str(program.id), force=True, stdout=StringIO())

    # the 4-action must_exist remove + add swap moved the alias to the fresh _v2 pair
    assert list(es.indices.get_alias(name=ind_name)) == [f"{ind_name}_v2"]
    es.indices.refresh(index=ind_name)
    assert es.count(index=ind_name)["count"] == 1
    assert es.indices.exists(index=f"{ind_name}_v1")  # old version kept unaliased for rollback
    # the _meta stamp survived indices.create and round-trips through get_mapping still
    # matching the CODE mapping's hash - the exact comparison the fleet-resume skip makes
    # (hashing the ES-returned mapping would differ: ES normalizes what it stores)
    stored = es.indices.get_mapping(index=f"{ind_name}_v2")[f"{ind_name}_v2"]["mappings"]["_meta"]["hope_mapping_hash"]
    assert stored == mapping_content_hash(get_individual_doc(str(program.id))._index.to_dict().get("mappings"))
