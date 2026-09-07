from collections.abc import Callable
import enum
import logging
from typing import TYPE_CHECKING, Any

from constance import config
from django.db import transaction
from elasticsearch import NotFoundError
from elasticsearch.dsl import connections

logger = logging.getLogger(__name__)

DEFAULT_SCRIPT = "return (1.0/doc.length)*query.boost"


if TYPE_CHECKING:
    from django.db.models.query import QuerySet
    from django_elasticsearch_dsl import Document


PROGRESS_EVERY = 1_000


def populate_index(
    queryset: "QuerySet",
    doc: Any,
    parallel: bool = False,
    chunk_size: int = 2000,
    progress_cb: Callable[[int], None] | None = None,
) -> None:
    if not config.IS_ELASTICSEARCH_ENABLED:
        return
    # atomic() so iterator() opens a plain (lazy) server-side cursor: outside a transaction
    # Django declares it WITH HOLD, which materializes the ENTIRE result set on DECLARE
    # before the first row arrives - minutes-to-hours on big programs under IO pressure
    with transaction.atomic():
        # cursors are planned for partial reads (cursor_tuple_fraction=0.1) -> plain index
        # scan -> one RANDOM heap page read per row on a big scattered table. We always read
        # the FULL result, and saying so buys a bitmap heap scan (sequential, prefetched):
        # measured 7x faster chunk fetches on remote disks. SET LOCAL dies with this txn.
        with transaction.get_connection().cursor() as c:
            c.execute("SET LOCAL cursor_tuple_fraction = 1.0")
        qs: Any = queryset.iterator(chunk_size=chunk_size)
        if progress_cb is not None:
            qs = _reporting(qs, progress_cb)
        doc().update(qs, parallel=parallel)


def _reporting(rows: Any, cb: Callable[[int], None]) -> Any:
    n = 0
    for row in rows:
        yield row
        n += 1
        if n % PROGRESS_EVERY == 0:
            cb(n)
    cb(n)


def remove_elasticsearch_documents_by_matching_ids(
    id_list: list[str], document: "type[Document]", using: str | None = None
) -> None:
    if not config.IS_ELASTICSEARCH_ENABLED or not id_list:
        return
    try:
        query_dict = {"query": {"terms": {"_id": [str(_id) for _id in id_list]}}}
        document.search(using=using).params(search_type="dfs_query_then_fetch", conflicts="proceed").update_from_dict(
            query_dict
        ).delete()
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
    # DESTRUCTIVE (delete -> create -> populate) on purpose, like the per-program admin
    # "Rebuild Index" button: it must also recover from a junk index auto-created by a doc
    # write that raced index creation (dynamic mapping, no analyzers). Explicit console/dev
    # entrypoints only - AUTOMATIC paths (signals) use ensure_program_indexes instead.
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
