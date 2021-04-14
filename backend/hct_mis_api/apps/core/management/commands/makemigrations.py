from django.core.management.commands import makemigrations


class Command(makemigrations.Command):
    def handle(self, *args, **options):
        self.stdout.write(
            self.style.WARNING(
                'This is the overridden command which creates migrations with the name "_migration" '
                "by which we can catch conflicts at a Pull Request level"
            )
        )
        options["name"] = "migration"
        super().handle(*args, **options)
