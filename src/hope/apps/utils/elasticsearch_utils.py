import enum
import logging
from typing import TYPE_CHECKING, Any

from django.db.models import Model
from django_elasticsearch_dsl.registries import registry
from elasticsearch_dsl import connections

logger = logging.getLogger(__name__)

DEFAULT_SCRIPT = "return (1.0/doc.length)*query.boost"


if TYPE_CHECKING:
    from django.db.models.query import QuerySet
    from django_elasticsearch_dsl import Document


def populate_index(queryset: "QuerySet", doc: Any, parallel: bool = False, chunk_size: int = 2000) -> None:
    qs = queryset.iterator(chunk_size=chunk_size)
    doc().update(qs, parallel=parallel)


def _create(models: list[Model] | None) -> None:
    import elasticsearch

    for index in registry.get_indices(models):
        logger.info(f"Creating index {index._name}")
        try:
            index.create()
        except elasticsearch.exceptions.RequestError:  # pragma: no cover
            logger.exception(f"Failed to create index {index._name}")


def _populate(models: list[Any] | None, options: dict) -> None:
    parallel = options["parallel"]
    for doc in registry.get_documents(models):
        qs = doc().get_indexing_queryset()
        doc().update(qs, parallel=parallel)


def _delete(models: list[Model] | None) -> bool:
    for index in registry.get_indices(models):
        index.delete(ignore=404)
    return True


def _rebuild(models: list[Model] | None, options: dict) -> None:
    if not _delete(models):
        return

    _create(models)
    _populate(models, options)


def rebuild_search_index(models: list[Model] | None = None, options: dict | None = None) -> None:
    if options is None:
        options = {"parallel": False, "quiet": True}
    _rebuild(models=models, options=options)


def populate_all_indexes() -> None:
    _populate(models=None, options={"parallel": False, "quiet": True})


def delete_all_indexes() -> None:
    _delete(models=None)


def remove_elasticsearch_documents_by_matching_ids(id_list: list[str], document: "type[Document]") -> None:
    query_dict = {"query": {"terms": {"_id": [str(_id) for _id in id_list]}}}
    document.search().params(search_type="dfs_query_then_fetch").update_from_dict(query_dict).delete()


class HealthStatus(enum.Enum):
    RED = "red"
    YELLOW = "yellow"
    GREEN = "green"


def ensure_index_ready(index_name: str) -> None:
    """Check ES is not RED and refresh index to ensure documents are searchable."""
    conn = connections.get_connection()
    health = conn.cluster.health()

    if health.get("status") == HealthStatus.RED.value:
        raise Exception("ES cluster is RED - cannot proceed")

    conn.indices.refresh(index=index_name)
