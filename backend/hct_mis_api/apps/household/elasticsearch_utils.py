import logging

from django_elasticsearch_dsl.registries import registry
from elasticsearch_dsl import Search

logger = logging.getLogger(__name__)

DEFAULT_SCRIPT = "return (1.0/doc.length)*query.boost"


def populate_index(queryset, doc, parallel=False) -> None:
    qs = queryset.iterator()
    doc().update(qs, parallel=parallel)


def _create(models, options) -> None:
    for index in registry.get_indices(models):
        index.create()


def _populate(models, options) -> None:
    parallel = options["parallel"]
    for doc in registry.get_documents(models):
        qs = doc().get_indexing_queryset()
        doc().update(qs, parallel=parallel)


def _delete(models, options) -> bool:
    for index in registry.get_indices(models):
        index.delete(ignore=404)
    return True


def _rebuild(models, options) -> None:
    if not _delete(models, options):
        return

    _create(models, options)
    _populate(models, options)


def rebuild_search_index(models=None, options=None) -> None:
    if options is None:
        options = {"parallel": False, "quiet": True}
    _rebuild(models=models, options=options)


def populate_all_indexes():
    _populate(models=None, options={"parallel": False, "quiet": True})


def remove_document_by_matching_ids(id_list, document) -> None:
    query_dict = {"query": {"terms": {"id": id_list}}}
    search = Search(index="individuals")
    search.update_from_dict(query_dict)
    search.delete()


def remove_elasticsearch_documents_by_matching_ids(id_list, document) -> None:
    query_dict = {"query": {"terms": {"id": id_list}}}
    search = Search(index=document.Index.name)
    search.update_from_dict(query_dict)
    search.delete()
