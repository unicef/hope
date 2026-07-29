from django.core.management import BaseCommand, call_command


class Command(BaseCommand):
    def handle(self, *args: object, **options: object) -> None:
        call_command("migrate")
        call_command("collectstatic", "--no-default-ignore", interactive=False)
        from adminactions.perms import create_extra_permissions

        create_extra_permissions()
