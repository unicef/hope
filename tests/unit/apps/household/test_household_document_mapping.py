from constance.test import override_config
from django.conf import settings
from elasticsearch import Elasticsearch
import pytest

from extras.test_utils.factories import HouseholdFactory, IndividualFactory, ProgramFactory
from hope.apps.household.documents import IndividualDocument, get_individual_doc
from hope.models import BusinessArea, Household, Individual, Program

pytestmark = pytest.mark.django_db


@pytest.fixture
def es_enabled(django_elasticsearch_setup):
    with override_config(IS_ELASTICSEARCH_ENABLED=True):
        yield


@pytest.fixture
def es_program(es_enabled, afghanistan: BusinessArea) -> Program:
    program = ProgramFactory(business_area=afghanistan, status=Program.DRAFT)
    program.status = Program.ACTIVE
    program.save()
    return program


@pytest.fixture
def individual_john_smith(es_program: Program) -> Individual:
    individual = IndividualFactory(program=es_program, full_name="John Smith")
    individual.unicef_id = "IND-0000001"
    individual.save(update_fields=["unicef_id"])
    return individual


@pytest.fixture
def individual_with_alternative_phone(es_program: Program) -> Individual:
    return IndividualFactory(
        program=es_program,
        phone_no="+48 123 456 789",
        phone_no_alternative="+48 999 000 111",
    )


@pytest.fixture
def household_with_address(es_program: Program) -> Household:
    return HouseholdFactory(program=es_program, address="Main Street 5, Aleppo")


@pytest.fixture
def individual_in_addressed_household(es_program: Program, household_with_address: Household) -> Individual:
    return IndividualFactory(program=es_program, household=household_with_address, full_name="Alice Aleppan")


def test_individual_document_has_unicef_id_keyword_subfield():
    mapping = IndividualDocument._doc_type.mapping.to_dict()
    unicef_id_props = mapping["properties"]["unicef_id"]
    assert "fields" in unicef_id_props, "unicef_id should have multi-fields"
    keyword_field = unicef_id_props["fields"]["keyword"]
    assert keyword_field["type"] == "keyword"
    assert keyword_field["normalizer"] == "lowercase_normalizer"


def test_household_object_has_unicef_id_keyword_subfield():
    mapping = IndividualDocument._doc_type.mapping.to_dict()
    hh_props = mapping["properties"]["household"]["properties"]
    unicef_id_props = hh_props["unicef_id"]
    assert "fields" in unicef_id_props, "household.unicef_id should have multi-fields"
    keyword_field = unicef_id_props["fields"]["keyword"]
    assert keyword_field["type"] == "keyword"
    assert keyword_field["normalizer"] == "lowercase_normalizer"


def test_household_object_has_address_keyword_field():
    mapping = IndividualDocument._doc_type.mapping.to_dict()
    hh_props = mapping["properties"]["household"]["properties"]
    assert "address" in hh_props, "household should have an address field"
    address_props = hh_props["address"]
    assert address_props["type"] == "keyword"
    assert address_props["normalizer"] == "lowercase_normalizer"


def test_lowercase_normalizer_is_registered():
    from hope.apps.core.es_analyzers import lowercase_normalizer

    normalizer_dict = lowercase_normalizer.get_definition()
    assert "lowercase" in normalizer_dict.get("filter", [])


@pytest.mark.elasticsearch
@pytest.mark.xdist_group(name="elasticsearch")
def test_indexed_document_populates_unicef_id_keyword(es_program, individual_john_smith):
    es = Elasticsearch(settings.ELASTICSEARCH_HOST)
    index_name = get_individual_doc(str(es_program.id))._index._name
    es.indices.refresh(index=index_name)

    result = es.search(
        index=index_name,
        body={"query": {"term": {"unicef_id.keyword": "ind-0000001"}}},
    )
    assert result["hits"]["total"]["value"] == 1
    assert result["hits"]["hits"][0]["_id"] == str(individual_john_smith.id)


@pytest.mark.elasticsearch
@pytest.mark.xdist_group(name="elasticsearch")
def test_indexed_document_populates_household_address(es_program, individual_in_addressed_household):
    es = Elasticsearch(settings.ELASTICSEARCH_HOST)
    index_name = get_individual_doc(str(es_program.id))._index._name
    es.indices.refresh(index=index_name)

    result = es.search(
        index=index_name,
        body={"query": {"term": {"household.address": "main street 5, aleppo"}}},
    )
    hit_ids = {hit["_id"] for hit in result["hits"]["hits"]}
    assert str(individual_in_addressed_household.id) in hit_ids


@pytest.mark.elasticsearch
@pytest.mark.xdist_group(name="elasticsearch")
def test_indexed_document_populates_phone_no_alternative_text_from_alternative_number(
    es_program, individual_with_alternative_phone
):
    es = Elasticsearch(settings.ELASTICSEARCH_HOST)
    index_name = get_individual_doc(str(es_program.id))._index._name
    es.indices.refresh(index=index_name)

    source = es.get(index=index_name, id=str(individual_with_alternative_phone.id))["_source"]
    assert source["phone_no_alternative_text"] == "+48999000111"
