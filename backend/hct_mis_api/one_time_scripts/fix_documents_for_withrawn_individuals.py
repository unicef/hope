from hct_mis_api.apps.household.models import Document


def fix_documents_for_withdrawn_individuals() -> None:
    batch_size = 500
    document_ids = (
        Document.objects.filter(individual__withdrawn=True)
        .exclude(status=Document.STATUS_INVALID)
        .values_list("id", flat=True)
    )
    document_count = document_ids.count()

    for batch_start in range(0, document_count, batch_size):
        batch_end = batch_start + batch_size
        document_ids_batch = document_ids[batch_start:batch_end]
        Document.objects.filter(id__in=document_ids_batch).update(status=Document.STATUS_INVALID)

    print(f"Updated {document_count} documents.")
