from hct_mis_api.apps.household.models import Document


def fix_documents_for_withdrawn_individuals() -> None:
    batch_size = 500
    documents = Document.objects.filter(individual__withdrawn=True).exclude(status=Document.STATUS_INVALID)
    documents_count = documents.count()

    for batch_start in range(0, documents_count, batch_size):
        batch_end = batch_start + batch_size
        documents[batch_start:batch_end].update(status=Document.STATUS_INVALID)

    print(f"Updated {documents_count} documents.")
