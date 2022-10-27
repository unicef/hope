import logging

from django.core.management import CommandError

from django_elasticsearch_dsl.registries import registry
from elasticsearch_dsl import Search

logger = logging.getLogger(__name__)

# DEFAULT_SCRIPT = (
#     "double tf = Math.sqrt(doc.freq); double idf = 1.0; double norm = 1/"
#     "Math.sqrt(doc.length); return query.boost * tf * idf * norm;"
# )
DEFAULT_SCRIPT = "return (1.0/doc.length)*query.boost"


def populate_index(queryset, doc, parallel=False):
    qs = queryset.iterator()
    doc().update(qs, parallel=parallel)


def _get_models(args):
    if args:
        models = []
        for arg in args:
            arg = arg.lower()
            match_found = False

            for model in registry.get_models():
                if model._meta.app_label == arg:
                    models.append(model)
                    match_found = True
                elif f"{model._meta.app_label.lower()}.{model._meta.model_name.lower()}" == arg:
                    models.append(model)
                    match_found = True

            if not match_found:
                logger.error(f"No model or app named {arg}")
                raise CommandError(f"No model or app named {arg}")
    else:
        models = registry.get_models()

    return set(models)


def _create(models, options):
    for index in registry.get_indices(models):
        index.create()


def _populate(models, options):
    parallel = options["parallel"]
    for doc in registry.get_documents(models):
        qs = doc().get_indexing_queryset()
        doc().update(qs, parallel=parallel)


def _delete(models, options):
    for index in registry.get_indices(models):
        index.delete(ignore=404)
    return True


def _rebuild(models, options):
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


def remove_document_by_matching_ids(id_list, document):
    query_dict = {"query": {"terms": {"id": id_list}}}
    search = Search(index="individuals")
    search.update_from_dict(query_dict)
    search.delete()


def remove_elasticsearch_documents_by_matching_ids(id_list, document):
    query_dict = {"query": {"terms": {"id": id_list}}}
    search = Search(index=document.Index.name)
    search.update_from_dict(query_dict)
    search.delete()
