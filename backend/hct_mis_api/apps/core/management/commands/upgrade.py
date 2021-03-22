from django.core.management import call_command, BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **options):
        call_command("collectstatic", interactive=False)
        call_command("migratealldb")
        call_command("search_index", "--rebuild", "-f")
        call_command("generateroles")
