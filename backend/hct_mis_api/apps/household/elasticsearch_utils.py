from django.core.management import CommandError
from django_elasticsearch_dsl.registries import registry


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
                elif '{}.{}'.format(
                    model._meta.app_label.lower(),
                    model._meta.model_name.lower()
                ) == arg:
                    models.append(model)
                    match_found = True

            if not match_found:
                raise CommandError("No model or app named {}".format(arg))
    else:
        models = registry.get_models()

    return set(models)


def _create(models, options):
    for index in registry.get_indices(models):
        index.create()


def _populate(models, options):
    parallel = options['parallel']
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


def rebuild_search_index(models=None, options=None):
    if options is None:
        options = {"parallel": False, "quiet": True}
    _rebuild(models=models, options=options)


def populate_all_indexes():
    _populate(models=None, options={"parallel": False, "quiet": True})

