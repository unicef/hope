from constance.test import override_config
from django.conf import settings
from elasticsearch import Elasticsearch
import pytest

from extras.test_utils.factories import HouseholdFactory, IndividualFactory, ProgramFactory
from hope.apps.household.documents import IndividualDocument, get_individual_doc
from hope.models import Program

pytestmark = pytest.mark.django_db


class TestMappingIntrospection:
    """Tests 4.1-4.4: verify the document class mapping without needing ES."""

    def test_individual_document_has_unicef_id_keyword_subfield(self):
        mapping = IndividualDocument._doc_type.mapping.to_dict()
        unicef_id_props = mapping["properties"]["unicef_id"]
        assert "fields" in unicef_id_props, "unicef_id should have multi-fields"
        keyword_field = unicef_id_props["fields"]["keyword"]
        assert keyword_field["type"] == "keyword"
        assert keyword_field["normalizer"] == "lowercase_normalizer"

    def test_household_object_has_unicef_id_keyword_subfield(self):
        mapping = IndividualDocument._doc_type.mapping.to_dict()
        hh_props = mapping["properties"]["household"]["properties"]
        unicef_id_props = hh_props["unicef_id"]
        assert "fields" in unicef_id_props, "household.unicef_id should have multi-fields"
        keyword_field = unicef_id_props["fields"]["keyword"]
        assert keyword_field["type"] == "keyword"
        assert keyword_field["normalizer"] == "lowercase_normalizer"

    def test_household_object_has_address_field_with_keyword_subfield(self):
        mapping = IndividualDocument._doc_type.mapping.to_dict()
        hh_props = mapping["properties"]["household"]["properties"]
        assert "address" in hh_props, "household should have an address field"
        address_props = hh_props["address"]
        assert address_props["type"] == "text", "address parent field should be TextField"
        assert "fields" in address_props, "address should have multi-fields"
        keyword_field = address_props["fields"]["keyword"]
        assert keyword_field["type"] == "keyword"
        assert keyword_field["normalizer"] == "lowercase_normalizer"

    def test_lowercase_normalizer_is_registered(self):
        from hope.apps.core.es_analyzers import lowercase_normalizer

        normalizer_dict = lowercase_normalizer.get_definition()
        assert "lowercase" in normalizer_dict.get("filter", [])


@pytest.mark.usefixtures("django_elasticsearch_setup")
@pytest.mark.elasticsearch
@pytest.mark.xdist_group(name="elasticsearch")
class TestMappingIndexing:
    """Tests 4.5-4.6: verify new subfields are populated after indexing.

    Data is created inline (not via fixtures) so that factory post_save signals
    fire inside the @override_config(IS_ELASTICSEARCH_ENABLED=True) context —
    otherwise the program activation signal won't create the ES index and
    individual saves won't sync to ES.
    """

    @override_config(IS_ELASTICSEARCH_ENABLED=True)
    def test_indexed_document_populates_unicef_id_keyword(self, afghanistan):
        program = ProgramFactory(business_area=afghanistan, status=Program.DRAFT)
        program.status = Program.ACTIVE
        program.save()

        individual = IndividualFactory(program=program, full_name="John Smith")
        individual.unicef_id = "IND-0000001"
        individual.save(update_fields=["unicef_id"])

        es = Elasticsearch(settings.ELASTICSEARCH_HOST)
        doc_class = get_individual_doc(str(program.id))
        index_name = doc_class._index._name
        es.indices.refresh(index=index_name)

        result = es.search(
            index=index_name,
            body={"query": {"term": {"unicef_id.keyword": "ind-0000001"}}},
        )
        assert result["hits"]["total"]["value"] == 1
        assert result["hits"]["hits"][0]["_id"] == str(individual.id)

    @override_config(IS_ELASTICSEARCH_ENABLED=True)
    def test_indexed_document_populates_household_address_keyword(self, afghanistan):
        program = ProgramFactory(business_area=afghanistan, status=Program.DRAFT)
        program.status = Program.ACTIVE
        program.save()

        household = HouseholdFactory(program=program, address="Main Street 5, Aleppo")
        individual = IndividualFactory(
            program=program,
            household=household,
            full_name="Alice Aleppan",
        )

        es = Elasticsearch(settings.ELASTICSEARCH_HOST)
        doc_class = get_individual_doc(str(program.id))
        index_name = doc_class._index._name
        es.indices.refresh(index=index_name)

        result = es.search(
            index=index_name,
            body={"query": {"term": {"household.address.keyword": "main street 5, aleppo"}}},
        )
        hit_ids = {hit["_id"] for hit in result["hits"]["hits"]}
        assert str(individual.id) in hit_ids
