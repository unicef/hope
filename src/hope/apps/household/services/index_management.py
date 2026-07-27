"""Elasticsearch Index Management for Per-Program Indexes.

Simple utilities for managing per-program Elasticsearch indexes.
"""

import logging

from constance import config
from elasticsearch import Elasticsearch
from elasticsearch.dsl import connections

from hope.apps.household.documents import get_household_doc, get_individual_doc
from hope.apps.utils.elasticsearch_utils import populate_index

logger = logging.getLogger(__name__)


def _resolve_to_concrete_indexes(es: Elasticsearch, index_name: str) -> list[str]:
    alias_info = es.indices.get_alias(index=index_name, ignore_unavailable=True)
    return list(alias_info.keys()) or [index_name]


def delete_es_index(es: Elasticsearch, index_name: str) -> None:
    if not es.indices.exists(index=index_name):
        return
    for concrete in _resolve_to_concrete_indexes(es, index_name):
        es.options(ignore_status=[400, 404]).indices.delete(index=concrete)


def create_versioned_index(es: Elasticsearch, doc_class: type) -> None:
    """Create ``<name>_v1`` with the alias attached in the same call.

    Blue-green convention: the app addresses the suffix-less name, which is an ALIAS onto the
    physical ``_vN``. Creating both in one call means the index is born on the alias scheme —
    there is never a bare physical index squatting on the logical name.
    """
    index = doc_class._index
    body = index.to_dict()
    es.indices.create(
        index=f"{index._name}_v1",
        settings=body.get("settings"),
        mappings=body.get("mappings"),
        aliases={index._name: {}},
    )


def create_program_indexes(program_id: str, using: str = "default") -> tuple[bool, str]:
    """Create Elasticsearch indexes for a program (physical ``_v1`` + suffix-less alias)."""
    try:
        individual_doc_class = get_individual_doc(program_id)
        household_doc_class = get_household_doc(program_id)

        es: Elasticsearch = connections.get_connection(using)

        # exists() also matches aliases, so bootstrapped and newly-created programs both skip
        if not es.indices.exists(index=individual_doc_class._index._name):
            create_versioned_index(es, individual_doc_class)

        if not es.indices.exists(index=household_doc_class._index._name):
            create_versioned_index(es, household_doc_class)

        return True, ""
    except Exception as e:  # pragma: no cover  # noqa
        logger.error(f"Failed to create indexes for program {program_id}: {e}")
        return False, str(e)


def delete_program_indexes(program_id: str, using: str = "default") -> tuple[bool, str]:
    """Delete Elasticsearch indexes for a program."""
    try:
        individual_doc_class = get_individual_doc(program_id)
        household_doc_class = get_household_doc(program_id)

        es: Elasticsearch = connections.get_connection(using)
        delete_es_index(es, individual_doc_class._index._name)
        delete_es_index(es, household_doc_class._index._name)

        return True, ""
    except Exception as e:  # pragma: no cover  # noqa
        logger.error(f"Failed to delete indexes for program {program_id}: {e}")
        return False, str(e)


def populate_program_indexes(
    program_id: str,
    batch_size: int = 2000,
    parallel: bool = False,
    thread_count: int = 4,
    using: str = "default",
) -> tuple[bool, str]:
    """Populate Elasticsearch indexes for a program."""
    try:
        individual_doc_class = get_individual_doc(program_id)
        household_doc_class = get_household_doc(program_id)

        individuals = individual_doc_class().get_queryset()
        households = household_doc_class().get_queryset()

        populate_index(individuals, individual_doc_class, parallel=parallel, chunk_size=batch_size)
        populate_index(households, household_doc_class, parallel=parallel, chunk_size=batch_size)

        return True, ""
    except Exception as e:  # pragma: no cover  # noqa
        logger.error(f"Failed to populate indexes for program {program_id}: {e}")
        return False, str(e)


def ensure_program_indexes(
    program_id: str,
    batch_size: int = 2000,
    parallel: bool = False,
    thread_count: int = 4,
    using: str = "default",
) -> tuple[bool, str]:
    """Create missing indexes (``_v1`` + alias) and upsert-populate. Never deletes anything.

    The safe choice for every AUTOMATIC path (signals, bulk console actions): an existing live
    index keeps serving while populate upserts into it. Stale-document cleanup is the job of an
    explicit blue-green reindex, not of this function.
    """
    success, msg = create_program_indexes(program_id, using=using)
    if not success:  # pragma: no cover
        return False, f"Create failed: {msg}"

    success, msg = populate_program_indexes(
        program_id, batch_size, parallel=parallel, thread_count=thread_count, using=using
    )
    if not success:  # pragma: no cover
        return False, f"Populate failed: {msg}"

    return True, f"Ensured indexes for program {program_id}"


def rebuild_program_indexes(
    program_id: str,
    batch_size: int = 2000,
    parallel: bool = False,
    thread_count: int = 4,
    using: str = "default",
) -> tuple[bool, str]:
    """Rebuild Elasticsearch indexes for a program (delete, create, populate).

    DESTRUCTIVE: deletes the live index first, so search/dedup see an empty index until populate
    finishes. Reserved for the explicit admin "Rebuild Index" button as a recovery tool — automatic
    paths must use ``ensure_program_indexes`` instead. The end state is alias-consistent (the
    rebuilt index is ``_v1`` behind the suffix-less alias).
    """
    success, msg = delete_program_indexes(program_id, using=using)
    if not success:  # pragma: no cover
        return False, f"Delete failed: {msg}"

    success, msg = create_program_indexes(program_id, using=using)
    if not success:  # pragma: no cover
        return False, f"Create failed: {msg}"

    success, msg = populate_program_indexes(
        program_id, batch_size, parallel=parallel, thread_count=thread_count, using=using
    )
    if not success:  # pragma: no cover
        return False, f"Populate failed: {msg}"

    return True, f"Rebuilt indexes for program {program_id}"


def check_program_indexes(program_id: str, using: str = "default") -> tuple[bool, str]:
    """Return (True, msg) if both indexes exist and counts match, (False, msg) otherwise."""
    if not config.IS_ELASTICSEARCH_ENABLED:  # pragma: no cover
        return False, "Elasticsearch is disabled."
    try:
        individual_doc_class = get_individual_doc(program_id)
        household_doc_class = get_household_doc(program_id)
        es: Elasticsearch = connections.get_connection(using)
        for doc in (individual_doc_class, household_doc_class):
            index_name = doc._index._name
            if not es.indices.exists(index=index_name):
                return False, f"Index {index_name} does not exist."
            db_count = doc().get_queryset().count()
            es_count = es.count(index=index_name)["count"]
            if es_count != db_count:
                return False, f"Number of records does not match: index {index_name}."
        return True, "Indexes exist and counts match."
    except Exception as e:  # pragma: no cover  # noqa
        return False, str(e)
