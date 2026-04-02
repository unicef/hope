import enum
import logging
from typing import TYPE_CHECKING, Any

from constance import config
from elasticsearch import NotFoundError
from elasticsearch_dsl import connections

logger = logging.getLogger(__name__)

DEFAULT_SCRIPT = "return (1.0/doc.length)*query.boost"


if TYPE_CHECKING:
    from django.db.models.query import QuerySet
    from django_elasticsearch_dsl import Document


def populate_index(queryset: "QuerySet", doc: Any, parallel: bool = False, chunk_size: int = 2000) -> None:
    if not config.IS_ELASTICSEARCH_ENABLED:  # pragma: no cover
        return
    qs = queryset.iterator(chunk_size=chunk_size)
    doc().update(qs, parallel=parallel)


def remove_elasticsearch_documents_by_matching_ids(id_list: list[str], document: "type[Document]") -> None:
    if not config.IS_ELASTICSEARCH_ENABLED or not id_list:
        return
    try:
        query_dict = {"query": {"terms": {"_id": [str(_id) for _id in id_list]}}}
        document.search().params(search_type="dfs_query_then_fetch").update_from_dict(query_dict).delete()
    except NotFoundError:
        pass


class HealthStatus(enum.Enum):
    RED = "red"
    YELLOW = "yellow"
    GREEN = "green"


def ensure_index_ready(index_name: str) -> None:
    """Check ES is not RED and refresh index to ensure documents are searchable."""
    if not config.IS_ELASTICSEARCH_ENABLED:  # pragma: no cover
        raise Exception("Elasticsearch is disabled - cannot proceed")

    conn = connections.get_connection()
    health = conn.cluster.health()

    if health.get("status") == HealthStatus.RED.value:
        raise Exception("ES cluster is RED - cannot proceed")

    conn.indices.refresh(index=index_name)


def rebuild_search_index(models: None = None, options: dict | None = None) -> None:
    from hope.apps.household.services.index_management import rebuild_program_indexes
    from hope.models import Program

    if not config.IS_ELASTICSEARCH_ENABLED:  # pragma: no cover
        return

    for program in Program.objects.filter(status=Program.ACTIVE):
        rebuild_program_indexes(str(program.id))


def populate_all_indexes() -> None:
    """Populate Elasticsearch indexes - for all active programs."""
    from hope.apps.household.services.index_management import populate_program_indexes
    from hope.models import Program

    if not config.IS_ELASTICSEARCH_ENABLED:  # pragma: no cover
        return

    for program in Program.objects.filter(status=Program.ACTIVE):
        populate_program_indexes(str(program.id))


def delete_all_indexes() -> None:
    """Delete Elasticsearch indexes - for all active programs."""
    from hope.apps.household.services.index_management import delete_program_indexes
    from hope.models import Program

    if not config.IS_ELASTICSEARCH_ENABLED:  # pragma: no cover
        return

    for program in Program.objects.filter(status=Program.ACTIVE):
        delete_program_indexes(str(program.id))
