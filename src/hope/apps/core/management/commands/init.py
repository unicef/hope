from django.core.management import BaseCommand, call_command


class Command(BaseCommand):
    def handle(self, *args: object, **options: object) -> None:
        call_command("initempty")
        call_command("generatefixtures", "--noinput")
