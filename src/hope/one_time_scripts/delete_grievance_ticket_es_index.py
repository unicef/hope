"""
Delete the orphaned grievance_tickets Elasticsearch index.

Run from Django shell:
    from hope.one_time_scripts.delete_grievance_ticket_es_index import delete_grievance_ticket_es_index
    delete_grievance_ticket_es_index()
"""
from django.conf import settings
from elasticsearch import Elasticsearch

from hope.apps.household.services.index_management import delete_es_index

GRIEVANCE_INDEX_NAME = "grievance_tickets"


def delete_grievance_ticket_es_index() -> None:
    es = Elasticsearch(settings.ELASTICSEARCH_HOST)
    prefix = settings.ELASTICSEARCH_INDEX_PREFIX
    index = f"{prefix}{GRIEVANCE_INDEX_NAME}"

    if not es.indices.exists(index=index):
        print(f"Index {index} does not exist, nothing to do.")
        return

    delete_es_index(es, index)
    print(f"Deleted index: {index}")
