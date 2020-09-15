from django.core.management import call_command


def rebuild_search_index():
    call_command("search_index", "--rebuild", "-f", "--parallel")


def populate_all_indexes():
    call_command("search_index", "--populate", "--parallel")
