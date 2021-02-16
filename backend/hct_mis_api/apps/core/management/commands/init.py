from django.core.management import call_command, BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **options):
        call_command("initempty")
        call_command("generatefixtures", "--noinput", flush=False)
