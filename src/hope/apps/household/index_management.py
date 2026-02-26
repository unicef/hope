"""Elasticsearch Index Management for Per-Program Indexes.

Simple utilities for managing per-program Elasticsearch indexes.
"""

import logging

from django.conf import settings
from elasticsearch import Elasticsearch

from hope.apps.household.documents import get_household_doc, get_individual_doc
from hope.apps.utils.elasticsearch_utils import populate_index

logger = logging.getLogger(__name__)


def create_program_indexes(program_id: str) -> tuple[bool, str]:
    """Create Elasticsearch indexes for a program."""
    try:
        individual_doc_class = get_individual_doc(program_id)
        household_doc_class = get_household_doc(program_id)

        es = Elasticsearch(settings.ELASTICSEARCH_HOST)

        if not es.indices.exists(index=individual_doc_class._index._name):
            individual_doc_class._index.create()

        if not es.indices.exists(index=household_doc_class._index._name):
            household_doc_class._index.create()

        return True, ""
    except Exception as e:  # noqa
        logger.error(f"Failed to create indexes for program {program_id}: {e}")
        return False, str(e)


def delete_program_indexes(program_id: str) -> tuple[bool, str]:
    """Delete Elasticsearch indexes for a program."""
    try:
        individual_doc_class = get_individual_doc(program_id)
        household_doc_class = get_household_doc(program_id)

        es = Elasticsearch(settings.ELASTICSEARCH_HOST)

        if es.indices.exists(index=individual_doc_class._index._name):
            es.indices.delete(index=individual_doc_class._index._name)

        if es.indices.exists(index=household_doc_class._index._name):
            es.indices.delete(index=household_doc_class._index._name)

        return True, ""
    except Exception as e:  # noqa
        logger.error(f"Failed to delete indexes for program {program_id}: {e}")
        return False, str(e)


def populate_program_indexes(program_id: str, batch_size: int = 2000) -> tuple[bool, str]:
    """Populate Elasticsearch indexes for a program."""
    try:
        individual_doc_class = get_individual_doc(program_id)
        household_doc_class = get_household_doc(program_id)

        individuals = individual_doc_class().get_queryset()
        households = household_doc_class().get_queryset()

        populate_index(individuals, individual_doc_class, chunk_size=batch_size)
        populate_index(households, household_doc_class, chunk_size=batch_size)

        return True, ""
    except Exception as e:  # noqa
        logger.error(f"Failed to populate indexes for program {program_id}: {e}")
        return False, str(e)


def rebuild_program_indexes(program_id: str, batch_size: int = 2000) -> tuple[bool, str]:
    """Rebuild Elasticsearch indexes for a program (delete, create, populate)."""
    success, msg = delete_program_indexes(program_id)
    if not success:
        return False, f"Delete failed: {msg}"

    success, msg = create_program_indexes(program_id)
    if not success:
        return False, f"Create failed: {msg}"

    success, msg = populate_program_indexes(program_id, batch_size)
    if not success:
        return False, f"Populate failed: {msg}"

    return True, f"Rebuilt indexes for program {program_id}"


def check_program_indexes(program_id: str) -> tuple[bool, str]:
    """Return (True, msg) if both indexes exist and counts match, (False, msg) otherwise."""
    try:
        individual_doc_class = get_individual_doc(program_id)
        household_doc_class = get_household_doc(program_id)
        es = Elasticsearch(settings.ELASTICSEARCH_HOST)
        for doc in (individual_doc_class, household_doc_class):
            index_name = doc._index._name
            if not es.indices.exists(index=index_name):
                return False, f"Index {index_name} does not exist."
            db_count = doc().get_queryset().count()
            es_count = es.count(index=index_name)["count"]
            if es_count != db_count:
                return False, f"Number of records does not mach: index {index_name}."
        return True, "Indexes exist and counts match."
    except Exception as e:  # noqa
        return False, str(e)
