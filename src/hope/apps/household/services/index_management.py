"""Elasticsearch Index Management for Per-Program Indexes.

Simple utilities for managing per-program Elasticsearch indexes.
"""

import logging
import re

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


def versioned_doc(doc_class: type, suffix: str) -> type:
    """Subclass a per-program Document so every read/write targets ``<name>_<suffix>``.

    Blue-green needs to populate/delta a DARK ``_vN`` physical index while the alias (the
    suffix-less name every doc class addresses) still points at the old version. All ES
    consumption goes through the class's ``_index``/``Index.name``, so one subclass with a
    suffixed name redirects bulk writes, deletes-by-id and searches alike.
    """

    class VersionedDoc(doc_class):
        class Index(doc_class.Index):  # type: ignore[name-defined]
            name = f"{doc_class.Index.name}_{suffix}"

    VersionedDoc.__name__ = f"{doc_class.__name__}_{suffix}"
    return VersionedDoc


def existing_version_numbers(es: Elasticsearch, name: str) -> list[int]:
    """Numbers N of all physical ``<name>_vN`` indexes present in ES."""
    existing = es.indices.get(index=f"{name}_v*", ignore_unavailable=True)
    return [int(m.group(1)) for i in existing for m in [re.match(rf"^{re.escape(name)}_v(\d+)$", i)] if m]


def next_version_suffix(es: Elasticsearch, doc_classes: list) -> str:
    """Next unused ``vN`` across ALL given docs' versions.

    Taking the max over the whole set keeps a program's individuals/households pair in
    lockstep: both dark indexes get the SAME suffix, so a single delta ``--target-suffix``
    pass covers the pair even if their version histories diverged.
    """
    versions = [n for doc_class in doc_classes for n in existing_version_numbers(es, doc_class._index._name)]
    return f"v{max(versions, default=0) + 1}"


def create_versioned_index(
    es: Elasticsearch, doc_class: type, suffix: str | None = None, attach_alias: bool = True
) -> str:
    """Create ``<name>_<suffix>`` from the doc class's code mapping and return its name.

    Blue-green convention: the app addresses the suffix-less name, which is an ALIAS onto the
    physical ``_vN``. With ``attach_alias`` (new/rebuilt programs) index and alias are born in
    one call — there is never a bare physical index squatting on the logical name. Without it
    (reindex) the index is created DARK: the alias stays on the old version until the swap.
    Default ``suffix`` is ``max(existing) + 1`` rather than a hardcoded ``_v1`` so a rebuild
    during a blue-green sanity window (old ``_vN`` still lingering unaliased) cannot collide
    and strand the program without an index.
    """
    index = doc_class._index
    name = index._name
    if suffix is None:
        suffix = f"v{max(existing_version_numbers(es, name), default=0) + 1}"
    target = f"{name}_{suffix}"
    body = index.to_dict()
    es.indices.create(
        index=target,
        settings=body.get("settings"),
        mappings=body.get("mappings"),
        aliases={name: {}} if attach_alias else None,
    )
    return target


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
    if not success:
        return False, f"Create failed: {msg}"

    success, msg = populate_program_indexes(
        program_id, batch_size, parallel=parallel, thread_count=thread_count, using=using
    )
    if not success:
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
