from django.core.management import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    def handle(self, *args, **options):
        # Ideally, this command should initialize the app
        # with root:root1234 user
        # and allow to visit the dashboard without any errors

        # For now:
        call_command("initdemo")
