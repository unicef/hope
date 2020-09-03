from django.core.management import call_command


def rebuild_search_index():
    call_command("search_index", "--rebuild", "-f")
