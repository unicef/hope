from django.core.management import call_command


def rebuild_search_index():
    call_command("search_index", "--rebuild", "-f")


def populate_all_indexes():
    call_command("search_index", "--populate")


def populate_index(queryset, doc, parallel=False):
    print(f"Indexing {queryset.count()} {doc}...")
    qs = queryset.iterator()
    doc().update(qs, parallel=parallel)
    print("Done.")
