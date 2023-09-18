import enum
import logging
from time import sleep
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Type

from django.conf import settings
from django.db.models import Model

from django_elasticsearch_dsl.registries import registry
from elasticsearch_dsl import Search, connections
from elasticsearch import Elasticsearch, helpers

from hct_mis_api.apps.household.models import Household, Individual

logger = logging.getLogger(__name__)

DEFAULT_SCRIPT = "return (1.0/doc.length)*query.boost"


if TYPE_CHECKING:
    from django.db.models.query import QuerySet

    from django_elasticsearch_dsl import Document


def populate_index(queryset: "QuerySet", doc: Any, parallel: bool = False) -> None:
    qs = queryset.iterator()
    doc().update(qs, parallel=parallel)


def _create(models: Optional[List[Model]]) -> None:
    for index in registry.get_indices(models):
        index.create()


def _populate(models: Optional[List[Model]], options: Dict) -> None:
    parallel = options["parallel"]
    for doc in registry.get_documents(models):
        qs = doc().get_indexing_queryset()
        doc().update(qs, parallel=parallel)


def _delete(models: Optional[List[Model]]) -> bool:
    for index in registry.get_indices(models):
        index.delete(ignore=404)
    return True


def _rebuild(models: Optional[List[Model]], options: Dict) -> None:
    if not _delete(models):
        return

    _create(models)
    _populate(models, options)


def rebuild_search_index(models: Optional[List[Model]] = None, options: Optional[Dict] = None) -> None:
    if options is None:
        options = {"parallel": False, "quiet": True}
    _rebuild(models=models, options=options)


def populate_all_indexes() -> None:
    _populate(models=None, options={"parallel": False, "quiet": True})


def remove_elasticsearch_documents_by_matching_ids(id_list: List[str], document: "Type[Document]") -> None:
    query_dict = {"query": {"terms": {"_id": [str(_id) for _id in id_list]}}}
    search = Search(index=document.Index.name)
    search.update_from_dict(query_dict)
    search.delete()


class HealthStatus(enum.Enum):
    RED = "red"
    YELLOW = "yellow"
    GREEN = "green"


def wait_until_es_healthy() -> None:
    max_tries = 12
    sleep_time = 5
    # https://www.yireo.com/blog/2022-08-31-elasticsearch-cluster-is-yellow-which-is-ok
    expected_statuses = [HealthStatus.GREEN.value, HealthStatus.YELLOW.value]

    for _ in range(max_tries):
        health = connections.get_connection().cluster.health()
        ok = (
            health.get("status") in expected_statuses
            and not health.get("timed_out")
            and health.get("number_of_pending_tasks") == 0
        )
        if ok:
            break

        sleep(sleep_time)

    else:
        raise Exception(
            f"Max Check ES attempts reached - status: {health.get('status')} timeout: {health.get('timed_out')} "
            f"number of pending tasks:{health.get('number_of_pending_tasks')}"
        )


def bulk_upsert(ids: List[str], model_name: str, business_area_slug: str) -> None:
    from hct_mis_api.apps.household.documents import (
        HouseholdDocument,
        IndividualDocumentAfghanistan,
        IndividualDocumentUkraine,
        IndividualDocumentOthers
    )

    es = Elasticsearch(settings.ELASTICSEARCH_HOST)

    document = HouseholdDocument
    if model_name == "Household":
        model = Household
    else:
        if business_area_slug == "afghanistan":
            document = IndividualDocumentAfghanistan
        elif business_area_slug == "ukraine":
            document = IndividualDocumentUkraine
        else:
            document = IndividualDocumentOthers
        model = Individual

    documents_to_update = []
    for obj in model.objects.filter(id__in=ids):
        data = document().prepare(obj)
        doc = {
            "_op_type": 'update',
            "_index": document.Index.name,
            "_id": str(obj.id),
            "doc": data,
            "doc_as_upsert": True
        }
        documents_to_update.append(doc)

    try:
        helpers.bulk(es, documents_to_update)
    except Exception:
        logger.error(f"Updating {','.join([str(_id) for _id in ids])} of {document.__name__} failed")

    logger.info(f"{document.__name__} with {','.join([str(_id) for _id in ids])} have been updated.")
